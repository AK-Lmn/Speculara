# MVP scope

## Submission story

A marketing team has views, saves and sales but needs its next decision. Speculara converts an export into inspectable evidence and small proposed tests. The product's credibility comes from showing what is measured and refusing unsupported conclusions.

## Included

Existing Speculara identity and six modules; CSV/XLSX import; input limits; header normalization; missing-value disclosure; genuine totals, grouped charts and Pearson correlations; conditional seven-day baseline forecasts; holdout MAE; limited text lexicon; observed demand signals; evidence-linked action rules; deterministic dataset chat; Markdown and JSON downloads; synthetic demo files; local run and hosting configuration.

## Explicitly excluded

Social platform login/scraping, live feeds, notifications, external LLMs, long-term storage, user accounts, validated multilingual sentiment, customer attribution, item/basket recommenders, calibrated prediction intervals, causal uplift, inventory optimization and market-wide trend lifespan.

## Acceptance checks

- CSV and XLSX containing the same rows return the same computed totals.
- Different uploaded values change outputs; filenames do not generate results.
- Blank metrics stay unknown, invalid negative/infinite/nonnumeric counts fail clearly.
- Missing dates, text or numeric pairs produce precise unavailable states.
- Text-only data supports sentiment without claiming campaign totals.
- Chat reports only the active result, and resets on successful replacement or clear.
- Failed uploads preserve the prior successful dataset, with its source label visible.
- Every action cites measured evidence and frames the next step as a test.
- Charts have zero-based axes, readable labels and exact data tables.
- Report downloads include source, limitations and computed results.
- Production build and automated tests pass before deployment.

## Known limits

Dataset grain must be checked by the user. Duplicates are warned about and retained. Sales/view ratios are proxies. Daily trend extrapolation may be poor under structural changes or seasonality. Sentiment is intentionally limited. UI keeps results only until refresh. Mobile and keyboard checks are part of the delivery checklist, not a claim of certified accessibility.


## Schema 2 calculation contract

Only schema_version 2 is consumed. Available sections use reason=null; explanations use notes. Unavailable sections carry a reason. Unknown numeric values remain null.

Sales/view and saves/view percentages divide paired sums, not mean row percentages. Both values must be known; excluded rows, complete pairs and known zero-view rows are disclosed. Zero-view rows remain in overall sums; zero summed views make the ratio unavailable. Rates above 100% remain visible with a scope warning. These are proxies, not attributed conversion.

Category rankings require three complete positive-view rows and 1,000 views; unique nonblank post IDs require at least 100 views per complete post. Repeated IDs disable post rankings because snapshots and increments cannot be distinguished. Lists return at most ten, descending rate then ascending label. Thresholds are product heuristics, not significance guarantees. Category experiments need two eligible categories and a strict winner. The post experiment needs four eligible unique posts, 1,000 summed views, at least the linear-interpolated 75th percentile exposure, and rate below the overall paired rate; highest views then ID wins. No causal effectiveness or uplift is inferred.

Demand compares the latest seven UTC calendar dates with the preceding seven, anchored on the latest valid date. Exact start/end dates, totals, absolute count change and percent change are shown. All 14 dates must be represented; invalid dates block membership and missing counts within windows block that metric. Older missing values outside windows do not block it. Missing dates are not zeros. A zero prior total leaves percentage change null with an explanation, including zero-to-zero.

Pearson r/p and Spearman rho/p use the same nonconstant complete pairs (minimum three). n<10 is exploratory small sample. P-values are unadjusted and assume independent rows; no causal claim. Spearman uses SciPy default tied ranks.

Forecasts require 14–365 consecutive complete UTC daily dates, no invalid dates; priority sales, views, saves, likes, comments. Linear (clipped at zero) and last-observed-value baselines train before the same final three dates. Lowest unrounded MAE selects the model; ties choose last_value. Both errors in target count units, holdout dates and selected model are shown. Winner refits all days for seven projected dates. This is one small holdout comparison, not validated generalization performance. No accuracy percentage, confidence band, seasonality or trend lifespan is claimed.

Sentiment is unchanged: small English/Filipino lexicon, negation treated neutral; unsupported sarcasm, context and validated multilingual NLP. Counts/keywords are heuristic observations; question/request rows may overlap and are not unique buyers. No raw representative comments or new NLP dependency.

Six modules, deterministic chat and full Markdown/JSON exports share computed results. Specific growth, rate and ranking intents precede generic forecast/trend/next/sales routing. Text-only uploads show explicit unavailable numeric sections. Processing stays stateless and in memory; upload limits remain 5 MB, 20,000 rows, 50 columns and 30 MB expanded XLSX. Production hardening and NLP evaluation remain deferred.
