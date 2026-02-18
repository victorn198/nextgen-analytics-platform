import os
import sys
import argparse
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

# Ensure local package imports work when running from scripts/ path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fivetran_simulator.extract_customers import load_customers
from fivetran_simulator.extract_orders import load_orders
from fivetran_simulator.extract_products import load_products


def _ensure_raw_tables(cur):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS RAW.customers_raw (customer_id STRING, customer_name STRING, email STRING, city STRING, state STRING, created_date TIMESTAMP)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS RAW.products_raw (product_id STRING, product_name STRING, category STRING, unit_price FLOAT, stock_quantity INT)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS RAW.orders_raw (order_id STRING, customer_id STRING, product_id STRING, order_date TIMESTAMP, quantity INT, unit_price FLOAT, total_amount FLOAT, status STRING)"
    )


def _truncate_raw_tables(cur):
    cur.execute("TRUNCATE TABLE RAW.orders_raw")
    cur.execute("TRUNCATE TABLE RAW.products_raw")
    cur.execute("TRUNCATE TABLE RAW.customers_raw")


def _resolve_mode(explicit_mode):
    if explicit_mode:
        return explicit_mode
    return os.getenv("PIPELINE_LOAD_MODE", "incremental").strip().lower()


def main():
    """
    Orchestrates RAW load:
    - Connect to Snowflake
    - Ensure RAW tables exist
    - Optionally truncate RAW tables (full refresh mode)
    - Fetch data from Fake Store API and load into RAW (incremental by default)
    - Verify final counts
    """
    parser = argparse.ArgumentParser(description="Load Fake Store data into Snowflake RAW")
    parser.add_argument(
        "--mode",
        choices=["incremental", "full_refresh"],
        default=None,
        help="Load mode. Defaults to PIPELINE_LOAD_MODE env var or incremental.",
    )
    args = parser.parse_args()

    load_dotenv()
    load_mode = _resolve_mode(args.mode)
    if load_mode not in {"incremental", "full_refresh"}:
        raise ValueError(
            "Invalid load mode. Use 'incremental' or 'full_refresh' via --mode or PIPELINE_LOAD_MODE."
        )

    print(f"Starting API-based load into Snowflake RAW schema (mode={load_mode})...")

    conn = None
    try:
        conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )
        print("Snowflake connection successful.")

        cur = conn.cursor()
        _ensure_raw_tables(cur)
        conn.commit()

        if load_mode == "full_refresh":
            print("Applying full refresh: truncating RAW tables...")
            _truncate_raw_tables(cur)
            conn.commit()
            print("RAW tables truncated.")
        else:
            print("Incremental mode: keeping existing RAW data.")

        cur.close()
        print("RAW tables ready for load.")

        print("Loading data from Fake Store API...")
        load_customers(conn)
        load_products(conn)
        load_orders(conn)

        print("Verifying final counts...")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM RAW.customers_raw")
        print(f"Customers: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM RAW.products_raw")
        print(f"Products: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM RAW.orders_raw")
        print(f"Orders: {cur.fetchone()[0]}")
        cur.close()

        print("Load complete. RAW data is ready for dbt.")

    except Exception as exc:
        print(f"Load failed: {exc}")
        raise
    finally:
        if conn:
            conn.close()
            print("Snowflake connection closed.")


if __name__ == "__main__":
    main()
