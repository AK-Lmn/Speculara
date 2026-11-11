# Speculara implementation plan

Goal: turn the existing interface into an honest, stateless analytics MVP.
Architecture: retain React shell, primitives, branding and six modules. FastAPI parses in-memory uploads and returns measured summaries. Chat and report consume the same result.
Constraints: no Git initialization, database, deployment, scraping, LLM requirement, or invented accuracy. CSV and XLSX only. Netlify frontend, Render backend.

- [x] Baseline: install dependencies, run original build, preserve original App and Vite config under docs/baseline.
- [x] Backend: test upload validation, normalization, missing data, totals, correlations, forecast eligibility, sentiment and report/chat evidence. Implement bounded parsing and deterministic calculations.
- [x] Frontend: preserve shell and chart primitives; replace simulated module internals, source form and chat answers. Add loading, errors, source transparency and report downloads.
- [x] Delivery: synthetic demo CSV/XLSX, Netlify/Render configuration, documentation and three-minute script.
- [x] Verify: Python suite, TypeScript, production build and browser workflow where available.

Review focus: malformed files, missing columns, constant metrics, partial dates, stale upload/chat state, zero denominators, large XLSX expansion and API outages.
Ruling: proceed in current folder without approval pauses, per explicit user instruction. Do not initialize Git or create a worktree.

Verification ledger: original build passed. Fifteen Python tests pass with warnings treated as errors; two frontend tests pass; four browser workflows passed after fixing mobile chart-label overflow. Independent review found CSV width inference and contradictory demand guidance; both reproduced with failing regressions and fixed. Final production checks recorded in docs/verification.md.
