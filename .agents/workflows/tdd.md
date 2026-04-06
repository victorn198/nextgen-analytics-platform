---
description: Apply a strict tests-first workflow to backend, dbt, and safe frontend changes
---

# TDD Playbook

This is a workflow document, not a built-in `codex-acp` slash command.

Use this when adding behavior, fixing bugs, or changing governed logic.

## 1. Write the Test First

Choose the closest test surface:

- backend/API -> `tests/test_nextgen_dashboard_api.py`
- semantic logic -> targeted API or service tests
- dbt -> schema/data tests in `dbtproject/`
- frontend helper logic -> add a focused test only if the repo already has a
  lightweight path for it; otherwise keep the change small and validate with
  syntax plus backend-facing checks

## 2. Make the Failure Visible

Run the smallest command that proves the test or check fails before the fix.

Examples:

```powershell
$env:NEXTGEN_SKIP_PREWARM="1"; venv\Scripts\python.exe -m pytest tests/test_nextgen_dashboard_api.py -v --tb=short -k "<name>"
node --check nextgen_dashboard/frontend/app.js
cd dbtproject; venv\Scripts\dbt test; cd ..
```

## 3. Implement the Smallest Fix

- change the narrowest layer possible
- avoid refactoring while making the test pass
- do not broaden scope beyond the failing behavior

## 4. Re-run and Expand

After the targeted test passes:

1. run the relevant local checks again
2. run `.agents/workflows/validate.md`
3. run `.agents/workflows/code-review.md`

## 5. Special Guardrails

- If KPI meaning changes, this is not a pure bug fix. Update semantic files,
  tests, and docs explicitly.
- If performance-sensitive code changed, run the benchmark before closing work.
- If dbt grain or join behavior changed, add or update dbt tests before
  considering the work done.
