---
description: Fix failing checks with minimal diffs and no opportunistic refactors
---

# Build-Fix Playbook

This is a workflow document, not a built-in `codex-acp` slash command.

Use this when tests, syntax checks, or dbt commands are failing.

## 1. Pick the Right Failing Command

- backend/API:
  - `venv\Scripts\python.exe -m pytest tests/test_nextgen_dashboard_api.py -v --tb=short`
- frontend:
  - `node --check nextgen_dashboard/frontend/app.js`
  - `node --check nextgen_dashboard/frontend/desktop_lab.js`
- dbt:
  - `cd dbtproject`
  - `venv\Scripts\dbt run`
  - `venv\Scripts\dbt test`
  - `cd ..`

## 2. Fix One Failure at a Time

For each error:

1. read the full traceback or syntax error
2. inspect the exact file and surrounding code
3. apply the smallest possible fix
4. rerun the failing command

## 3. Do Not Expand Scope

- no refactors
- no style cleanup unless it is the cause of the failure
- no new features
- no speculative performance work

## 4. Escalate Only If Needed

Stop and rethink if:

- the same failure persists after multiple small fixes
- the fix would change KPI semantics
- the error is caused by missing environment setup or external dependencies

## 5. Exit Criteria

- failing command passes
- no new failures were introduced
- the broader validation surface is still run before closing
