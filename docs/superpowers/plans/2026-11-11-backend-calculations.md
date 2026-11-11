# Backend Calculations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add trustworthy ratios, period comparisons, rankings, stronger decision rules, Spearman relationships and benchmarked forecasts to the existing Speculara MVP.

**Architecture:** Keep parsing, validation and orchestration in backend/analysis.py. Add focused calculation helpers consuming its validated DataFrame, then extend the existing API result and React consumers without changing the layout. No new endpoint or persistence layer is required.

**Tech Stack:** Existing Python 3.12, FastAPI, pandas, numpy, scipy, unittest; React, TypeScript, Vite and Playwright.

**Spec:** docs/superpowers/specs/2026-11-11-backend-calculations.md

## Global Constraints

- Work directly inside the current folder.
- Do not initialize Git unless explicitly requested.
- Preserve the existing design and six analytical modules.
- Keep processing stateless and in memory.
- No database, required LLM, scraping, or new runtime dependencies.
- Use pandas, numpy and scipy already installed; retain Python 3.12 and Node >=22.12.0.
- Preserve the current upload limits: 5 MB, 20,000 rows, 50 columns, 30 MB expanded XLSX.
- Never fabricate metrics, model accuracy, causal effects or uplift.
- Do not deploy as part of this work.

## Review Focus

1. Unequal paired completeness and zero exposure must never produce a ratio from unrelated totals (Task 1).
2. Missing dates, invalid-date rows and zero prior totals must not become invented growth (Task 1).
3. Repeated post IDs and low-exposure categories must not generate confident winners (Tasks 2 and 3).
4. Tied ranks, constant values and small samples must retain honest statistical limits (Task 4).
5. Forecast selection must not train on holdout values or compare different date ranges; all consumers must use the selected model (Tasks 5 and 6).

---

## File map and execution conventions

- Create backend/calculations.py: ratios, periods, rankings and correlation helpers.
- Create backend/forecasting.py: daily-series baseline evaluation and forecast selection.
- Create backend/tests/test_calculations.py and backend/tests/test_forecasting.py: exact mathematical fixtures and edge cases.
- Modify backend/analysis.py: call helpers, schema v2, evidence-linked recommendation rules, Python chat/report wording.
- Modify backend/tests/test_analysis.py and backend/tests/test_api.py: orchestration and serialized contract checks.
- Modify src/analysis.ts: exact v2 types, deterministic chat routes and report sections.
- Modify src/App.tsx: reuse existing module cards and accessible data tables.
- Modify tests/analysis.test.ts and tests/browser/workflow.spec.ts: frontend evidence and workflow regressions.
- Update README.md, docs/architecture.md, docs/mvp-scope.md and docs/demo-script.md after integration.

No repository exists. Omit Git commits and worktree creation unless the user later authorizes them. Each task ends with a verified checkpoint; if Git is later authorized, that checkpoint is the natural commit boundary. Do not add synthetic fallback results.

Preflight: read the spec and current files. Run `.venv/Scripts/python -W error -m unittest discover -s backend/tests -v`, `npm test`, `npm run typecheck`, and `npm run build`. Record actual baseline failures before editing. Existing recorded baseline was 15 Python tests, 2 frontend tests and 4 Chromium workflows; rerun rather than assuming.

### Task 1: Paired ratios and equal-period comparisons

**Files:** Create backend/calculations.py and backend/tests/test_calculations.py.

**Interfaces:**
- Consumes: validated DataFrame with numeric metrics and UTC `YYYY-MM-DD` date labels; invalid dates are null.
- Produces: `calculate_ratios(df: pd.DataFrame) -> dict` and `compare_periods(df: pd.DataFrame) -> dict`.
- Ratio keys: sales_per_view and saves_per_view. Each value includes available, reason, numerator_metric, denominator_metric, numerator, denominator, percent, n, excluded_rows, zero_view_rows, notes. Missing pairs use null numeric outputs and n=0; all-zero denominator preserves known sums but percent=null.
- Period mapping keys: available metric names. Each includes available, reason, current_start, current_end, previous_start, previous_end, current_total, previous_total, absolute_change, percent_change, percent_change_reason. Unavailable windows have null totals/change values. No date or metric columns returns an empty mapping.

- [x] Step 1: Write unittest cases with the assertions below before creating helper implementations.

```python
r = calculate_ratios(pd.DataFrame({'views':[100,900,None], 'sales':[10,9,99]}))['sales_per_view']
self.assertAlmostEqual(r['percent'], 1.9)
self.assertEqual((r['numerator'], r['denominator'], r['n'], r['excluded_rows']), (19,1000,2,1))
r = calculate_ratios(pd.DataFrame({'views':[0], 'sales':[2]}))['sales_per_view']
self.assertFalse(r['available'])
self.assertIsNone(r['percent'])
```

Add separate tests for absent sales, saves-only ratios, all-null pairs, mixed zero-view pairs and ratios exceeding 100% (disclose, do not clamp). For 14 daily rows starting 2026-01-01 with seven sales values of 10 followed by seven of 20, assert prior/current totals 70/140, delta 70, growth 100, previous_end=2026-01-07 and current_end=2026-01-14. Assert a missing date, in-window null count or invalid-date row makes that metric unavailable; prior zero gives percent_change=null; old null counts outside the windows do not block calculation.

- [x] Step 2: Run `.venv/Scripts/python -m unittest discover -s backend/tests -p test_calculations.py -v`; confirm failure names missing helpers.
- [x] Step 3: Implement the two signatures above using paired sums and explicit calendar windows. Follow all null/coverage rules in the spec.
- [x] Step 4: Rerun the same tests with `-W error` before `-m`; expect all passing and finite JSON-compatible scalars.

### Task 2: Exposure-aware category and post rankings

**Files:** Modify backend/calculations.py and backend/tests/test_calculations.py.

**Interfaces:**
- Consumes: same validated frame as Task 1.
- Produces: `rank_performance(df: pd.DataFrame) -> dict` with categories and posts mappings. Each has sales_per_view and saves_per_view result objects with available, reason, rows and excluded_groups.
- Ranking rows: label, numerator, views, percent, n. Rows are capped at ten; excluded_groups counts labels rejected by eligibility rules. Missing grouping columns return unavailable with empty rows.

- [x] Step 1: Add separate tests: category A with three rows of views=400/sales=8 ranks at 2%; B with three rows of views=1000/sales=10 ranks below A at 1%, despite more raw sales. Assert A numerator=24, views=1200 and n=3. Assert two-row categories or total views=999 are excluded. Assert ties sort label ascending; eleven eligible labels return ten rows. Assert post views=99 are excluded, views=100 eligible, and any repeated nonblank post_id makes post ranking unavailable. Missing/blank post IDs do not become a shared named post.
- [x] Step 2: Run the Task 1 test command; confirm the new ranking tests fail for missing behavior.
- [x] Step 3: Implement `rank_performance` with separate complete positive-view cohorts for each numerator. Normalize group labels for display with stripped strings; exclude blank labels. Retain exact source labels otherwise.
- [x] Step 4: Run the full calculation suite; expect Task 1 and Task 2 tests passing.

### Task 3: Integrate measured findings and decision rules

**Files:** Modify backend/analysis.py, backend/tests/test_analysis.py and backend/tests/test_api.py.

**Interfaces:**
- Consumes: Task 1 and Task 2 helper dictionaries, existing correlations and demand signals.
- Produces: `build_recommendations(df: pd.DataFrame, ratios: dict, rankings: dict, correlations: list[dict], demand: dict) -> list[dict]`; entries retain title/evidence/action.
- `analyze(frame: pd.DataFrame) -> dict` adds ratios, periods and rankings and sets schema_version=2. Existing fields remain available. Correlation and forecast changes are delivered by Tasks 4 and 5 before frontend integration.

- [x] Step 1: Write failing recommendation tests. Assert unequal category exposure selects the higher sales/view category and evidence includes its numerator, views and n. Assert fewer than two eligible categories does not yield a category-winner recommendation. Assert four posts with views=[100,200,300,1400] and sales=[10,20,30,1] yield an offer/checkout experiment for the 1400-view post with 1 sale, using numpy percentile(method='linear') for the 75th percentile. Duplicate IDs suppress this post rule. Equal ratios do not claim one category is better. Text-only input retains evidence-collection or observed-inquiry guidance without fabricated numeric ratios.
- [x] Step 2: Add an API assertion that schema_version=2, sales_per_view.percent=2 for views=100/sales=2, and serialization contains no NaN/Infinity. Confirm unknown ratios serialize as null. Run the Python suite and observe new failures.
- [x] Step 3: Replace inline raw-mean category guidance with `build_recommendations`; wire helpers into `analyze` after validation. Reuse existing correlation/inquiry/fallback rules where their conditions still hold. Preserve stable rule ordering: paired overview, category experiment, post experiment, relationship, inquiries, fallback. Omit a rule when its evidence is insufficient.
- [x] Step 4: Run the full Python suite with warnings as errors; expect all tests passing. Confirm existing CSV/XLSX validation and source labels remain intact.

### Task 4: Add Spearman correlations with sample disclosures

**Files:** Modify backend/calculations.py, backend/analysis.py and backend/tests/test_calculations.py.

**Interfaces:**
- Produces: `calculate_correlations(df: pd.DataFrame) -> list[dict]`.
- Each entry preserves a, b, r, p, n and adds spearman_r, spearman_p, small_sample (n<10). All four statistics are finite floats. Preserve sorting by absolute Pearson r descending, with a/b lexical tie break.
- Consumed by `analyze`, recommendation rules and existing Pearson consumers; the default ranking remains Pearson.

- [x] Step 1: Write tests for x=[1,2,3,4], y=[1,4,9,16]: Spearman=1 and Pearson<1; tied inputs x=[1,1,2,3], y=[2,2,4,6]: Spearman=1. Assert paired nulls reduce n, constant columns are excluded, n=2 yields no pair, n=9 marks small_sample=true and n=10 marks false. Assert p-values stay finite and exact existing Pearson r/p/n keys remain present.
- [x] Step 2: Run calculation tests and confirm failure for missing helper/metadata.
- [x] Step 3: Implement using scipy.stats.pearsonr and spearmanr on identical complete pairs; guard nonconstant inputs and skip nonfinite results. Replace inline Pearson loop in analyze with this helper.
- [x] Step 4: Run all Python tests with warnings as errors. Expect unchanged legacy correlation assertions and new Spearman tests passing.

### Task 5: Compare forecast baselines without leakage

**Files:** Create backend/forecasting.py and backend/tests/test_forecasting.py; modify backend/analysis.py and backend/tests/test_analysis.py.

**Interfaces:**
- Produces: `forecast_daily(df: pd.DataFrame) -> dict`; consumes validated dates and metrics, owns existing metric priority and daily eligibility.
- Preserves available/reason/metric/method/mae/training_days/points. Adds selected_model ('linear' or 'last_value'), evaluation={holdout_dates: list[str], train_days: int, scores: {linear: float, last_value: float}}, notes. Unavailable results omit evaluation and points.
- Replaces the inline forecast block in analyze. Evaluation compares unrounded scores; display values may round to three decimals.

- [x] Step 1: Add an increasing 14-day sales series 1..14: linear MAE=0, last-value MAE=2, selected_model='linear', next value=15 and seven future dates. Constant sales=5 selects last_value on a tie, forecasts seven 5s, and reports both scores=0. A 14-day series of eleven 10s followed by three 0s must score both models at 10 (proves the holdout was not used for fitting). Assert training_days=14 and evaluation.train_days=11. Test descending linear forecasts clip at zero.
- [x] Step 2: Add eligibility tests for 13 dates, 366 dates, missing days, invalid-date rows and partially missing target values; all remain unavailable. Reordered input must yield the same forecast. Run the new suite and observe failure for missing forecasting helper.
- [x] Step 3: Implement `forecast_daily`, evaluating both candidates against exactly the same three dates, choosing the lower unrounded MAE and preferring last_value on exact ties. Refit chosen model on all eligible observations and return notes about the small holdout and unsupported seasonality/uncertainty.
- [x] Step 4: Run all Python tests with warnings as errors. Existing exact linear projection tests must still pass.

### Task 6: Keep dashboard, chat, reports and documentation consistent

**Files:** Modify src/analysis.ts, src/App.tsx, tests/analysis.test.ts, tests/browser/workflow.spec.ts, backend/analysis.py (answer/report), backend/tests/test_analysis.py, README.md, docs/architecture.md, docs/mvp-scope.md and docs/demo-script.md.

**Interfaces:**
- Consume schema v2 only. Add TypeScript types matching Tasks 1 to 5, using discriminated available/unavailable objects for new sections.
- Existing `answer(question: string, a: Analysis): string` and `analysisReport(a: Analysis, source: string)` stay public.
- Chat routing order: explicit growth/period, ratio/rate, ranking/best post, forecast, correlation, sentiment, recommendations, demand, totals, unsupported. Specific calculation intents precede generic trend/next/sales matches. Mirror this order in Python answer.

- [x] Step 1: Add frontend fixture tests before UI changes: rate answer includes numerator, denominator and excluded rows; growth answer includes both date windows and the zero-baseline explanation; rank answer respects unavailable repeated-ID state; forecast answer reports selected_model and both MAEs; correlation answer names Pearson and Spearman. Assert Markdown includes Ratios, Period comparisons, Rankings, source and all calculation limits. Add equivalent Python answer/report assertions for these intents, plus the existing unsupported-question behavior.
- [x] Step 2: Run `npm test` and Python tests; confirm failures identify missing sections/wording.
- [x] Step 3: Update v2 types, chat and report functions; render ratios/rankings in Charts, seven-day comparisons in Demand, both relationships/sample counts in Correlation and both errors/selected model in Predict. Use current neumorphic cards and exact-data tables, accessible headings, null explanations and units. No new screens, controls or CSS theme system are needed.
- [x] Step 4: Add browser assertions to real-upload workflows for the ratio explanation, dated growth, two model scores, Spearman label, unavailable repeated-ID ranking and new report headings. Upload text-only data and assert new numeric sections clearly report insufficient evidence. Keep existing 320px overflow, failed-upload retention and chat-reset checks.
- [x] Step 5: Run `.venv/Scripts/python -W error -m unittest discover -s backend/tests -v`, `npm test`, `npm run typecheck`, `npm run build`, and `npm run test:e2e` with both servers running. All must pass. Inspect phone and desktop screenshots after new numeric content is visible.
- [x] Step 6: Update the four docs with exact thresholds, ratio cohorts, period dates, schema version, two-model holdout method and unchanged sentiment limitations. Record verified commands and actual counts in docs/verification.md; do not copy old test counts. Obtain whole-change review and resolve material findings before reporting implementation complete.

## Self-review and handoff

Coverage checked: core numerical proposals map to Tasks 1 to 5; dashboard/chat/report consistency maps to Task 6. Sentiment model expansion, raw comment excerpts and production hardening are explicitly deferred in the spec. Every review-focus case has an owning test task. All helper names and response fields are defined above; no new service or library is required.

Recommended execution: native in this chat. These six tasks depend on one response contract and touch a small set of shared files, so sequential implementation avoids conflicting edits. This document authorizes no code execution by itself: request review and execution-method choice before implementation, per the writing-plans handoff.

## Execution completed 2026-11-12

User selected subagent-driven execution. All six tasks passed separate spec/quality reviews. Whole-change review found no blocking defects; its two minor findings were fixed and scoped re-review approved both. No Git or deployment operations occurred. See docs/backend-calculations-execution.md and docs/verification.md.
