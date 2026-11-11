import json
import unittest
import pandas as pd
from backend.analysis import analyze, parse_file, answer, report


class DecisionWorkflowTests(unittest.TestCase):
    def test_text_questions_and_missing_versus_zero(self):
        result = analyze(pd.DataFrame({'text':['Where to buy?', 'nice', None], 'views':[0, None, 0], 'comments':[9,9,9]}))
        stages = {s['key']: s['value'] for s in result['funnel']['stages']}
        self.assertEqual(stages, dict(views=0, saves=None, questions=1, sales=None))
        self.assertIn('independent', result['funnel']['note'])
        self.assertIn('weekly change', result['decision_brief']['changed'].lower())
        self.assertIn('independent', answer('show funnel', result))
        self.assertIn(result['decision_brief']['changed'], answer('decision brief', result))
        self.assertIn('comparable', answer('how to measure success', result))
        document = report(result)
        self.assertLess(document.index('Decision brief'), document.index('Ratios'))
        self.assertIn('Independent counts', document)

    def test_complete_sales_period_zero_baseline(self):
        result = analyze(pd.DataFrame({'date':pd.date_range('2026-01-01', periods=14).strftime('%Y-%m-%d'), 'sales':[0]*7+[1]*7}))
        self.assertIn('7 sales', result['decision_brief']['changed'])
        self.assertIn('previous week had no sales', result['decision_brief']['changed'])
        self.assertNotIn('100%', result['decision_brief']['changed'])

    def test_references_preserve_ids_and_reject_unsafe_ambiguous_links(self):
        frame = parse_file(b'post,views,post_url\n001,100,https://example.com/a\n002,100,javascript:alert(1)\n003,100,https://example.com/a\n004,100,https://u:p@example.com/a\n005,100,https://example.com/one\n005,100,https://example.com/two\n006,100,https:///missing\n', 'data.csv')
        self.assertEqual(frame['post_id'].iloc[0], '001')
        result = analyze(frame)
        refs = result['post_references']
        self.assertIn({'post_id':'001', 'post_url':None}, refs)
        self.assertIn({'post_id':'005', 'post_url':None}, refs)
        self.assertTrue(all(r['post_url'] is None for r in refs))
        self.assertTrue(any('ambiguous' in w.lower() for w in result['warnings']))
        self.assertTrue(any('unsafe' in w.lower() for w in result['warnings']))

    def test_valid_reference_and_experiment_measurement(self):
        result = analyze(pd.DataFrame({'post_id':list('abcd'),'post_url':['https://example.com/'+p for p in 'abcd'], 'views':[100,200,300,1400], 'sales':[10,20,30,1]}))
        experiment = next(r for r in result['recommend'] if r.get('post_id') == 'd')
        self.assertEqual(experiment['post_url'], 'https://example.com/d')
        self.assertTrue(all('comparable' in r['success_metric'] or 'Keep audience size and time windows similar.' in r['success_metric'] for r in result['recommend']))

    def test_default_brief_and_funnel_use_plain_measurement_cautions(self):
        result = analyze(pd.DataFrame({'views':[100,200,300,1400], 'sales':[10,20,30,1]}))
        measure = result['decision_brief']['measure']
        note = result['funnel']['note']
        self.assertEqual(measure, 'Compare sales and views before and after the test. Keep audience size and time windows similar. This does not track which views led to sales.')
        self.assertIn('independent counts, not a tracked customer journey', note)
        self.assertIn('which people moved between steps or which views led to sales', note)
        for text in (measure, note):
            self.assertNotIn('proxy', text.lower())
            self.assertNotIn('attributed', text.lower())

    def test_preview_is_bounded_normalized_and_json_safe(self):
        result = analyze(pd.DataFrame({'Views':[1]*370, 'Long Text':['x'*200]*370, 'Extra':[float('inf')]+[None]*369, 'Post ID':[str(i) for i in range(370)]}))
        preview = result['preview']
        self.assertEqual(preview['total_rows'],370)
        self.assertEqual(len(preview['rows']),5)
        self.assertIn('long_text',preview['columns'])
        self.assertEqual(len(preview['rows'][0]['long_text']),160)
        self.assertIsNone(preview['rows'][0]['extra'])
        self.assertLessEqual(len(result['post_references']),365)
        json.dumps(result,allow_nan=False)

    def test_text_only_and_incomplete_dates_have_no_invented_change(self):
        for frame in (pd.DataFrame({'text':['hello']}), pd.DataFrame({'date':['2026-01-01',None], 'sales':[2,3]})):
            result = analyze(frame)
            self.assertIn('Weekly change needs dated complete data', result['decision_brief']['changed'])
            self.assertIsNone(next(s for s in result['funnel']['stages'] if s['key']=='saves')['value'])

    def test_csv_normalized_identifier_headers_and_blank_ids(self):
        for header in ('Post ID', 'post', 'post_id'):
            frame = parse_file((header+',views\n0001,0\n,1\n').encode(), 'data.csv')
            self.assertEqual(frame['post_id'].iloc[0], '0001')
            self.assertTrue(pd.isna(frame['post_id'].iloc[1]))
            result = analyze(frame)
            self.assertEqual(result['post_references'], [{'post_id':'0001','post_url':None}])

    def test_experiment_grounding_survives_title_edits(self):
        from backend.analysis import build_recommendations, period_summary
        from backend.decisions import add_decision_fields
        frame = pd.DataFrame({'post_id':list('abcd'), 'views':[100,200,300,1400], 'sales':[10,20,30,1]})
        result = analyze(frame)
        result['recommend'] = build_recommendations(frame, result['ratios'], result['rankings'], result['correlation'], result['demand'])
        experiment = next(item for item in result['recommend'] if item.get('post_id') == 'd')
        experiment['title'] = 'Review this offer'
        add_decision_fields(result, frame, period_summary)
        self.assertEqual(experiment['post_id'], 'd')
        self.assertIn('sales and views', experiment['success_metric'])

    def test_empty_userinfo_credentials_are_rejected(self):
        result = analyze(pd.DataFrame({'views':[1,1], 'post_id':['a','b'], 'post_url':['https://@example.com/post','https://:@example.com/post']}))
        self.assertTrue(all(ref['post_url'] is None for ref in result['post_references']))
        self.assertTrue(any('Unsafe' in warning for warning in result['warnings']))

    def test_technical_forecast_measurement_keeps_technical_route(self):
        from backend.analysis import technical_answer
        result = analyze(pd.DataFrame({'date':pd.date_range('2026-01-01', periods=14).strftime('%Y-%m-%d'), 'sales':list(range(14))}))
        self.assertIn('MAE', answer('How is forecast error measured?', result))
        self.assertIn('MAE', technical_answer('How is forecast error measured?', result))
        self.assertEqual(answer('How do I measure a test?', result), result['decision_brief']['measure'])
