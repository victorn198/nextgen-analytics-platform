---
description: Update documentation only where code or metrics changed, keeping portfolio narrative aligned with reality
---

# Docs-Update Playbook

This is a workflow document, not a built-in `codex-acp` slash command.

Use this when behavior, metrics, setup, or architecture changed in a way that a
reader of the portfolio would notice.

## 1. Identify the Source of Truth

Generate doc updates from the current code and config:

- semantic definitions -> `nextgen_dashboard/semantic/`
- API/backend behavior -> `nextgen_dashboard/backend/`
- dbt behavior -> `dbtproject/models/`, tests, snapshots
- setup and run flow -> `README.md`, `.env.example`, `docker-compose.yml`
- architecture narrative -> `docs/ARCHITECTURE.md`, `docs/DATA_LINEAGE.md`,
  `docs/MEASURE_DICTIONARY.md`

## 2. Update Only the Necessary Docs

Typical targets:

- `README.md`
- `README.pt.md`
- `docs/ARCHITECTURE.md`
- `docs/MEASURE_DICTIONARY.md`
- `docs/PREDICTIVE_OUTLOOK_METHOD.md`
- `docs/PROJECT_INTERVIEW_NARRATIVE.md`

If the change is internal-only and invisible to readers, say so and skip doc
edits.

## 3. Guardrails

- Do not change business language casually.
- Keep explanations interview-friendly and concrete.
- If KPI semantics changed, docs are mandatory, not optional.
- Do not document behavior that the code does not actually implement.

## 4. Verify

After doc edits, confirm:

- referenced files and routes exist
- commands still match the repo
- changed metrics/pages still map to the documented narrative
