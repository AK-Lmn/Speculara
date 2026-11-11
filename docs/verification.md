# Verification record

Verified locally on 2026-11-12 in the existing Windows workspace. No Git initialization, deployment, new runtime dependencies, database or background server duplication.

| Command | Actual result |
| --- | --- |
| `.venv/Scripts/python -W error -m unittest discover -s backend/tests -v` | 62 tests passed |
| `npm test` | 3 tests passed |
| `npm run typecheck` | Passed |
| `npm run build` | Passed |
| `npm run test:e2e` | 5 Chromium workflows passed with existing Vite 8443 and API 8000 |

Task 6 red evidence: frontend fixture failed because sales-rate intent returned totals instead of numerator/denominator/exclusions. Equivalent Python fixture failed for the same missing rate routing. Green fixtures additionally verify dated windows and zero-baseline reason, repeated-ID unavailable rankings, selected model and both scores, Pearson/Spearman, source/full results, calculation limitations and unchanged unsupported-question behavior. Python checks available sentiment/demand reason=null while preserving heuristic counts and moving explanatory demand wording to notes.

Browser coverage: real CSV/XLSX uploads through the API; all six existing modules; paired-rate evidence; dated period comparison; linear and last_value model rows; Spearman label; actual Markdown download with Ratios, Period comparisons and Rankings; text-only unavailable numeric sections; explicit duplicated numeric post IDs with valid overall rate but unavailable ranking; failed-upload retention; chat reset and clear; keyboard skip link; 375px and 320px overflow checks; large counts and API failure.

Screenshots after numeric content is visible: `docs/screenshots/task6-desktop.png` and `docs/screenshots/task6-mobile.png`. Legacy mobile screenshot remains `docs/screenshots/mobile.png`. Visual inspection and whole-change review are recorded in the task report after review completion.

Earlier browser attempts found a row-header selector mistaken for a data-cell selector, incorrect assumptions that the numeric demo repeats post IDs and the text demo lacks IDs, and a 5-second cold-request wait. Tests now use real fixture properties, a dedicated duplicated-ID upload and a bounded 30-second first-analysis wait. Windows default encoding initially wrote a non-UTF-8 dash to analysis source; corrected to UTF-8 and verified build. These were implementation/test failures resolved before the final passing run. Playwright emits terminal color-environment warnings; these are unrelated to application behavior. Async API test debug timing messages are not warnings and the warning-as-error suite passes.

No deployed hosting, cross-browser coverage beyond Chromium, formal WCAG certification, adversarial load capacity, representative campaign forecast validation or multilingual sentiment accuracy was measured. One small shared three-date holdout comparison does not establish validated generalization performance.

## Final review and verification

All six task reviews passed spec compliance and quality. Whole-change review found no blocking defects. Its two minor findings were fixed in one wave and scoped re-review marked both addressed: forecast availability now requires a complete typed payload, fixtures are structurally checked, and both ranking chat paths disclose thresholds/cap/noncausal limits.

The coordinator reran final frozen source: Python 62 passed with warnings as errors; frontend 3 passed; TypeScript passed; production build passed; Chromium 5 passed (46.4s). Final build artifacts were 256.90 kB JS (80.26 kB gzip) and 26.97 kB CSS (6.18 kB gzip). These are artifact sizes, not user-performance scores. Backend health returned status=ok, storage=none. Desktop/mobile screenshots were visually inspected. No unresolved material review findings remain.

See docs/backend-calculations-execution.md for decisions and the retained audit trail.

## Plain-language update, 2026-11-12

Every module now leads with a plain finding; technical evidence is in closed See the numbers disclosures. Recommendations show at most three initial actions; chat defaults to one. Reports begin with a plain summary and retain technical evidence/full JSON. Computation helpers and forecast algorithms are unchanged.

Final frozen-source verification: 72 Python tests passed with warnings treated as errors; 8 frontend tests passed; TypeScript and production build passed; 7 Chromium workflows passed (52.8 seconds). Coverage includes relationship direction/strength boundaries, small samples, zero baselines, weekly declines, text-only uploads, hidden statistics/keyboard disclosure, unsupported questions, sales/saves intent separation, keyword counts, next-day forecasts and recommendation requests. Existing upload, error recovery, reports and 320px/375px checks remain covered.

Independent review identified metric selection, keyword routing, action intent, and historical week wording issues. Fixes were regression-tested and re-review marked all addressed. No material findings remain. Visual inspection includes docs/screenshots/plain-correlation.png, plain-demand.png and plain-mobile.png. Screenshots show synthetic input only. Native disclosures remain closed by default.

No deployment, extra dependencies, database or model changes. Verification covers Chromium only; real-campaign forecast validity and sentiment accuracy were not newly measured. Details: docs/plain-language.md.

## Readable dataset notes

Replaced the dataset-summary schema/method paragraph with About this data, a short 16px list with generous line spacing. Missing counts, unreadable dates, repeated entries and chart truncation still produce plain-language notes when relevant. Full technical methods and raw checks remain in reports/JSON.

Verified: 8 frontend tests, TypeScript and production build passed; 2 focused browser tests passed, checking font size, short copy, and preservation of file-specific warnings. Dataset-note screenshot visually inspected. No backend or calculation changes; backend suite was not rerun for this display-only edit.

## Chat spacing fix

The suggested-question strip overflowed horizontally (469px content in a 343px panel). Replaced it with short, wrapping question buttons; removed the scrolling strip. Kept header/suggestions/input from flex shrinking, allowed the message area to scroll within available height, used dynamic viewport height, and tightened launcher spacing. Question meanings and chat answers are unchanged.

Verified TypeScript and production build; three focused browser tests passed, including new 375x620, 320x420 and desktop bounds/suggestion tests, send and Escape close, plus existing plain-language chat flows. Chat screenshot visually inspected. No backend or calculation changes; backend tests were not rerun for this layout-only fix.

## Approved interface polish

Added file-analysis freshness, evidence-derived module badges, concise takeaways, copy finding with synthetic attribution, optional Why this matters hints, real loading/wait messages, column/date guidance, suggested-order recommendation labels, download-start feedback and Reset view separate from Clear data.

Final checks: 10 frontend tests passed; TypeScript and production build passed; 13 Chromium workflows passed (55.9 seconds). New browser coverage tests clipboard permission failure, synthetic copy provenance, delayed response messaging, unchanged data/timestamp after failed uploads, reset preservation and report confirmation. Independent review found no material issues; desktop/mobile screenshots were visually inspected. Earlier regression failures from repeated demand copy and old quick-question/details selectors were fixed. Calculations and backend unchanged; backend suite was not rerun. No platform-style labels, sourcing claims, GitHub push or deployment. See docs/interface-polish.md.
