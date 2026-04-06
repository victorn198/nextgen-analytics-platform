---
description: Plan repository changes with ECC-style step breakdown, adapted to governed analytics work
---

# Plan Playbook

This is a workflow document, not a built-in `codex-acp` slash command.

Use this before non-trivial implementation. The output should be a concrete plan,
not code.

## 1. Classify the Request

Determine which surface is affected:

- semantic
- analytical
- UX/frontend
- performance
- pipeline/dbt
- security
- documentation

## 2. Inspect Before Proposing

Read the current implementation before planning:

- nearest source files
- relevant tests
- relevant semantic definitions
- docs that would become stale if behavior changes

Do not invent new layers if an existing one already owns the behavior.

## 3. Define the Narrowest Change

For each planned edit, specify:

- file path
- exact responsibility of the file
- why this layer is the right one
- risk to KPI semantics, security, or benchmark performance

## 4. Attach Validation Up Front

Every plan must name the validation commands required after implementation.

- Backend/API -> pytest + benchmark
- Frontend -> `node --check`
- dbt -> `dbt run`, `dbt snapshot`, `dbt test`
- Semantic changes -> tests + docs review

## 5. Output Format

Produce:

1. brief overview
2. assumptions and risks
3. file-by-file plan
4. validation checklist

If the request looks larger than the portfolio needs, say so and propose a
smaller version first.
