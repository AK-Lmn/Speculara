import json
import math
import unittest

import pandas as pd
from scipy.stats import pearsonr

from backend.calculations import calculate_ratios, compare_periods
from backend import calculations
from backend.analysis import analyze


class CorrelationTests(unittest.TestCase):
    def test_monotonic_nonlinear_and_tied_ranks(self):
        for views, sales in (([1, 2, 3, 4], [1, 4, 9, 16]),
                             ([1, 1, 2, 3], [2, 2, 4, 6])):
            with self.subTest(views=views):
                row = calculations.calculate_correlations(pd.DataFrame({'views': views, 'sales': sales}))[0]
                self.assertAlmostEqual(row['spearman_r'], 1)
                self.assertEqual((row['a'], row['b'], row['n']), ('views', 'sales', 4))
                r, p = pearsonr(views, sales)
                self.assertEqual((row['r'], row['p']), (round(float(r), 4), float(p)))
                for key in ('r', 'p', 'spearman_r', 'spearman_p'):
                    self.assertIsInstance(row[key], float)
                    self.assertTrue(math.isfinite(row[key]))
                if views == [1, 2, 3, 4]:
                    self.assertLess(row['r'], 1)
                json.dumps(row, allow_nan=False)

    def test_complete_pairs_constants_and_minimum_sample(self):
        frame = pd.DataFrame({'views': [1, 2, 3, 4, None],
                              'sales': [1, 4, 9, None, 25], 'likes': [1] * 5})
        rows = calculations.calculate_correlations(frame)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['n'], 3)
        self.assertTrue(rows[0]['small_sample'])
        self.assertEqual(calculations.calculate_correlations(frame.iloc[:2]), [])
        self.assertEqual(calculations.calculate_correlations(pd.DataFrame()), [])

    def test_small_sample_boundary(self):
        for n in (9, 10):
            row = calculations.calculate_correlations(pd.DataFrame({'views': range(n), 'sales': range(n)}))[0]
            self.assertEqual(row['small_sample'], n < 10)

    def test_pearson_ranking_and_lexical_ties(self):
        frame = pd.DataFrame({'views': [1, 2, 3, 4], 'sales': [1, 4, 9, 16],
                              'likes': [1, 2, 3, 4], 'saves': [1, 2, 3, 4]})
        rows = calculations.calculate_correlations(frame)
        self.assertEqual(rows, sorted(rows, key=lambda row: (-abs(row['r']), row['a'], row['b'])))
        self.assertEqual([(row['a'], row['b']) for row in rows[:3]],
                         [('likes', 'saves'), ('views', 'likes'), ('views', 'saves')])

    def test_analyze_uses_shared_metadata_and_does_not_mutate_input(self):
        frame = pd.DataFrame({'views': [1, 2, 3, 4], 'sales': [1, 4, 9, 16]})
        original = frame.copy(deep=True)
        expected = calculations.calculate_correlations(frame)
        self.assertEqual(analyze(frame)['correlation'], expected)
        pd.testing.assert_frame_equal(frame, original)

    def test_nonfinite_input_has_no_pair(self):
        for value in (float('inf'), -float('inf')):
            frame = pd.DataFrame({'views': [1, 2, value], 'sales': [1, 2, 3]})
            self.assertEqual(calculations.calculate_correlations(frame), [])


class CalculationTests(unittest.TestCase):
    def frame(self):
        return pd.DataFrame({'date': pd.date_range('2026-01-01', periods=14).strftime('%Y-%m-%d'), 'sales': [10] * 7 + [20] * 7})

    def test_paired_sums(self):
        r = calculate_ratios(pd.DataFrame({'views': [100, 900, None], 'sales': [10, 9, 99]}))['sales_per_view']
        self.assertAlmostEqual(r['percent'], 1.9)
        self.assertEqual((r['numerator'], r['denominator'], r['n'], r['excluded_rows']), (19, 1000, 2, 1))

    def test_zero_denominator_preserves_sums(self):
        r = calculate_ratios(pd.DataFrame({'views': [0], 'sales': [2]}))['sales_per_view']
        self.assertFalse(r['available'])
        self.assertIsNone(r['percent'])
        self.assertEqual((r['numerator'], r['denominator'], r['zero_view_rows']), (2, 0, 1))

    def test_missing_sales_and_saves_only(self):
        r = calculate_ratios(pd.DataFrame({'views': [100], 'saves': [5]}))
        self.assertFalse(r['sales_per_view']['available'])
        self.assertIsNone(r['sales_per_view']['numerator'])
        self.assertEqual(r['sales_per_view']['n'], 0)
        self.assertEqual(r['saves_per_view']['percent'], 5)

    def test_all_null_pairs(self):
        r = calculate_ratios(pd.DataFrame({'views': [None, 1], 'sales': [2, None]}))['sales_per_view']
        self.assertFalse(r['available'])
        self.assertEqual((r['n'], r['excluded_rows']), (0, 2))
        self.assertIsNone(r['denominator'])

    def test_zero_rows_and_above_100_are_disclosed(self):
        r = calculate_ratios(pd.DataFrame({'views': [0, 10], 'sales': [5, 15]}))['sales_per_view']
        self.assertEqual((r['percent'], r['n'], r['zero_view_rows']), (200, 2, 1))
        self.assertTrue(r['notes'])
        self.assertIn('100%', ' '.join(r['notes']))
        json.dumps(r, allow_nan=False)

    def test_equal_calendar_periods(self):
        r = compare_periods(self.frame())['sales']
        self.assertTrue(r['available'])
        self.assertIsNone(r['reason'])
        self.assertEqual((r['previous_total'], r['current_total'], r['absolute_change'], r['percent_change']), (70, 140, 70, 100))
        self.assertEqual((r['previous_start'], r['previous_end'], r['current_start'], r['current_end']), ('2026-01-01', '2026-01-07', '2026-01-08', '2026-01-14'))
        json.dumps(r, allow_nan=False)

    def test_missing_date_or_count_or_invalid_date_blocks(self):
        frames = [self.frame().drop(3), self.frame(), self.frame()]
        frames[1].loc[3, 'sales'] = None
        frames[2].loc[3, 'date'] = None
        for frame in frames:
            with self.subTest(frame=frame.to_dict()):
                r = compare_periods(frame)['sales']
                self.assertFalse(r['available'])
                self.assertTrue(r['reason'])
                for key in ('current_total', 'previous_total', 'absolute_change', 'percent_change'):
                    self.assertIsNone(r[key])

    def test_previous_zero_has_no_percent(self):
        for current in (0, 20):
            frame = self.frame()
            frame['sales'] = [0] * 7 + [current] * 7
            r = compare_periods(frame)['sales']
            self.assertTrue(r['available'])
            self.assertIsNone(r['percent_change'])
            self.assertTrue(r['percent_change_reason'])

    def test_old_missing_count_does_not_block(self):
        frame = pd.concat([pd.DataFrame({'date': ['2025-12-01'], 'sales': [None]}), self.frame()], ignore_index=True)
        self.assertTrue(compare_periods(frame)['sales']['available'])

    def test_metric_coverage_independent_and_duplicate_dates_sum(self):
        frame = self.frame()
        frame['views'] = 100
        frame.loc[0, 'sales'] = None
        r = compare_periods(frame)
        self.assertTrue(r['views']['available'])
        self.assertFalse(r['sales']['available'])
        frame = pd.concat([self.frame(), self.frame().iloc[[0]]], ignore_index=True)
        self.assertEqual(compare_periods(frame)['sales']['previous_total'], 80)

    def test_absent_columns_and_all_invalid_dates(self):
        self.assertEqual(compare_periods(pd.DataFrame({'sales': [1]})), {})
        self.assertEqual(compare_periods(pd.DataFrame({'date': ['2026-01-01']})), {})
        r = compare_periods(pd.DataFrame({'date': [None], 'sales': [1]}))['sales']
        self.assertFalse(r['available'])
        self.assertIsNone(r['current_start'])

    def test_overflow_and_empty_results_remain_json_compatible(self):
        huge = pd.DataFrame({'views': [1, 1], 'sales': [1e308, 1e308]})
        r = calculate_ratios(huge)
        self.assertFalse(r['sales_per_view']['available'])
        json.dumps(r, allow_nan=False)
        frame = self.frame()
        frame['sales'] = 1e308
        r = compare_periods(frame)
        self.assertFalse(r['sales']['available'])
        json.dumps(r, allow_nan=False)
        json.dumps(calculate_ratios(pd.DataFrame()), allow_nan=False)

    def test_invalid_old_date_still_blocks(self):
        frame = pd.concat([pd.DataFrame({'date': [None], 'sales': [1]}), self.frame()], ignore_index=True)
        self.assertFalse(compare_periods(frame)['sales']['available'])


class RankingTests(unittest.TestCase):
    def rank(self, frame):
        return calculations.rank_performance(frame)

    def test_categories_use_paired_aggregate_rates(self):
        frame = pd.DataFrame({'category': ['A'] * 3 + ['B'] * 3,
                              'views': [400] * 3 + [1000] * 3,
                              'sales': [8] * 3 + [10] * 3})
        result = self.rank(frame)['categories']['sales_per_view']
        self.assertTrue(result['available'])
        self.assertIsNone(result['reason'])
        self.assertEqual(result['rows'], [
            {'label': 'A', 'numerator': 24, 'views': 1200, 'percent': 2, 'n': 3},
            {'label': 'B', 'numerator': 30, 'views': 3000, 'percent': 1, 'n': 3}])
        self.assertEqual(result['excluded_groups'], 0)

    def test_category_exposure_and_row_boundaries(self):
        frame = pd.DataFrame({'category': ['two'] * 2 + ['low'] * 3 + ['exact'] * 3,
                              'views': [1000, 1000, 333, 333, 333, 333, 333, 334], 'sales': 1})
        result = self.rank(frame)['categories']['sales_per_view']
        self.assertEqual([row['label'] for row in result['rows']], ['exact'])
        self.assertEqual(result['excluded_groups'], 2)

    def test_category_ties_sort_labels_and_cap_without_excluding_eligible(self):
        frame = pd.DataFrame([{'category': label, 'views': 400, 'sales': 0}
                              for label in reversed('ABCDEFGHIJK') for _ in range(3)])
        result = self.rank(frame)['categories']['sales_per_view']
        self.assertEqual([row['label'] for row in result['rows']], list('ABCDEFGHIJ'))
        self.assertEqual(result['excluded_groups'], 0)

    def test_each_numerator_has_separate_positive_view_cohort(self):
        frame = pd.DataFrame({'category': ['A'] * 5, 'views': [400, 400, 400, 0, 400],
                              'sales': [8, 8, 8, 100, None], 'saves': [None, 4, 4, 100, 4]})
        result = self.rank(frame)['categories']
        self.assertEqual(result['sales_per_view']['rows'][0],
                         {'label': 'A', 'numerator': 24, 'views': 1200, 'percent': 2, 'n': 3})
        self.assertEqual(result['saves_per_view']['rows'][0],
                         {'label': 'A', 'numerator': 12, 'views': 1200, 'percent': 1, 'n': 3})

    def test_post_minimum_exposure_and_missing_pairs(self):
        frame = pd.DataFrame({'post_id': ['low', 'exact', 'missing', 'high'],
                              'views': [99, 100, 500, 200], 'sales': [20, 2, None, 2]})
        result = self.rank(frame)['posts']['sales_per_view']
        self.assertEqual(result['rows'], [
            {'label': 'exact', 'numerator': 2, 'views': 100, 'percent': 2, 'n': 1},
            {'label': 'high', 'numerator': 2, 'views': 200, 'percent': 1, 'n': 1}])
        self.assertEqual(result['excluded_groups'], 2)

    def test_duplicate_nonblank_ids_block_both_post_rankings_globally(self):
        frame = pd.DataFrame({'post_id': ['p', ' p ', 'q'], 'views': [0, None, 100],
                              'sales': [None, None, 1], 'saves': [None, None, 2]})
        for result in self.rank(frame)['posts'].values():
            self.assertFalse(result['available'])
            self.assertTrue(result['reason'])
            self.assertEqual(result['rows'], [])

    def test_blank_labels_excluded_and_source_case_preserved(self):
        frame = pd.DataFrame({'post_id': [None, '', '  ', ' Mixed Case '],
                              'views': [100] * 4, 'sales': [1] * 4})
        original = frame.copy(deep=True)
        result = self.rank(frame)['posts']['sales_per_view']
        self.assertTrue(result['available'])
        self.assertEqual([row['label'] for row in result['rows']], ['Mixed Case'])
        self.assertEqual(result['excluded_groups'], 0)
        pd.testing.assert_frame_equal(frame, original)

    def test_category_labels_strip_and_merge_blank_labels_never_rank(self):
        frame = pd.DataFrame({'category': [' A ', 'A', ' A', '', None, '  '],
                              'views': [400] * 6, 'sales': [4] * 6})
        result = self.rank(frame)['categories']['sales_per_view']
        self.assertEqual(result['rows'], [
            {'label': 'A', 'numerator': 12, 'views': 1200, 'percent': 1, 'n': 3}])
        self.assertEqual(result['excluded_groups'], 0)

    def test_missing_columns_and_no_eligible_groups_are_unavailable(self):
        for frame in (pd.DataFrame(), pd.DataFrame({'category': ['A'], 'views': [400], 'sales': [1]})):
            result = self.rank(frame)
            for grouping in result.values():
                for item in grouping.values():
                    self.assertFalse(item['available'])
                    self.assertTrue(item['reason'])
                    self.assertEqual(item['rows'], [])
            json.dumps(result, allow_nan=False)

    def test_overflow_groups_are_excluded_and_json_finite(self):
        frame = pd.DataFrame({'category': ['huge'] * 3, 'views': [1e308] * 3, 'sales': [1e308] * 3})
        result = self.rank(frame)
        self.assertEqual(result['categories']['sales_per_view']['excluded_groups'], 1)
        json.dumps(result, allow_nan=False)
