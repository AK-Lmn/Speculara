# Three-minute demo script

## Before the clock

Start both services or verify deployed URLs. Warm Render. Open the app at desktop width. Download fictional demo CSV, XLSX and text-only CSV. Keep screenshots and a generated Markdown report available as fallback. State clearly that demo records are synthetic.

## 0:00 to 0:25: problem

“Views tell us someone looked. Saves suggest interest. Sales tell us something happened. Marketing teams still need to decide what to test next. Speculara turns these scattered numbers into evidence-grounded decisions.”

Show original branding and six questions. Explain Bucket 05: Measure.

## 0:25 to 1:05: upload and decision

Choose **Try synthetic demo data**. Say: “These are 42 fictional post records, not a live social integration.”

Point to source label and data quality. Open Recommend. Read one actual evidence statement from the screen and its proposed test. Do not memorize numeric claims; use the computed result shown.

“The recommendation links its evidence to a next action. We do not promise reach uplift or confuse association with causation.”

## 1:05 to 1:35: inspect evidence

Show Charts and a category comparison. Change metric and open the exact-data table. Show Correlation, sample size and its caveat. Explain why views and sales can rise together without proving what caused sales.

## 1:35 to 2:00: forecast with limits

Open Predict. Show the seven projected dates and MAE in metric units. “This compares interpretable linear and last-value baselines on one small holdout. We report held-out error rather than invented accuracy. We refuse a forecast when date coverage is inadequate.”

## 2:00 to 2:25: ask and export

Open Ask Speculara. Ask “What should I do next?” and “Summarize totals.” Show answers agreeing with dashboard. Download report. “No LLM or API key is required. The report carries the evidence and limitations.”

## 2:25 to 2:45: honest text analysis

Upload `speculara-text-synthetic.csv`. Show Sentiment and Demand. “These separate fictional comments avoid repeating post totals. A small English/Filipino lexicon labels text; question counts indicate signals, not unique customers.” Show unavailable forecast if time permits.

## 2:45 to 3:00: close

“Speculara is not another dashboard of attractive numbers. It gives teams a measured finding, a reason to trust its limits, and the next test to run. The MVP processes uploads in memory without a database.”

## Judge questions

- Model accuracy? Both linear and last_value MAEs on one shared three-date holdout; selected model and no universal accuracy claim.
- Live integrations? None. CSV/XLSX exports are the current input.
- AI? Deterministic recommendation rules and text heuristic; external AI is optional future work.
- Privacy? No application upload persistence or database. Browser keeps the result until clear/refresh; hosting access logs still exist.
- What next? Validate usefulness with marketers, improve text evaluation and compare forecasting baselines on representative historical datasets.


## Schema 2 calculation contract

Only schema_version 2 is consumed. Available sections use reason=null; explanations use notes. Unavailable sections carry a reason. Unknown numeric values remain null.

Sales/view and saves/view percentages divide paired sums, not mean row percentages. Both values must be known; excluded rows, complete pairs and known zero-view rows are disclosed. Zero-view rows remain in overall sums; zero summed views make the ratio unavailable. Rates above 100% remain visible with a scope warning. These are proxies, not attributed conversion.

Category rankings require three complete positive-view rows and 1,000 views; unique nonblank post IDs require at least 100 views per complete post. Repeated IDs disable post rankings because snapshots and increments cannot be distinguished. Lists return at most ten, descending rate then ascending label. Thresholds are product heuristics, not significance guarantees. Category experiments need two eligible categories and a strict winner. The post experiment needs four eligible unique posts, 1,000 summed views, at least the linear-interpolated 75th percentile exposure, and rate below the overall paired rate; highest views then ID wins. No causal effectiveness or uplift is inferred.

Demand compares the latest seven UTC calendar dates with the preceding seven, anchored on the latest valid date. Exact start/end dates, totals, absolute count change and percent change are shown. All 14 dates must be represented; invalid dates block membership and missing counts within windows block that metric. Older missing values outside windows do not block it. Missing dates are not zeros. A zero prior total leaves percentage change null with an explanation, including zero-to-zero.

Pearson r/p and Spearman rho/p use the same nonconstant complete pairs (minimum three). n<10 is exploratory small sample. P-values are unadjusted and assume independent rows; no causal claim. Spearman uses SciPy default tied ranks.

Forecasts require 14–365 consecutive complete UTC daily dates, no invalid dates; priority sales, views, saves, likes, comments. Linear (clipped at zero) and last-observed-value baselines train before the same final three dates. Lowest unrounded MAE selects the model; ties choose last_value. Both errors in target count units, holdout dates and selected model are shown. Winner refits all days for seven projected dates. This is one small holdout comparison, not validated generalization performance. No accuracy percentage, confidence band, seasonality or trend lifespan is claimed.

Sentiment is unchanged: small English/Filipino lexicon, negation treated neutral; unsupported sarcasm, context and validated multilingual NLP. Counts/keywords are heuristic observations; question/request rows may overlap and are not unique buyers. No raw representative comments or new NLP dependency.

Six modules, deterministic chat and full Markdown/JSON exports share computed results. Specific growth, rate and ranking intents precede generic forecast/trend/next/sales routing. Text-only uploads show explicit unavailable numeric sections. Processing stays stateless and in memory; upload limits remain 5 MB, 20,000 rows, 50 columns and 30 MB expanded XLSX. Production hardening and NLP evaluation remain deferred.

Show Charts paired numerators, denominators, excluded rows and repeated-ID post ranking explanation. Show Demand exact dated windows. Ask “sales rate”, “sales growth trend” and “best post sales”. In Predict read both model errors, selected model and holdout dates. In Correlation point to Pearson, Spearman and n. Export includes Ratios, Period comparisons, Rankings and full schema 2 result.

## Decision-first presentation path (three minutes)

0:00-0:25: State the challenge: turn views, saves and sales into the next decision. Load the clearly labeled synthetic demo; explain that its records are fictional.

0:25-1:00: Read the Decision Brief. Show the observed weekly change, why it matters, one test and how to measure it. Explain that a pattern does not prove cause.

1:00-1:25: Show Views, Saves, Questions and Sales as separate counts. Point out missing questions if text was not supplied. Do not call the sequence tracked conversion.

1:25-2:00: Open an experiment card. Read evidence, proposed test and comparable-exposure measurement. Show optional evidence rather than reading every statistic.

2:00-2:30: Ask Speculara for the brief or how to measure a test. Show that the answer matches the dashboard. Download the report and point to its plain-language findings.

2:30-3:00: Upload the text-only synthetic file. Show detected columns, available modules and clear missing-data instructions before confirming. Finish with the next test, not a promised improvement. No live social account is connected.
