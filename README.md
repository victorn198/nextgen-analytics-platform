# Data Pipeline Portfolio

![Social preview](./assets/social-preview.png)

End-to-end analytics engineering portfolio built with `Python`, `PostgreSQL`,
`dbt`, `FastAPI`, `Power BI`, and a custom desktop-style analytics dashboard.

This repository is intentionally structured as a portfolio case study, not just
a code dump. It shows the full analytics lifecycle: ingestion, warehousing,
quality, semantic modeling, API delivery, and an interactive BI product layer.

## Why This Repository Exists

I wanted one project that proves I can do more than assemble a final dashboard.
The repo demonstrates:

- API ingestion into a `raw` layer
- warehouse modeling with `dbt`
- snapshots and SQL tests
- monitoring and audit objects in SQL
- BI semantics and reporting structures
- API-first analytics delivery
- a desktop-first dashboard UX with Spotlight, Compare, Bookmarks, and Action Board

## What It Proves

- `100,000+` simulated order lines
- `10,000` customers
- `2,000` products
- `8` dbt models
- `1` dbt snapshot
- `4+` SQL data quality tests
- `19` API and semantic tests currently passing
- desktop analytics experience with pages for:
  - `Sales Overview`
  - `Revenue Trends`
  - `Predictive Outlook`
  - `Customer Segmentation`
  - `Retention Cohorts`
  - `Product Performance`
  - `Order Flow Operations`

## Gallery

### Desktop Shell

<img src="./assets/gallery/desktop-home.png" alt="NextGen desktop analytics shell" width="900">

### Sales and Predictive Views

<img src="./assets/gallery/desktop-sales-predictive.png" alt="Sales Overview window in the desktop analytics dashboard" width="900">

### Customer and Retention Views

<img src="./assets/gallery/desktop-products-retention.png" alt="Customer Segmentation and Retention Cohorts windows in the desktop analytics dashboard" width="900">

## Architecture

<img src="./assets/diagrams/architecture-overview.png" alt="NextGen analytics architecture overview" width="900">

## Warehouse and Database Layers

<img src="./assets/diagrams/warehouse-model.png" alt="Warehouse model and database layers derived from the repository structure" width="900">

Note: the warehouse image above is a repository-derived model view, not a live
GUI screenshot of PostgreSQL. I used that approach intentionally so the repo
shows the database structure even when a local database is not running.

## Analytics Built Into the Dashboard

The dashboard is not limited to topline KPIs. It includes business analysis
methods that a senior BI / analytics workflow would actually use:

- period-over-period comparisons with aligned partial-period handling
- Pareto and `ABC` concentration analysis
- `RFM` customer segmentation
- retention cohort views
- anomaly and structural shift detection
- forecast scenarios (`Base`, `Conservative`, `Upside`)
- drilldowns from chart -> segment -> underlying members
- Spotlight windows with local filters and frozen context

## Product Features

The desktop dashboard layer includes features that move it closer to a usable
analytics product instead of a static portfolio mockup:

- desktop-style navigation with windows and taskbar
- `Spotlight` windows for focused analysis
- `Compare` windows for side-by-side business slices
- `Bookmarks` to restore workspace layouts
- `Recent` items and `Action Board` for follow-up
- CSV export from detail and comparison views
- window design themes inside the desktop shell

## AI Collaboration Disclosure

I did use an AI coding assistant while building this repository. I do not hide
that, because the goal of the project is to show modern, defensible work.

I used AI for:

- implementation acceleration
- UI iteration and alternative design exploration
- refactoring and cleanup
- test expansion
- documentation drafting
- security review and hardening suggestions

I did **not** outsource the important parts of the project to AI. The product
direction, business framing, acceptance/rejection of changes, and final review
were still my responsibility. In practice, I used AI the same way many teams
now use it professionally: to move faster, compare options, and raise the
quality bar.

More detail: [AI Collaboration Disclosure](./docs/AI_COLLABORATION_DISCLOSURE.md)

## Quick Start

### Prerequisites

- Python `3.10+`
- Docker Desktop or local PostgreSQL
- Power BI Desktop (optional)

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Create `.env`

```bash
cp .env.example .env
```

### 3. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Load sample data

```bash
python scripts/loadsampledata.py --mode full_refresh
```

### 5. Run dbt

```bash
cd dbtproject
dbt deps
dbt run --full-refresh
dbt snapshot
dbt test
```

### 6. Create monitoring objects

```bash
cd ..
psql "postgresql://postgres:postgres@localhost:${POSTGRES_PORT:-5432}/analytics" -f scripts/setup_data_quality_audit.sql
psql "postgresql://postgres:postgres@localhost:${POSTGRES_PORT:-5432}/analytics" -f scripts/setup_data_quality_alerting.sql
psql "postgresql://postgres:postgres@localhost:${POSTGRES_PORT:-5432}/analytics" -f scripts/setup_operational_monitoring_views.sql
```

### 7. Run the desktop dashboard

```bash
uvicorn nextgen_dashboard.backend.main:app --reload --port 8601
```

Open `http://127.0.0.1:8601`

## Quality and Security

Run API tests:

```bash
pytest tests/test_nextgen_dashboard_api.py
```

Run the dashboard benchmark:

```bash
python scripts/benchmark_dashboard.py --threshold-seconds 1.50
```

Security posture added to the project:

- explicit CORS origins instead of wildcard access
- mutating agent endpoints disabled by default
- token-gated mutation flow when enabled
- static asset allowlist instead of serving the whole frontend directory
- atomic local writes for governed proposal state

Docs:

- [AI Agent Security](./docs/AI_AGENT_SECURITY.md)
- [Quality Gates](./docs/QUALITY_GATES.md)

## Repository Map

- `fivetran_simulator/`: ingestion simulators and scaled data generation
- `dbtproject/models/`: dbt transformations
- `dbtproject/tests/`: dbt SQL tests
- `scripts/setup_*.sql`: monitoring and data quality objects
- `scripts/benchmark_dashboard.py`: dashboard performance regression check
- `docs/MEASURE_DICTIONARY.md`: semantic definitions and measures
- `nextgen_dashboard/`: FastAPI backend plus the desktop-first frontend
- `assets/gallery/`: real screenshots from the project
- `assets/diagrams/`: generated architecture and warehouse visuals
- `assets/social-preview.png`: recommended GitHub repository social preview image

## Recruiter Summary

If you want the short version, this repo shows that I can build and explain an
analytics stack end to end:

- ingestion
- warehouse modeling
- tests and monitoring
- BI semantics
- API design
- desktop-style analytics UX
- secure and explainable iteration with AI assistance

## Useful Docs

- [GitHub Repository Setup](./docs/GITHUB_REPOSITORY_SETUP.md)

- [Architecture](./docs/ARCHITECTURE.md)
- [Data Lineage](./docs/DATA_LINEAGE.md)
- [dbt Models](./docs/DBT_MODELS.md)
- [Measure Dictionary](./docs/MEASURE_DICTIONARY.md)
- [Predictive Outlook Method](./docs/PREDICTIVE_OUTLOOK_METHOD.md)
- [Statistical Analytics Stack](./docs/STATISTICAL_ANALYTICS_STACK.md)
- [Project Interview Narrative](./docs/PROJECT_INTERVIEW_NARRATIVE.md)
- [Portfolio Action Plan](./docs/PORTFOLIO_ACTION_PLAN.md)
