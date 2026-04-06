---
name: verification-loop
description: Choose and run the right validation depth for backend, frontend, dbt, benchmark, and security-sensitive changes.
---

# Verification Loop

Use this skill after implementation and before declaring work complete.

## Step 1: Choose the Scope

- Backend/API: run pytest and benchmark
- Frontend: run `node --check` on touched JS files
- dbt/pipeline: run dbt commands
- Security-sensitive changes: add `security-scan`
- Semantic changes: confirm metrics, pages, tests, and docs stayed aligned

## Step 2: Run the Smallest Useful Checks First

1. Reproduce the targeted behavior or failure.
2. Run the closest validation to the touched files.
3. Escalate to full-project validation when the local checks pass.

## Step 3: Full Validation Commands

```powershell
$env:NEXTGEN_SKIP_PREWARM="1"
venv\Scripts\python.exe -m pytest tests/test_nextgen_dashboard_api.py -v --tb=short
node --check nextgen_dashboard/frontend/app.js
node --check nextgen_dashboard/frontend/desktop_lab.js
$env:NEXTGEN_SKIP_PREWARM="1"; venv\Scripts\python.exe scripts/benchmark_dashboard.py --threshold-seconds 1.50
```

For dbt changes:

```powershell
cd dbtproject
venv\Scripts\dbt run
venv\Scripts\dbt snapshot
venv\Scripts\dbt test
cd ..
```

## Reporting

Summarize only:

- checks run
- pass/fail outcome
- remaining risk
- whether KPI semantics or benchmark posture still need manual review

## Related Workflows

- `.agents/workflows/validate.md`
- `.agents/workflows/security-scan.md`
- `.agents/workflows/code-review.md`
