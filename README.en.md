# Data Pipeline Portfolio

Production-ready end-to-end data engineering project with Snowflake, dbt, Python ETL.

## Architecture

```
RAW <- Python ETL (1,600 records)
  |
STAGING <- dbt models (clean views)
  |
MARTS <- Fact/Dimension tables
```

## Data Loaded

| Table | Records | Description |
|-------|---------|-------------|
| orders_raw | 1,000 | Orders with customer/product |
| customers_raw | 500 | Brazilian customers |
| products_raw | 100 | Categorized products |

## Tech Stack

- **Snowflake**: Data Warehouse (ANALYTICS.RAW)
- **Python**: ETL automation (loadsampledata.py)
- **dbt**: Transformations (STAGING/MARTS)
- **GitHub Actions**: CICD pipeline

## Key Features

- Production-ready ETL with error handling
- dbt 7 transformation models
- Data quality testing and validation
- Modular architecture (Staging → Intermediate → Marts)
- Scalable for real APIs and production workloads

## Skills Demonstrated

- Data Warehouse design and 3-layer architecture
- Python ETL development and automation
- dbt ELT best practices and modeling
- Git version control and CICD pipeline
- Data quality testing and validation

---

Victor Nogueira | Data Engineer | Sao Paulo, BR