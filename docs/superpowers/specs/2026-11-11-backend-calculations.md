# Backend calculation improvements specification

Date: 2026-11-11. Status: approved and implemented 2026-11-12 via subagent-driven execution.

## Goal and current behavior

Extend the existing stateless Speculara backend so users can compare attention, interest and observed sales, inspect relationships, and choose a measured next experiment. Existing totals, grouped sums, Pearson correlations, linear forecasts, text heuristics, upload validation and six-module React interface remain the starting point.

## Constraints

- Work directly inside the current folder.
- Do not initialize Git unless explicitly requested.
- Preserve the existing design and six analytical modules.
- Keep processing stateless and in memory.
- No database, required LLM, scraping, or new runtime dependencies.
- Use pandas, numpy and scipy already installed; retain Python 3.12 and Node >=22.12.0.
- Preserve the current upload limits: 5 MB, 20,000 rows, 50 columns, 30 MB expanded XLSX.
- Never fabricate metrics, model accuracy, causal effects or uplift.
- Do not deploy as part of this work.

## Calculation decisions

Ratios: calculate sales/views and saves/views as percentages of sums over rows complete in both metrics. Include known zero-view rows in the paired sums, disclose their count and return unavailable when the summed denominator is zero. Never average per-row percentages. Do not clamp ratios above 100%; disclose inconsistent measurement scopes. Expose numerator, denominator, complete-row count and excluded-row count. Ratios are proxies, not attributed conversion.

Periods: compare the latest seven UTC calendar dates against the immediately preceding seven. Anchor both windows on the dataset's latest valid date. Each metric needs all 14 represented dates and no missing metric values within these windows. A row with an invalid date blocks period comparison because its period membership is unknown. Missing dates are not zero activity. Older missing metric values outside the windows do not block comparison. Report exact window boundaries, known totals, absolute change and percentage change. If previous total is zero, percentage change is null with a reason, including when both totals are zero.

Rankings: rank categories using paired aggregate sales/views and saves/views separately; require at least three complete positive-view rows and 1,000 summed views per category. These are product heuristics, not statistical significance guarantees. Rank posts only when all nonblank post_id values are unique; repeated IDs make post ranking unavailable because snapshots versus increments are ambiguous. Eligible post rows require at least 100 views and both metrics. Return at most ten results per list, sorted by ratio descending then label ascending. No confidence or causal ranking claim.

Decision rules: retain evidence-grounded fallback guidance. Prefer category ratio comparisons to raw sales-per-row ranking. Require at least two eligible categories, and propose a matched-exposure experiment for the highest sales/view ratio. With at least four eligible unique posts and 1,000 summed paired views, identify a post at or above the 75th percentile of views with sales/view below the paired overall rate; choose highest views then post_id ascending. Suggest checking offer and buying instructions, with actual values and row counts. Zero rates are valid; ties do not imply winners. No universal performance benchmarks or invented impact scores.

Correlation: preserve existing Pearson r/p/n fields for compatibility and append Spearman rho/p for the same complete pairs. Require nonconstant columns and at least three complete pairs. Mark n<10 as exploratory small sample. Exclude undefined/nonfinite statistics. P-values remain unadjusted and assume independent observations. Tied ranks use scipy.stats.spearmanr defaults.

Forecasting: keep current daily eligibility (14 to 365 consecutive dates, complete target values, no invalid dates), metric priority and seven-day horizon. Compare linear and last-observed-value models on the same final three held-out dates, training both on the earlier dates. Select lowest unrounded MAE, breaking ties in favor of last-value. Refit the selected model on all data for projection. Existing mae becomes the selected model's holdout MAE. Report both scores, selected model and holdout dates. This is one small holdout comparison, not validated generalization performance. No accuracy percentage or confidence band.

Sentiment: retain current limited lexicon and limitations. Existing counts and keywords remain available. Do not add representative raw comments, emotion inference, or an NLP dependency in this iteration.

## Response and user-facing integration

Bump schema_version to 2. Preserve existing response fields and add ratios, periods and rankings; append correlation and predict metadata. Keep title/evidence/action recommendation fields. Backend calculations supply every new number; frontend only formats them. Update Charts, Demand, Correlation and Predict within their current cards. Chat and both Markdown/JSON exports must explain the same metrics, window boundaries, exclusions and limitations. Update Python answer/report helpers too, preventing contradictory wording.

All unavailable result objects carry available=false and a reason. Available objects carry available=true and reason=null, except optional explanatory notes, which use notes. JSON uses null for unknown values, never NaN/Infinity. No raw-row response expansion.

## Acceptance

Exact fixture calculations and edge cases pass Python unittest tests. Existing CSV/XLSX, chat/reset and mobile browser flows still pass. Add API and browser coverage for the new schema and visible calculation explanations. Documentation must distinguish new calculations from deferred NLP/production hardening. No performance or accuracy claims without measured evidence.
