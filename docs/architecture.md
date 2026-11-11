# Architecture

## Existing prototype and changes

The extracted project contained `src/App.tsx`, shared CSS, React 19, TypeScript, Tailwind 4 and Vite 8. Six modules and chat were implemented using deterministic pseudo-random values. Arbitrary social page links seeded results; notification controls only toggled text. The initial production build passed with Figma configuration warnings. There was no backend or test suite.

`vite.config.ts` now uses only React and Tailwind plugins. The HTML shell owns its title, language, metadata and favicon. `.figma/` files are retained as historical export metadata and are not imported by the app. `docs/baseline/` preserves the original configuration and component file. No Git repository was created.

## Runtime path

1. Browser selects a file. The frontend validates extension and byte size.
2. `POST /api/analyze` receives raw bytes with `X-Filename: upload.csv` or `upload.xlsx`. This deliberately avoids multipart temporary-file spooling.
3. Request streaming caps bytes at 5 MB. XLSX compressed expansion is checked before loading. Parsing uses `BytesIO` and first-sheet read-only iteration.
4. pandas normalizes headers and validates metric values. Missing metrics remain missing. Dates normalize to UTC daily labels.
5. `backend/analysis.py` computes summaries, grouped sums, correlations, optional forecast, lexicon text labels and rule-based recommendations. SciPy provides Pearson and least-squares calculations. numpy supports finite-value checks and error calculations.
6. JSON returns computed outputs, availability reasons and data-quality warnings. Raw uploaded rows are not returned. Category labels and keywords may still contain user-supplied text.
7. React retains results only in component memory. Six views, chat and browser-generated Markdown/JSON reports read this result. Clear or reload removes browser state.

Server buffers and frames become unreachable after each request; they are not securely erased from process memory. No application upload directory, database, history, external AI or social scraping exists. Responses use `Cache-Control: no-store`.

## Endpoint contract

`GET /api/health` returns `{ "status": "ok", "storage": "none" }`.

`POST /api/analyze` accepts a binary body and filename header. Success includes schema_version, rows, columns, metrics, totals, missing, warnings, charts, ratios, periods, rankings, correlation, predict, recommend, sentiment and demand. Synthetic provenance is inferred only from explicit dataset_label markers; it is a disclosure, not verified provenance. Schema is reflected in `src/analysis.ts`. Invalid datasets return HTTP 422 with a human-readable detail; oversize bodies return 413. Framework API documentation is available at `/docs`.

No server chat/report endpoints are needed. Chat performs deterministic intent matching over the current result. Markdown/JSON exports are assembled locally. `backend.analysis.answer/report` support Python-side verification of equivalent evidence, while frontend functions supply the user-facing wording.

## Statistical guardrails

Totals sum known values. Ratios use rows complete in both metrics; they are not attributed conversion rates. Category recommendations compare paired aggregate rates across at least two eligible categories.

Pearson uses complete pairs with at least three rows and nonzero variance. Reported p-values are exploratory and unadjusted. Independence assumptions may fail for repeated observations. Correlation is not a causal finding.

Forecasts require complete consecutive daily coverage. Two baselines compare on one untouched three-date holdout; the selected model refits all observations for projection. Linear predictions clip counts at zero. Both baseline errors and the selected model are disclosed; no calibrated uncertainty is claimed.

Sentiment uses a small documented lexicon in code. A negation token causes a neutral classification. It cannot resolve sarcasm, nuanced Filipino, mixed sentiment or entity context. Frequent words count occurrences, not people. Questions and requests may overlap.

## Boundaries and operational limits

No authentication, cross-worker throttling or production observability integration. CORS is an explicit origin allowlist, not authentication. Concurrent requests can multiply peak memory. Add upstream rate limits and resource monitoring before broad public use. Limits do not defend against every malformed compressed document. Keep libraries updated and avoid sensitive real records in public demos.

Charts return at most 365 sorted groups per dimension, with a warning when truncated; totals still cover all rows. Unknown columns do not enter analysis. Forecast eligibility is capped at 365 daily groups. No database, scikit-learn or statsmodels is needed for this baseline.

Reference: the supplied ManilaHack architecture document was read through Google Drive. It supports Python/FastAPI, in-memory parsing, native React visualizations, Netlify and Render. Its heavier ML libraries were treated as optional choices, not claimed integrations. The Figma web link was inaccessible; the extracted source was the design reference.


## Schema 2 calculation contract

Only schema_version 2 is consumed. Available sections use reason=null; explanations use notes. Unavailable sections carry a reason. Unknown numeric values remain null.

Sales/view and saves/view percentages divide paired sums, not mean row percentages. Both values must be known; excluded rows, complete pairs and known zero-view rows are disclosed. Zero-view rows remain in overall sums; zero summed views make the ratio unavailable. Rates above 100% remain visible with a scope warning. These are proxies, not attributed conversion.

Category rankings require three complete positive-view rows and 1,000 views; unique nonblank post IDs require at least 100 views per complete post. Repeated IDs disable post rankings because snapshots and increments cannot be distinguished. Lists return at most ten, descending rate then ascending label. Thresholds are product heuristics, not significance guarantees. Category experiments need two eligible categories and a strict winner. The post experiment needs four eligible unique posts, 1,000 summed views, at least the linear-interpolated 75th percentile exposure, and rate below the overall paired rate; highest views then ID wins. No causal effectiveness or uplift is inferred.

Demand compares the latest seven UTC calendar dates with the preceding seven, anchored on the latest valid date. Exact start/end dates, totals, absolute count change and percent change are shown. All 14 dates must be represented; invalid dates block membership and missing counts within windows block that metric. Older missing values outside windows do not block it. Missing dates are not zeros. A zero prior total leaves percentage change null with an explanation, including zero-to-zero.

Pearson r/p and Spearman rho/p use the same nonconstant complete pairs (minimum three). n<10 is exploratory small sample. P-values are unadjusted and assume independent rows; no causal claim. Spearman uses SciPy default tied ranks.

Forecasts require 14–365 consecutive complete UTC daily dates, no invalid dates; priority sales, views, saves, likes, comments. Linear (clipped at zero) and last-observed-value baselines train before the same final three dates. Lowest unrounded MAE selects the model; ties choose last_value. Both errors in target count units, holdout dates and selected model are shown. Winner refits all days for seven projected dates. This is one small holdout comparison, not validated generalization performance. No accuracy percentage, confidence band, seasonality or trend lifespan is claimed.

Sentiment is unchanged: small English/Filipino lexicon, negation treated neutral; unsupported sarcasm, context and validated multilingual NLP. Counts/keywords are heuristic observations; question/request rows may overlap and are not unique buyers. No raw representative comments or new NLP dependency.

Six modules, deterministic chat and full Markdown/JSON exports share computed results. Specific growth, rate and ranking intents precede generic forecast/trend/next/sales routing. Text-only uploads show explicit unavailable numeric sections. Processing stays stateless and in memory; upload limits remain 5 MB, 20,000 rows, 50 columns and 30 MB expanded XLSX. Production hardening and NLP evaluation remain deferred.
