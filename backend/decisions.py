"""Additive decision guidance from measured results; no link fetching or storage."""
import math
from urllib.parse import urlsplit
import pandas as pd


def preview(frame):
    def cell(value):
        if value is None or pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return value if math.isfinite(value) else None
        return str(value)[:160]
    return {'columns': list(frame.columns), 'rows': [{key: cell(value) for key, value in row.items()} for row in frame.head(5).to_dict('records')], 'total_rows': len(frame)}


def post_references(frame, warnings):
    pairs = []
    seen_pairs = set()
    unsafe = False
    for row in frame.to_dict('records'):
        raw_id, raw_url = row.get('post_id'), row.get('post_url')
        post_id = str(raw_id).strip() if raw_id is not None and not pd.isna(raw_id) else None
        post_id = post_id or None
        url = str(raw_url).strip() if raw_url is not None and not pd.isna(raw_url) else None
        if url:
            try:
                parsed = urlsplit(url)
                valid = parsed.scheme.lower() in ('http', 'https') and bool(parsed.hostname) and parsed.username is None and parsed.password is None and not any(c.isspace() or ord(c) < 32 for c in url) and '\\' not in url
                parsed.port  # Reject malformed port numbers too.
            except ValueError:
                valid = False
            if not valid:
                unsafe = True
                url = None
        if post_id or url:
            pair = (post_id, url)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                pairs.append(pair)
    id_urls, url_ids = {}, {}
    for post_id, url in pairs:
        if post_id and url:
            id_urls.setdefault(post_id, set()).add(url)
            url_ids.setdefault(url, set()).add(post_id)
    ambiguous = {post_id for post_id, urls in id_urls.items() if len(urls) > 1}
    ambiguous_urls = {url for url, ids in url_ids.items() if len(ids) > 1}
    refs = []
    seen_refs = set()
    for post_id, url in pairs:
        if post_id in ambiguous or url in ambiguous_urls:
            url = None
        ref = {'post_id': post_id, 'post_url': url}
        ref_key = (post_id, url)
        if ref_key not in seen_refs:
            seen_refs.add(ref_key)
            refs.append(ref)
    if unsafe:
        warnings.append('Unsafe or invalid post links were omitted. Use absolute HTTP(S) links without credentials.')
    if ambiguous or ambiguous_urls:
        warnings.append('Ambiguous post ID and link associations were omitted; confirm one link per post ID.')
    if len(refs) > 365:
        warnings.append('Post references limited to the first 365 distinct usable references.')
    return refs[:365]


def add_decision_fields(result, frame, period_summary):
    result['preview'] = preview(frame)
    result['post_references'] = post_references(frame, result['warnings'])
    totals, demand = result['totals'], result['demand']
    stages = []
    for key in ('views', 'saves', 'questions', 'sales'):
        value = demand.get('inquiries') if key == 'questions' else totals.get(key)
        note = ('Text rows with question signals; not unique buyers.' if key == 'questions' else 'Sum of known counts; missing counts are excluded.') if value is not None else 'Not supplied or no usable values.'
        stages.append({'key': key, 'label': key.title(), 'value': value, 'note': note})
    result['funnel'] = {'stages': stages, 'note': 'These are independent counts, not a tracked customer journey. They do not show which people moved between steps or which views led to sales.'}
    for item in result['recommend']:
        kind = item.get('experiment_kind')
        if kind == 'sales':
            measure = 'Compare sales and views before and after the test. Keep audience size and time windows similar. This does not track which views led to sales.'
        elif kind == 'questions':
            measure = 'Compare recurring question rows before and after the FAQ with comparable exposure and the same text collection method; review intent manually.'
        elif kind == 'relationship':
            measure = 'Compare the two measured counts across comparable entries and exposure before and after one change; a pattern does not show causation.'
        else:
            measure = 'Collect complete dated counts across comparable exposure and two full weeks before comparing results.'
        item['success_metric'] = measure
        if item.get('post_id'):
            post_id = item['post_id']
            urls = {r['post_url'] for r in result['post_references'] if r['post_id'] == post_id and r['post_url']}
            if len(urls) == 1:
                item['post_url'] = next(iter(urls))
    period = next(((metric, result['periods'][metric]) for metric in ('sales', 'views', 'saves', 'likes', 'comments') if result['periods'].get(metric, {}).get('available')), None)
    changed = period_summary(*period) if period else (('Observed totals: ' + ', '.join(f'{value:,.0f} {metric}' for metric, value in totals.items()) + '.') if totals else f"The dataset contains {result['rows']:,} text entries.") + ' Weekly change needs dated complete data for two full weeks.'
    first = result['recommend'][0]
    result['decision_brief'] = {'changed': changed, 'matters': first['evidence'] + ' Observed patterns do not establish cause and effect.', 'try_next': first['action'], 'measure': first['success_metric']}


def decision_answer(question, result):
    import re
    q = question.lower()
    if re.search(r'brief|what changed|why.*matter', q) and result.get('decision_brief'):
        return '\n'.join(result['decision_brief'].values())
    if re.search(r'funnel|customer journey|drop.off', q) and result.get('funnel'):
        return '; '.join(f"{stage['label']}: {stage['value'] if stage['value'] is not None else 'not supplied'}. {stage['note']}" for stage in result['funnel']['stages']) + ' ' + result['funnel']['note']
    if re.search(r'measur|success|experiment', q) and result.get('decision_brief'):
        return result['decision_brief']['measure']
    return None


def decision_report(result):
    if not result.get('decision_brief'):
        return ''
    brief = result['decision_brief']
    return '\n\n## Decision brief\n\n' + '\n\n'.join(f"{label}: {brief[key]}" for label, key in [('Changed', 'changed'), ('Why it matters', 'matters'), ('Try next', 'try_next'), ('How to measure', 'measure')]) + '\n\n## Independent counts\n\n' + decision_answer('funnel', result) + '\n\n## Experiments\n\n' + '\n\n'.join(f"{item['title']}. {item['evidence']} {item['action']} How to measure: {item['success_metric']}" for item in result['recommend'])
