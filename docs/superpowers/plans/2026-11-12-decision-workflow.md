# Approved decision workflow

User approved eleven improvements and priority order on November 12, 2026. Continue in the existing folder, preserving design, calculations, explicit synthetic labeling and schema version 2. No platform sourcing claims, dependencies, Git initialization, upload or deployment. Existing UI audit fixes are frozen and reviewed.

Audience: nontechnical marketing teams. Tone: calm, plain language. Motion: existing subtle, reduced-motion aware. Layout: existing upload, summary, results and chat. Build on shared tokens and components.

## Shared contract

Extend analysis with optional additive fields, retaining every current field:

- `decision_brief: { changed: string; matters: string; try_next: string; measure: string }`. Choose a supported complete period comparison where possible (sales first); otherwise state observed totals and explicitly say weekly change needs dated complete data. Use existing recommendations and measured facts, never causal or improvement claims.
- `funnel: { stages: { key: 'views'|'saves'|'questions'|'sales'; label: string; value: number|null; note: string }[]; note: string }`. Questions are text rows with question signals, not numeric comments. Missing is null, true zero stays zero. These independent counts are not a tracked customer journey; no fabricated drop-off or conversion percentages.
- `preview: { columns: string[]; rows: Record<string, string|number|null>[]; total_rows: number }`. At most five rows and 160 characters per cell, finite JSON-safe values, normalized column names. API remains stateless. Analyze already calculates the candidate response; frontend stages it for user review before replacing active data, avoiding a second upload or endpoint.
- Recommendations retain title/evidence/action/details and add optional `success_metric: string`, `post_id: string`, `post_url: string`. Success metrics describe what to compare, with comparable exposure and no promised uplift. Build directly from structured calculations.
- `post_references: { post_id: string|null; post_url: string|null }[]` optional bounded list of usable references (up to365). Accept only absolute HTTP(S) links with a host, reject credentials/unsafe protocols. Never fetch links. Ambiguous ID-to-link associations must not be presented as definitive. Preserve post IDs as strings when parsing CSV; do not silently remove leading zeros. Add relevant plain warnings.

Frontend new helpers must tolerate absent additive fields for old fixtures/API data. No required LLM. Reports lead with the same decision brief, independent-count funnel, and experiments before full technical results. Chat answers brief/funnel/measurement requests deterministically from these fields, while existing answers remain stable.

## Execution

1. Backend additive contract and Python reports/answer helpers. Own backend files/tests only. Add meaningful edge tests first: text only, missing dates, zero prior totals, missing versus zero funnel stages, question semantics, invalid/ambiguous URLs, leading-zero IDs, preview limits. Keep existing statistical functions untouched. Write backend-report.md and freeze.
2. Frontend Decision Brief, funnel, experiment cards and post references, frontend types/report/chat parity. Own App.tsx and frontend helpers/tests. Consume agreed contract with graceful absence, reuse typography/tokens, 44px targets, wrapping, native details and safe external-link semantics. Decision Brief precedes module results; funnel has an explicit independence caveat. Recommendation cards show evidence, test and how to measure, first three prominent. Retain all module behavior and synthetic provenance. Write frontend-report.md and freeze.
3. Upload preview in App.tsx: uploads stage a candidate and show detected columns, five-row preview and truthful available-module statuses. Explicit Use this dataset / Cancel. Existing active analysis, timestamp and chat persist until confirmation; cancel/failure preserves them. Synthetic one-click demo remains immediate and clearly labeled. Preview of synthetic-labeled uploads must also say synthetic. Update affected browser workflows and add cancel/replacement/failure tests. Existing statuses/polish are reused, not duplicated. Write preview-report.md and freeze.
4. Independent task reviews, one final broad review, meaningful fixes, full Python/frontend/TypeScript/build/browser checks and visual mobile/keyboard/download verification. Update architecture/demo/verification docs. No claim of real social integration or validated prediction accuracy.

Backend and frontend can execute independently against this explicit contract. App edits remain sequential: frontend results then upload preview. Reviewers are read-only. No parallel broad suites. Use file snapshots because no Git exists. Keep artifacts as the only local change record.
