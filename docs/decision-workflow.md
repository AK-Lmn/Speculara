# From findings to a decision

Speculara turns the current uploaded dataset into a Decision Brief: what changed, why it matters, what to try and how to measure the test. Complete existing weekly comparisons take priority. Without complete dated data, the brief states observed counts and explains why a weekly comparison is unavailable. Findings do not establish cause and effect.

## Counts and experiments

Views, saves, questions and sales appear together as independent counts. They are not tracked people moving through a customer journey. Questions count text entries matching the existing simple question check; the numeric comments column is not treated as questions. Missing values remain unknown, while known zero counts remain zero. No attributed conversion or drop-off rate is invented.

Experiment cards retain their evidence and proposed action, then explain what to compare. Use comparable exposure and measurement windows. Suggested order is not predicted impact, and no improvement is promised. Technical evidence remains expandable. The frontend and Python report/chat helpers use the same structured result fields.

## Upload preview and references

User uploads are analyzed into an in-memory candidate before replacing the active dataset. The preview shows detected columns, up to five bounded sample rows and the available modules. Confirming replaces the current results. Canceling or failing an upload keeps the active results. The clearly labeled one-click synthetic demo remains immediate.

Optional post IDs and HTTP(S) links identify supplied records. Links are never fetched or verified as connected accounts. Invalid, credential-bearing and ambiguous associations are omitted from active references, with warnings. CSV post identifiers preserve leading zeros. A post-specific experiment links only when its reference is unambiguous.

## Data contract

Schema version remains 2. Optional additive fields are `decision_brief`, `funnel`, `preview` and `post_references`. Recommendations retain existing fields and add `success_metric`, structured `experiment_kind`, and supported `post_id`/`post_url` references. Old responses without the additions remain readable. Existing statistical calculations are unchanged.

Processing remains stateless and in memory. Preview data is returned to the browser with the analysis rather than saved on the server. Reports place the brief, independent counts and experiments before complete technical results. Synthetic records remain explicitly labeled. No live social integration is implied.
