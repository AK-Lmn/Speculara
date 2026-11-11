"""Daily baseline comparison on a shared, untouched three-date holdout."""
from datetime import timedelta

import numpy as np
import pandas as pd
from scipy.stats import linregress


PRIORITY = ('sales', 'views', 'saves', 'likes', 'comments')


def _linear(y, positions):
    # Constant inputs need no regression; this also avoids scipy precision warnings.
    if np.all(y == y[0]):
        return np.full(len(positions), y[0], dtype=float)
    fit = linregress(np.arange(len(y)), y)
    return np.maximum(0, fit.intercept + fit.slope * positions)


def forecast_daily(df: pd.DataFrame) -> dict:
    """Compare baselines without leakage, then refit the winner on all days."""
    unavailable = {'available': False, 'reason': 'Need a complete daily series with 14 to 365 consecutive dates and a numeric metric.'}
    target = next((metric for metric in PRIORITY if metric in df and df[metric].notna().any()), None)
    if 'date' not in df or target is None or df[target].isna().any():
        return unavailable
    dates = pd.to_datetime(df['date'], errors='coerce', utc=True, format='mixed')
    if dates.isna().any():
        return unavailable
    daily = df[target].groupby(dates.dt.strftime('%Y-%m-%d'), sort=True).sum(min_count=1)
    if not 14 <= len(daily) <= 365:
        return unavailable
    first = dates.min().to_pydatetime().date()
    last = dates.max().to_pydatetime().date()
    if (last - first).days != len(daily) - 1:
        return unavailable
    y = daily.to_numpy(dtype=float)
    train = y[:-3]
    linear = _linear(train, np.arange(len(train), len(y)))
    scores = {'linear': float(np.mean(np.abs(linear - y[-3:]))),
              'last_value': float(np.mean(np.abs(train[-1] - y[-3:])))}
    selected = 'linear' if scores['linear'] < scores['last_value'] else 'last_value'
    projected = (_linear(y, np.arange(len(y), len(y) + 7)) if selected == 'linear'
                 else np.full(7, y[-1], dtype=float))
    method = ('Daily linear trend, clipped at zero.' if selected == 'linear'
              else 'Daily last-observed-value baseline.')
    return {'available': True, 'reason': None, 'metric': target,
            'method': method + ' No seasonality or causal model.',
            'selected_model': selected, 'mae': round(scores[selected], 3),
            'training_days': len(y),
            'evaluation': {'holdout_dates': list(daily.index[-3:]), 'train_days': len(train),
                           'scores': {name: round(score, 3) for name, score in scores.items()}},
            'notes': ['One small three-date holdout comparison; not validated generalization performance.',
                      'Seasonality and uncertainty are unsupported; no confidence band or accuracy percentage.'],
            'points': [{'label': (last + timedelta(days=i + 1)).isoformat(), 'value': round(float(value), 3)}
                       for i, value in enumerate(projected)]}
