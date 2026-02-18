# README.md - Data Pipeline Portfolio Project

## ðŸŽ¯ Project: End-to-End Data Engineering Pipeline

A **production-ready, end-to-end data engineering project** demonstrating modern data stack best practices with Snowflake, dbt, Fivetran (simulated), Power BI, and MCP integration.

**Perfect for showcasing your data engineering skills to future employers! ðŸ“Š**

---

## ðŸ—ï¸ Architecture Overview

```
Data Sources (APIs) 
    â†“
Python Extraction (Fake Store API connector)
    â†“
Snowflake RAW Layer (Landing Zone)
    â†“
dbt Transformations
    â”œâ”€ STAGING (Cleaning)
    â”œâ”€ INTERMEDIATE (Business Logic)
    â””â”€ MARTS (Analytics Ready)
    â†“
Power BI Dashboards + Analytics
    â†“
MCP + Gemini CLI (AI Insights)
```

---

## ðŸš€ Quick Start (5 Minutes)

### 1. Prerequisites
```bash
# Install Python 3.10+
# Install Git
# Snowflake account (free trial available)
```

### 2. Clone & Setup
```bash
git clone https://github.com/yourusername/data-pipeline-portfolio
cd data-pipeline-portfolio
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Snowflake
Create `.env` file in root:
```env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ANALYTICS
SNOWFLAKE_SCHEMA=RAW
```

### 4. Run Setup Script
```bash
cd ..
python scripts/loadsampledata.py
cd ../dbt_project
dbt run
dbt test
```

### 5. Check Results
```bash
dbt docs generate
dbt docs serve  # Opens interactive documentation
```

---

## ðŸ“ Project Structure

```
data-pipeline-portfolio/
â”‚
â”œâ”€â”€ fivetran_simulator/          # Data extraction layer
â”‚   â”œâ”€â”€ extract_orders.py        # Simulates orders API
â”‚   â”œâ”€â”€ extract_customers.py     # Simulates customer CRM
â”‚   â””â”€â”€ extract_products.py      # Simulates product catalog
â”‚
â”œâ”€â”€ dbtproject/                 # Transformation layer
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ staging/             # Raw â†’ Cleaned
â”‚   â”‚   â”œâ”€â”€ intermediate/        # Business logic
â”‚   â”‚   â””â”€â”€ marts/               # Analytics tables
â”‚   â”œâ”€â”€ tests/                   # Data quality tests
â”‚   â””â”€â”€ macros/                  # Reusable components
â”‚
â”œâ”€â”€ mcp_tools/                   # AI Integration
â”‚   â”œâ”€â”€ data_analyzer.py         # MCP server for insights
â”‚   â””â”€â”€ mcp_server_config.json   # Configuration
â”‚
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ setup_snowflake.sql      # DDL scripts
â”‚   â”œâ”€â”€ load_sample_data.py      # Sample data loader
â”‚   â””â”€â”€ run_pipeline.sh          # Full pipeline runner
â”‚
â”œâ”€â”€ docs/                        # Documentation
â”‚   â”œâ”€â”€ ARCHITECTURE.md
â”‚   â”œâ”€â”€ DBT_MODELS.md
â”‚   â””â”€â”€ DATA_LINEAGE.md
â”‚
â”œâ”€â”€ .github/workflows/
â”‚   â””â”€â”€ dbt_run.yml             # CI/CD automation
â”‚
â””â”€â”€ power_bi/
    â””â”€â”€ sales_dashboard.pbix    # BI Visualization
```

---

## ðŸ”„ Data Pipeline Stages

### Stage 1: EXTRACT (Fake Store API Connector)
Extract data from multiple sources:
- **Orders API**: Transaction data
- **Customer CRM**: Customer information
- **Product Catalog**: Product master data

**Files**: `fivetran_simulator/*.py` (`extract_customers.py`, `extract_products.py`, `extract_orders.py`) now call the Fake Store API.

```python
# Example: extract_orders.py
from fivetran_simulator import OrdersExtractor

extractor = OrdersExtractor(api_url="https://api.example.com")
orders = extractor.fetch_recent_orders()
orders.to_snowflake(table="RAW.ORDERS")
```

---

### Stage 2: LOAD (Snowflake)
Land raw data in Snowflake:
- **Schema**: `RAW`
- **Tables**: `ORDERS`, `CUSTOMERS`, `PRODUCTS`
- **Pattern**: Append/Merge for incremental loads

```sql
-- RAW Layer Structure
CREATE SCHEMA RAW;

CREATE TABLE RAW.ORDERS (
    order_id STRING,
    customer_id STRING,
    order_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    _fivetran_synced TIMESTAMP
);
```

---

### Stage 3: TRANSFORM (dbt)

#### 3a. STAGING Layer - Cleaning & Standardization
```sql
-- models/staging/stg_orders.sql
with source as (
    select * from {{ source('raw', 'orders') }}
),
cleaned as (
    select
        order_id::STRING as order_id,
        customer_id::STRING as customer_id,
        order_date::DATE as order_date,
        total_amount::DECIMAL(10,2) as total_amount,
        CASE WHEN total_amount > 0 THEN 'valid' ELSE 'invalid' END as status,
        _fivetran_synced::TIMESTAMP as loaded_at
    from source
    where _fivetran_synced >= DATEADD(day, -1, CURRENT_TIMESTAMP)
)
select * from cleaned
```

#### 3b. INTERMEDIATE Layer - Business Logic
```sql
-- models/intermediate/int_orders_enhanced.sql
with orders as (
    select * from {{ ref('stg_orders') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
),
enhanced as (
    select
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.segment,
        o.order_date,
        o.total_amount,
        DATEDIFF(day, o.order_date, CURRENT_DATE) as days_since_order
    from orders o
    left join customers c on o.customer_id = c.customer_id
)
select * from enhanced
```

#### 3c. MARTS Layer - Analytics Ready
```sql
-- models/marts/fct_sales.sql
with orders as (
    select * from {{ ref('int_orders_enhanced') }}
),
products as (
    select * from {{ ref('stg_products') }}
),
facts as (
    select
        o.order_id as sales_key,
        o.customer_id,
        p.product_id,
        o.segment,
        o.order_date,
        o.total_amount,
        p.category,
        p.price,
        o.total_amount / NULLIF(p.price, 0) as units_sold
    from orders o
    left join products p on o.product_id = p.product_id
)
select * from facts
```

---

### Stage 4: TEST (Data Quality)
```sql
-- tests/assert_positive_revenue.sql
select count(*) as failure_count
from {{ ref('fct_sales') }}
where total_amount <= 0
having count(*) > 0
```

```bash
dbt test  # Run all tests
```

---

### Stage 5: ANALYTICS (Power BI)
Connect Power BI to Snowflake MARTS schema:
- **fct_sales**: Sales transactions
- **dim_customer**: Customer dimensions
- **dim_product**: Product dimensions
- **dim_date**: Date dimension

**Dashboards**:
- ðŸ“ˆ Sales Overview
- ðŸ’° Revenue Trends
- ðŸ‘¥ Customer Segmentation
- ðŸŽ¯ Product Performance

---

### Stage 6: AI INSIGHTS (MCP + Gemini CLI)
Automated data analysis and pattern detection:

```bash
gemini-cli --mcp data_analyzer \
  --query "Analyze sales trends and identify top customers"
```

---

## ðŸ§ª Testing & Quality

### dbt Tests
```bash
# Run all dbt tests
dbt test

# Run tests for specific model
dbt test --select fct_sales

# Test with detailed output
dbt test --debug
```

### Python Tests
```bash
# Run pytest suite
pytest tests/ -v --cov

# Run specific test
pytest tests/test_extraction.py -v
```

---

## ðŸ“Š Performance Optimization

### dbt Materializations
- **View**: Staging layer (not materialized)
- **Table**: Intermediate layer (materialized)
- **Incremental**: Marts (append new rows only)

### Snowflake Optimization
- Clustering keys on join columns
- Partitioning by date
- Statistics for query optimization

```sql
-- Clustered Incremental Table
{{ config(
    materialized='incremental',
    unique_key='sales_key',
    cluster_by=['order_date', 'customer_id']
) }}
```

---

## ðŸ” Security & Governance

âœ… **Version Control**: All code in GitHub  
âœ… **Access Control**: Row-level security via dbt  
âœ… **Data Lineage**: dbt provides full lineage  
âœ… **Audit Trail**: Fivetran tracks data freshness  
âœ… **Testing**: Automated data quality checks  

---

## ðŸš€ Deployment

### Local Development
```bash
dbt run --target dev
```

### Production
```bash
dbt run --target prod
```

### CI/CD (GitHub Actions)
Push to GitHub â†’ Automatic dbt testing â†’ Approval â†’ Deploy to production

See `.github/workflows/dbt_run.yml`

---

## ðŸ“š Documentation

- **ARCHITECTURE.md**: System design & decisions
- **DBT_MODELS.md**: Data model documentation
- **DATA_LINEAGE.md**: End-to-end data flow

Generate dbt docs:
```bash
cd dbt_project
dbt docs generate
dbt docs serve
```

---

## ðŸ› ï¸ Common Commands

```bash
# Development
dbt run                    # Execute all models
dbt test                   # Run data quality tests
dbt debug                  # Test Snowflake connection
dbt deps                   # Install dbt packages

# Documentation
dbt docs generate          # Generate interactive docs
dbt docs serve             # View docs locally

# Testing & Quality
dbt test --select model_name
pytest tests/ -v --cov

# Maintenance
dbt snapshot               # Create data snapshots
dbt freshness             # Check source freshness

# Pipeline
python scripts/loadsampledata.py   # Load test data
bash scripts/run_pipeline.sh         # Run full pipeline
```

---

## ðŸ’¡ Key Features

âœ… **Production-Ready**: Error handling, logging  
âœ… **Scalable**: Easy to add new sources  
âœ… **Tested**: dbt tests + Python tests  
âœ… **Documented**: Clear lineage & docs  
âœ… **CI/CD**: GitHub Actions automation  
âœ… **Modular**: Staging â†’ Intermediate â†’ Marts  
âœ… **Portfolio-Quality**: Professional structure  

---

## ðŸŽ“ Learning Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [Snowflake University](https://university.snowflake.com/)
- [Modern Data Stack Overview](https://www.moderndatastack.xyz/)
- [Data Engineering Best Practices](https://www.dataengineeringwiki.com/)

---

## ðŸ“ž Support

- Issues: GitHub Issues
- Questions: Check discussions
- Improvements: Pull requests welcome!

---

## ðŸ“„ License

MIT License - Feel free to use for portfolio purposes

---

## ðŸŽ¯ Next Steps

1. âœ… Clone repository
2. âœ… Setup Snowflake connection
3. âœ… Run `dbt run` and `dbt test`
4. âœ… Connect Power BI dashboard
5. âœ… Explore dbt docs
6. âœ… Create GitHub repo for your portfolio
7. âœ… Share with potential employers!

**Happy data engineering! ðŸš€**

