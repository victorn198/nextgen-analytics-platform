import os

import snowflake.connector
from dotenv import load_dotenv

# Import the modularized loading functions
from fivetran_simulator.extract_customers import load_customers
from fivetran_simulator.extract_orders import load_orders
from fivetran_simulator.extract_products import load_products

def main():
    """
    Main function to orchestrate the data loading process.
    - Connects to Snowflake.
    - Cleans old data.
    - Creates tables.
    - Loads new data using modular functions.
    - Verifies the loaded data.
    """
    load_dotenv()
    print("🚀 Starting full sample data load into Snowflake RAW schema...")

    conn = None  # Initialize conn to None
    try:
        conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )
        print("✅ Snowflake connection successful.")

        cur = conn.cursor()

        # 1. Clean old data
        print("\n🧹 Cleaning old data from RAW tables...")
        cur.execute("DELETE FROM RAW.CUSTOMERS_RAW;")
        cur.execute("DELETE FROM RAW.PRODUCTS_RAW;")
        cur.execute("DELETE FROM RAW.ORDERS_RAW;")
        conn.commit()
        print("✅ Old data cleaned successfully.")

        # 2. (Optional but good practice) Re-create tables to ensure schema is correct
        print("\n📋 Re-creating RAW tables for a clean slate...")
        cur.execute(
            "CREATE OR REPLACE TABLE RAW.customers_raw (customer_id STRING, customer_name STRING, email STRING, city STRING, state STRING, created_date TIMESTAMP)"
        )
        cur.execute(
            "CREATE OR REPLACE TABLE RAW.products_raw (product_id STRING, product_name STRING, category STRING, unit_price FLOAT, stock_quantity INT)"
        )
        cur.execute(
            "CREATE OR REPLACE TABLE RAW.orders_raw (order_id STRING, customer_id STRING, product_id STRING, order_date TIMESTAMP, quantity INT, unit_price FLOAT, total_amount FLOAT, status STRING)"
        )
        conn.commit()
        print("✅ Tables re-created successfully.")

        cur.close()

        # 3. Load new data using modular functions
        print("\n🚛 Loading new sample data...")
        load_customers(conn)
        load_products(conn)
        load_orders(conn)

        # 4. Final verification
        print("\n🔍 Verifying final counts...")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM RAW.customers_raw")
        print(f"   - Customers: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM RAW.products_raw")
        print(f"   - Products: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM RAW.orders_raw")
        print(f"   - Orders: {cur.fetchone()[0]}")
        cur.close()

        print("\n🎉 LOAD COMPLETE! RAW data is ready for dbt! 🎉")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("\nSnowflake connection closed.")

            conn.close()
            print("\nSnowflake connection closed.")

if __name__ == "__main__":
    main()
