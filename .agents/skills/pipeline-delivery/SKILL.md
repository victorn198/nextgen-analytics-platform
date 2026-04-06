---
name: pipeline-delivery
description: Deliver ingestion and dbt changes with ECC-style planning and validation, adapted to this repository's ELT stack.
---

# Pipeline Delivery

Use this skill when modifying `fivetran_simulator/`, `dbtproject/`, `scripts/`,
or any backend surface that depends on warehouse outputs.

## Workflow

1. Inspect existing models, seeds, tests, and scripts before adding new logic.
2. Prefer extending existing pipeline stages over creating parallel paths.
3. Keep business logic close to the current layer:
   - extraction logic in `fivetran_simulator/`
   - warehouse transformations in `dbtproject/models/`
   - operational helpers in `scripts/`
4. Add or update validation near the change:
   - dbt schema/data tests
   - API tests if the dashboard depends on the new fields
   - benchmark if data shape changes can affect route latency
5. Run the end-to-end pipeline when the change affects warehouse outputs.

## End-to-End Commands

```powershell
docker compose up -d postgres
venv\Scripts\python.exe -m fivetran_simulator.extract_customers
venv\Scripts\python.exe -m fivetran_simulator.extract_products
venv\Scripts\python.exe -m fivetran_simulator.extract_orders
cd dbtproject
venv\Scripts\dbt run
venv\Scripts\dbt snapshot
venv\Scripts\dbt test
cd ..
```

## Review Focus

- schema drift
- metric drift
- broken joins or grain mismatches
- missing dbt tests
- non-idempotent loads
- performance regressions in downstream dashboard queries

## Related Workflows

- `.agents/workflows/pipeline.md`
- `.agents/workflows/tdd.md`
- `.agents/workflows/validate.md`
- `.agents/workflows/perf.md`
