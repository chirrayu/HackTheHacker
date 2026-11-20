# Repository Agent Guide

## Project Overview & Architecture

Hack The Hacker is an isolated SOC lab platform that ingests PCAP and Suricata traffic, runs deterministic and statistical threat detection, correlates events and alerts, and shows results in a live React dashboard. The stack uses Python/FastAPI/SQLAlchemy/Pydantic/Scapy for the backend, React/TypeScript/Vite/TanStack Query/Tailwind for the frontend, and SQLite by default with PostgreSQL fallback. Keep API routes in `backend/app/api/routes/`, database models and session setup in `backend/app/database/`, Pydantic request/response types in `backend/app/schemas/`, detection and scoring logic in `backend/app/detection/` and `backend/app/intelligence/`, frontend API calls in `frontend/src/services/`, and reusable UI in `frontend/src/components/`.

## Executable Commands

Run all commands from the repository root in Windows PowerShell.

### Setup

```powershell
Copy-Item backend/.env.example backend/.env -Force
python -m venv backend/venv
& backend/venv/Scripts/Activate.ps1
python -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend install
```

### Backend

```powershell
& backend/venv/Scripts/Activate.ps1
Set-Location backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
npm.cmd --prefix frontend run dev
```

### Build

```powershell
npm.cmd --prefix frontend run build
```

### Lint

```powershell
npm.cmd --prefix frontend run lint
```

### Type-check

```powershell
Set-Location frontend
npx.cmd tsc --noEmit
```

### Tests

```powershell
& backend/venv/Scripts/Activate.ps1
Set-Location backend
python -m pytest
```

Run one backend test file:

```powershell
& backend/venv/Scripts/Activate.ps1
Set-Location backend
python -m pytest app/tests/test_scoring.py
```

For a backend change, run at least the relevant test file and the full `python -m pytest` suite before finishing.

## Non-Obvious Code Conventions

- Keep FastAPI route modules thin: validate with Pydantic, obtain SQLAlchemy sessions through `Depends(get_db)`, perform queries/detection through service, detector, or intelligence classes, and return response models.
- Put schemas for API input and output in `backend/app/schemas/models.py`; do not return SQLAlchemy models directly.
- Put database mutations and persistence behavior behind SQLAlchemy session code or a dedicated service/detector, not in Pydantic models or frontend components.
- Use UTC `datetime` values for event, alert, and report timestamps. Serialize JSON evidence in the existing `raw_evidence`, `evidence`, or `reasons` string fields unless changing the schema intentionally.
- Preserve the `Low`, `Moderate`, `High`, `Critical` severity vocabulary and the existing alert status values.
- Keep network addresses and executable paths in settings/environment configuration rather than duplicating them in route or detector code.
- Frontend API access belongs in `frontend/src/services/api.ts`. Components and pages must consume typed API functions and TanStack Query; do not create separate Axios clients.
- Keep React components typed, small, and in named exports. Match the existing folder split: `components/common/`, `components/layout/`, `pages/`, `services/`, and `utils/`.
- TypeScript strictness is enabled (`strict`, `noUnusedLocals`, `noUnusedParameters`). Do not add `any`, unused exports/imports, or fallback casts to silence diagnostics.
- Use the existing `@/` alias for imports within `frontend/src/` when it improves clarity. Keep Tailwind utilities and existing dark SOC visual patterns consistent.

## Testing Expectations

- Add or update pytest coverage for every backend behavior change. Test detection thresholds, SQLAlchemy cleanup, API response status and shape, and 0–100 threat-score bounds where applicable.
- For database tests, use `SessionLocal`, call `init_db()`, create isolated records, and delete every inserted alert/event/score record after assertions. Do not depend on seeded data or the host PostgreSQL instance.
- Mock external services and host tools; tests must not require VirtualBox, Wireshark, TShark, live packet traffic, or real network access.
- If frontend test tooling is added, add a test script to `frontend/package.json` and place colocated `*.test.ts` or `*.test.tsx` files. Currently no frontend test runner or test script is configured, so at minimum run `npm.cmd --prefix frontend run lint` and `npm.cmd --prefix frontend run build`.
- For bug fixes, add a regression test that fails before the fix and passes after it.

## Guardrails & Do Not Touch Paths

- Never commit `.env`, real database credentials, API keys, private keys, certificates, or live capture data. Commit only `backend/.env.example` for configuration templates.
- Do not commit `frontend/node_modules/`, `backend/venv/`, `frontend/dist/`, databases, logs, PCAP/PCAPNG files, or runtime uploads; they are ignored by `.gitignore`.
- Do not edit `frontend/package-lock.json` or `backend/requirements.txt` unless dependency changes are explicitly in scope. If adding dependencies, update the relevant manifest and lockfile together and explain why.
- Treat `backend/hackthehacker.db`, `logs/`, `monitoring/captures/`, `backend/data/pcap_uploads/`, and generated model/cache directories as runtime output. Do not hand-edit or delete them.
- Do not change `scripts/reset_db.py` or directly reset/delete `hackthehacker.db` unless the user explicitly approves data destruction.
- Do not run VirtualBox, network-adapter, firewall, packet-capture, VM attack, or shutdown commands without user approval. The active environment must remain an isolated educational lab.
- Do not remove the default SQLite fallback or weaken CORS, authentication, secret, or network-isolation settings as an incidental change.
- Do not touch unrelated worktree changes. Review `git status` before editing and leave existing user changes intact.

## Git & PR Workflows

- Start work on a descriptively named branch: `feature/<short-topic>`, `fix/<short-topic>`, `test/<short-topic>`, or `docs/<short-topic>`.
- Use Conventional Commit subjects: `feat(frontend): add alert filters`, `fix(backend): prevent duplicate scan alerts`, `test(backend): cover scoring bounds`, or `docs: update agent instructions`.
- Keep commits focused; do not mix dependency upgrades, runtime files, generated output, or unrelated fixes.
- Before opening a PR, verify:
  - Relevant pytest tests pass.
  - `npm.cmd --prefix frontend run lint` passes.
  - `npm.cmd --prefix frontend run build` passes.
  - No `.env`, database, captures, virtualenv, `node_modules`, or generated build output is staged.
  - API or detection behavior changes include a focused test.
  - The diff contains no secrets or host-specific absolute paths.