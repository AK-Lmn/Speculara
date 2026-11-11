# Team workflow

Four-person team, three implementation lanes. The fourth teammate owns the demo, challenge framing and judge questions.

| Developer | Scope | Primary files |
| --- | --- | --- |
| 1: data/backend | Parsing, validation, statistics, API and Python tests | backend/ |
| 2: interface | Existing shell, six modules, uploads, chat, error/loading states | src/App.tsx, src/analysis.ts, src/index.css |
| 3: delivery | Demo records, deployment verification, docs and integration checks | public/demo/, docs/, netlify.toml, render.yaml, tests/ |
| 4: presentation | Three-minute pitch, demo rehearsal, honest claims, backup screenshots | docs/demo-script.md |

Agree on `src/analysis.ts` and API schema_version before parallel changes. Developer 1 owns response shape; Developer 2 owns UI consumption. Add fields rather than silently changing meanings. Never add a simulated fallback when the backend is unavailable.

Work within this extracted folder. Git has not been initialized. If the team later authorizes a repository, use short feature branches and reviewed changes. Do not force-push or commit `.venv`, `node_modules`, `.env` or uploaded private files. Synthetic demos may be shared.

Integration gate: Python suite, frontend tests, TypeScript and production build. Then run the actual browser with both services. Test successful upload, malformed file, missing columns, module switching, text-only analysis, dataset replacement, clear, chat and both report exports. Check a narrow phone viewport and keyboard focus. Record unresolved issues explicitly.

Before presentation: warm Render, confirm deployed frontend's API origin and CORS, download demo files locally, and rehearse fallback screenshots. A health endpoint alone does not prove the full upload workflow.
