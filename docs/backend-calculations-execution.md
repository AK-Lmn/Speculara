# Backend calculations execution record

Completed 2026-11-12 (Asia/Manila). User selected subagent-driven execution of the approved 2026-11-11 plan.

## Delivered

Schema 2 adds paired sales/view and saves/view percentages, exact seven-day comparisons, exposure-aware category/post rankings, evidence-linked decisions, Spearman metadata beside Pearson, and shared-holdout comparison of linear versus last-value forecasts. The existing six modules, chat and reports consume these results. The Speculara design, upload limits, stateless processing and dependency set remain intact.

## Review trail

Each task received a fresh implementer and separate spec-compliance/code-quality review. All six passed. A broader final review found no critical or important defects. Two minor findings were fixed in one final wave: required available forecast typing/structurally checked fixtures, and ranking limits in standalone chat. Scoped re-review found both addressed without introduced breakage. Desktop and mobile screenshots were visually inspected.

Detailed briefs, test reports, snapshot diffs and review reports remain in `.superpowers/sdd/backend-calculations/`. There are no Git commits because initialization was not authorized.

## Rulings made and costs

1. Used the existing folder with file snapshots rather than Git worktrees or commits. This follows the user's instruction. Cost: no commit history or Git rollback; baseline and snapshots provide the local audit trail.
2. Suppressed category-winner recommendations on tied top rates, and used the entire eligible post population for recommendations instead of the capped display lists. Cost if these product choices are unsuitable: fewer category recommendations and a need to revise the documented decision rules. This avoids false winners and truncation-dependent findings.
3. Used standard gpt-6.1-sol task implementers/reviewers and gpt-6-astra for the broad final review, as the selected workflow directs. Cost: added review time and model usage; user chose subagent-driven execution.
4. Retained snapshot/review artifacts because no Git history exists. Cost: a small local disk footprint. No application data is stored in these artifacts; they contain source/test snapshots and review records.

## Limits

No deployment, external LLM, new database or live social integration. No validation claim about real-campaign predictive performance, sentiment quality or causal uplift. Category/post eligibility thresholds are product heuristics. The forecast comparison uses one small chronological holdout, not validated generalization accuracy. Browser verification covers Chromium only. See docs/verification.md for final check results.
