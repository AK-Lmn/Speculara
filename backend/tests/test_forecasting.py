import unittest

import pandas as pd

from backend.forecasting import forecast_daily


class ForecastTests(unittest.TestCase):
    def frame(self, values):
        return pd.DataFrame({'date': pd.date_range('2026-01-01', periods=len(values)).strftime('%Y-%m-%d'), 'sales': values})

    def test_linear_holdout_and_refit(self):
        result = forecast_daily(self.frame(range(1, 15)))
        self.assertTrue(result['available'])
        self.assertIsNone(result['reason'])
        self.assertEqual(result['selected_model'], 'linear')
        self.assertEqual(result['evaluation'], {'holdout_dates': ['2026-01-12', '2026-01-13', '2026-01-14'], 'train_days': 11, 'scores': {'linear': 0, 'last_value': 2}})
        self.assertEqual(result['mae'], 0)
        self.assertEqual(result['training_days'], 14)
        self.assertEqual(result['points'], [{'label': f'2026-01-{day:02}', 'value': day} for day in range(15, 22)])
        self.assertIn('holdout', ' '.join(result['notes']).lower())
        self.assertIn('uncertainty', ' '.join(result['notes']).lower())

    def test_constant_tie_prefers_last_value(self):
        result = forecast_daily(self.frame([5] * 14))
        self.assertEqual(result['selected_model'], 'last_value')
        self.assertEqual(result['evaluation']['scores'], {'linear': 0, 'last_value': 0})
        self.assertEqual([p['value'] for p in result['points']], [5] * 7)

    def test_holdout_never_used_for_fit(self):
        result = forecast_daily(self.frame([10] * 11 + [0] * 3))
        self.assertEqual(result['evaluation']['scores'], {'linear': 10, 'last_value': 10})
        self.assertEqual(result['selected_model'], 'last_value')
        self.assertEqual(result['training_days'], 14)
        self.assertEqual(result['evaluation']['train_days'], 11)
        self.assertEqual([p['value'] for p in result['points']], [0] * 7)

    def test_descending_linear_clips_zero(self):
        result = forecast_daily(self.frame(range(14, 0, -1)))
        self.assertEqual(result['selected_model'], 'linear')
        self.assertEqual([p['value'] for p in result['points']], [0] * 7)

    def test_ineligible_daily_series(self):
        gap = self.frame(range(15)).drop(index=3)
        invalid = self.frame(range(14))
        invalid.loc[0, 'date'] = 'invalid'
        missing = self.frame(range(14))
        missing.loc[0, 'sales'] = None
        for frame in (self.frame(range(13)), self.frame(range(366)), gap, invalid, missing, pd.DataFrame({'sales': [1]})):
            with self.subTest(rows=len(frame)):
                result = forecast_daily(frame)
                self.assertFalse(result['available'])
                self.assertTrue(result['reason'])
                self.assertNotIn('evaluation', result)
                self.assertNotIn('points', result)

    def test_order_and_metric_priority(self):
        frame = self.frame(range(1, 15))
        frame['views'] = 100
        self.assertEqual(forecast_daily(frame), forecast_daily(frame.sample(frac=1, random_state=7)))
        self.assertEqual(forecast_daily(frame)['metric'], 'sales')
        frame['sales'] = None
        self.assertEqual(forecast_daily(frame)['metric'], 'views')

    def test_selection_uses_unrounded_scores(self):
        result = forecast_daily(self.frame([i / 10000 for i in range(1, 15)]))
        self.assertEqual(result['evaluation']['scores'], {'linear': 0, 'last_value': 0})
        self.assertEqual(result['selected_model'], 'linear')

    def test_maximum_eligible_length(self):
        result = forecast_daily(self.frame([5] * 365))
        self.assertTrue(result['available'])
        self.assertEqual(result['training_days'], 365)
        self.assertEqual(result['evaluation']['train_days'], 362)
