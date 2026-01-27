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

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

-   Python 3.8+
-   `pip` (Python package installer)
-   dbt CLI (installed via pip, `dbt-snowflake` adapter)
-   Snowflake account with necessary permissions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/data-pipeline-portfolio.git
cd data-pipeline-portfolio
```

### 2. Set up Python environment and install dependencies

It's recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Snowflake Credentials

#### For `loadsampledata.py` script:

Create a `.env` file in the root of the project based on `.env.example`. This file will store your Snowflake connection details for the Python script that loads sample data.

```
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_WAREHOUSE=your_snowflake_warehouse
SNOWFLAKE_DATABASE=your_snowflake_database
SNOWFLAKE_SCHEMA=your_snowflake_schema
```

**Note:** The `.env` file should not be committed to version control.

#### For dbt:

Configure your dbt `profiles.yml` file. By default, this project looks for a profile named `data_pipeline`. Your `profiles.yml` should typically be located at `~/.dbt/profiles.yml` (on Linux/macOS) or `%userprofile%\.dbt\profiles.yml` (on Windows).

Example `profiles.yml` entry:

```yaml
data_pipeline:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}" # Use environment variable
      user: "{{ env_var('SNOWFLAKE_USER') }}"       # Use environment variable
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}" # Use environment variable
      role: your_snowflake_role
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}" # Use environment variable
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}" # Use environment variable
      schema: "{{ env_var('SNOWFLAKE_SCHEMA') }}" # Use environment variable
      threads: 4
      client_session_keep_alive: False
```

It's highly recommended to use environment variables for dbt credentials as well, by setting them in your shell or loading them from the `.env` file if your dbt execution environment supports it (e.g., via a wrapper script).

### 4. Load Sample Data

Run the Python script to populate your `RAW` schema in Snowflake with sample data.

```bash
python scripts/loadsampledata.py
```

### 5. Run dbt transformations

Navigate to the `dbtproject` directory and run your dbt models.

```bash
cd dbtproject
dbt deps
dbt seed # If you have seed files (not currently in this project, but good practice)
dbt run
dbt test
dbt docs generate
dbt docs serve # To view the generated documentation
```

## Skills Demonstrated

- Data Warehouse Design and Dimensional Modeling (Kimball).
- dbt ELT Best Practices and Performance Optimization.
- Advanced SQL for transformation logic and complex aggregations.
- Data Quality Management and Validation.
- Git version control and CICD implementation for the dbt layer.

---

Victor Nogueira | Data Engineer | Sao Paulo, BR