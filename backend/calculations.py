"""Stateless calculations over validated count metrics and UTC date labels."""

import math
from datetime import timedelta
from itertools import combinations

import pandas as pd
from scipy.stats import pearsonr, spearmanr


METRICS = ('views', 'likes', 'saves', 'comments', 'sales')


def calculate_correlations(df: pd.DataFrame) -> list[dict]:
    """Compare identical complete pairs; p-values assume independent observations."""
    result = []
    metrics = [metric for metric in METRICS if metric in df]
    for a, b in combinations(metrics, 2):
        pairs = df[[a, b]].dropna()
        if len(pairs) < 3 or pairs[a].nunique() < 2 or pairs[b].nunique() < 2:
            continue
        if not all(math.isfinite(value) for value in pairs.to_numpy().flat):
            continue
        r, p = pearsonr(pairs[a], pairs[b])
        rho, rho_p = spearmanr(pairs[a], pairs[b])
        if not all(math.isfinite(value) for value in (r, p, rho, rho_p)):
            continue
        result.append({'a': a, 'b': b, 'r': round(float(r), 4), 'p': float(p),
                       'n': len(pairs), 'spearman_r': float(rho),
                       'spearman_p': float(rho_p), 'small_sample': len(pairs) < 10})
    result.sort(key=lambda row: (-abs(row['r']), row['a'], row['b']))
    return result


def _finite(value):
    return float(value) if math.isfinite(value) else None


def _total(values):
    try:
        return _finite(math.fsum(float(value) for value in values))
    except OverflowError:
        return None


def calculate_ratios(df: pd.DataFrame) -> dict:
    """Return percentages of paired sums, including known zero-view rows."""
    result = {}
    for metric in ('sales', 'saves'):
        item = {
            'available': False, 'reason': None,
            'numerator_metric': metric, 'denominator_metric': 'views',
            'numerator': None, 'denominator': None, 'percent': None,
            'n': 0, 'excluded_rows': len(df), 'zero_view_rows': 0,
            'notes': ['Ratios are proxies, not attributed conversion.'],
        }
        result[f'{metric}_per_view'] = item
        if metric not in df or 'views' not in df:
            item['reason'] = f'Need both {metric} and views columns.'
            continue
        pairs = df[[metric, 'views']].dropna()
        item['n'] = len(pairs)
        item['excluded_rows'] = len(df) - len(pairs)
        item['zero_view_rows'] = int(pairs['views'].eq(0).sum())
        if pairs.empty:
            item['reason'] = 'No complete metric/view pairs.'
            continue
        numerator = item['numerator'] = _total(pairs[metric])
        denominator = item['denominator'] = _total(pairs['views'])
        if item['zero_view_rows']:
            item['notes'].append(f"Included {item['zero_view_rows']} zero-view rows in paired sums.")
        if numerator is None or denominator is None:
            item['reason'] = 'Paired sums exceed finite numeric range.'
            continue
        if denominator == 0:
            item['reason'] = 'Summed paired views are zero.'
            continue
        percent = _finite(numerator / denominator * 100)
        if percent is None:
            item['reason'] = 'Ratio exceeds finite numeric range.'
            continue
        item.update(available=True, percent=percent)
        if percent > 100:
            item['notes'].append('Ratio exceeds 100%; measurement scopes may be inconsistent.')
    return result


def rank_performance(df: pd.DataFrame) -> dict:
    """Rank paired rates using exposure heuristics, not significance guarantees."""
    result = {}
    for name, column in (('categories', 'category'), ('posts', 'post_id')):
        rankings = result[name] = {}
        labels = df[column].astype('string').str.strip() if column in df else None
        named = labels.notna() & labels.ne('') if labels is not None else None
        duplicates = (name == 'posts' and labels is not None
                      and labels[named].duplicated().any())
        for metric in ('sales', 'saves'):
            item = {'available': False, 'reason': None, 'rows': [], 'excluded_groups': 0}
            rankings[f'{metric}_per_view'] = item
            if labels is None:
                item['reason'] = f'Need {column} column for ranking.'
                continue
            if duplicates:
                item['reason'] = 'Repeated post IDs make snapshots versus increments ambiguous.'
                continue
            if metric not in df or 'views' not in df:
                item['reason'] = f'Need both {metric} and views columns.'
                continue
            groups = df.loc[named, [metric, 'views']].assign(label=labels[named])
            for label, group in groups.groupby('label', sort=False):
                pairs = group[[metric, 'views']].dropna()
                pairs = pairs.loc[pairs['views'].gt(0)]
                numerator = _total(pairs[metric])
                views = _total(pairs['views'])
                minimum_rows, minimum_views = (3, 1000) if name == 'categories' else (1, 100)
                if (len(pairs) < minimum_rows or numerator is None or views is None
                        or views < minimum_views):
                    item['excluded_groups'] += 1
                    continue
                percent = _finite(numerator / views * 100)
                if percent is None:
                    item['excluded_groups'] += 1
                    continue
                item['rows'].append({'label': label, 'numerator': numerator,
                                     'views': views, 'percent': percent, 'n': len(pairs)})
            item['rows'].sort(key=lambda row: (-row['percent'], row['label']))
            item['rows'] = item['rows'][:10]
            if item['rows']:
                item['available'] = True
            else:
                item['reason'] = 'No named groups meet complete-pair and exposure requirements.'
    return result


def compare_periods(df: pd.DataFrame) -> dict:
    """Compare the latest seven UTC calendar dates with the prior seven."""
    if 'date' not in df:
        return {}
    metrics = [metric for metric in METRICS if metric in df]
    if not metrics:
        return {}
    dates = pd.to_datetime(df['date'], format='%Y-%m-%d', utc=True, errors='coerce')
    latest = dates.max()
    boundaries = dict.fromkeys(('current_start', 'current_end', 'previous_start', 'previous_end'))
    if pd.notna(latest):
        latest = latest.to_pydatetime()
        current_start = latest - timedelta(days=6)
        previous_start = latest - timedelta(days=13)
        previous_end = latest - timedelta(days=7)
        boundaries = {key: value.strftime('%Y-%m-%d') for key, value in (
            ('current_start', current_start), ('current_end', latest),
            ('previous_start', previous_start), ('previous_end', previous_end),
        )}
    result = {}
    for metric in metrics:
        item = {
            'available': False, 'reason': None, **boundaries,
            'current_total': None, 'previous_total': None,
            'absolute_change': None, 'percent_change': None,
            'percent_change_reason': None,
        }
        result[metric] = item
        if dates.isna().any() or pd.isna(latest):
            item['reason'] = 'Invalid or missing dates make period membership unknown.'
            continue
        window = dates.between(previous_start, latest)
        if dates[window].nunique() != 14:
            item['reason'] = 'Need all 14 calendar dates; missing dates are not zero activity.'
            continue
        if df.loc[window, metric].isna().any():
            item['reason'] = f'Missing {metric} values within the comparison windows.'
            continue
        current = _total(df.loc[dates.between(current_start, latest), metric])
        previous = _total(df.loc[dates.between(previous_start, previous_end), metric])
        if current is None or previous is None:
            item['reason'] = 'Period totals exceed finite numeric range.'
            continue
        item.update(available=True, current_total=current, previous_total=previous,
                    absolute_change=_finite(current - previous))
        if previous == 0:
            item['percent_change_reason'] = 'Previous total is zero; percentage change is undefined.'
        else:
            item['percent_change'] = _finite((current - previous) / previous * 100)
            if item['percent_change'] is None:
                item['percent_change_reason'] = 'Percentage change exceeds finite numeric range.'
    return result
