# DSH-1 — Scaffold + thin data server

## Acceptance criteria
1. Vite + React + TypeScript + Vitest scaffold builds (`npm run build` green)
   and the test suite runs (`npx vitest run` green).
2. `server.py` (Python 3 stdlib only, no framework) serves on 127.0.0.1
   (default port 8765, --port override) with exactly three GET endpoints:
   /api/runs -> JSON list of run ids that have a ledger.jsonl;
   /api/ledger?run=<id> -> JSON array of that run's ledger rows;
   /api/findings -> JSON array of findings rows.
3. Any non-GET method returns 405. Unknown run id returns 404 with
   {error: "<reason>"}. Path traversal in the run parameter is refused.
4. A corrupt/unreadable source file returns 200 with
   {error: "<file>: <reason>"} for that source — the server never crashes
   and never fabricates rows.
5. Server tests (Python unittest) cover: happy path for all 3 endpoints,
   405 on POST, 404 on unknown run, traversal refusal, corrupt-file error
   format. CI runs build + vitest + server tests.

## Manifest (files you may touch)
- package.json, package-lock.json, tsconfig.json, vite.config.ts, index.html
- src/main.tsx, src/App.tsx, src/App.test.tsx, src/test-setup.ts
- server.py, test_server.py
- .github/workflows/ci.yml, .gitignore

## Design slice
- The server reads from a FACTORY_ROOT env var (default: the software-factory
  repo path) — runs/*/ledger.jsonl and state/findings.jsonl. Read-only: the
  server opens files for reading only, binds loopback only.
- The React app is a placeholder shell in this slice (data layer is DSH-2);
  it must render a heading and pass one smoke test.
- Vite dev proxy /api -> 127.0.0.1:8765 (vite.config.ts).
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- server: runs list, ledger rows, findings rows, 405, 404, traversal, corrupt.
- app: renders the dashboard heading (smoke).

## Definition of done
- `npm run build` green; `npx vitest run` green; `python3 -m unittest test_server` green.
- One commit on branch dsh-1. Do NOT merge; the human merges.
