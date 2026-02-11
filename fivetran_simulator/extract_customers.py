import os
import random
from datetime import datetime

import snowflake.connector
from dotenv import load_dotenv


def load_customers(conn):
    """
    Generates and loads 500 sample customers into the RAW.customers_raw table.
    """
    cur = conn.cursor()
    try:
        print("👥 Generating and loading 500 customers...")
        customers_data = []
        for i in range(1, 501):
            customers_data.append(
                (
                    f"CUST_{i:04d}",
                    f"Customer {i}",
                    f"customer{i}@example.com",
                    random.choice(["SP", "RJ", "BH", "POA", "CUR"]),
                    random.choice(["SP", "RJ", "MG", "RS", "PR"]),
                    datetime.now(),
                )
            )

        cur.executemany(
            "INSERT INTO RAW.customers_raw (customer_id, customer_name, email, city, state, created_date) VALUES (%s, %s, %s, %s, %s, %s)",
            customers_data,
        )
        conn.commit()
        print("✅ Customers loaded successfully.")
    finally:
        cur.close()


if __name__ == "__main__":
    load_dotenv()

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    try:
        # For standalone execution, clear the table first
        cursor = conn.cursor()
        print("🧹 Cleaning old customer data...")
        cursor.execute("DELETE FROM RAW.CUSTOMERS_RAW;")
        conn.commit()
        cursor.close()

        load_customers(conn)

        # Verification
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM RAW.customers_raw")
        print(f"   - Verification: {cursor.fetchone()[0]} customers in the table.")
        cursor.close()

    finally:
        conn.close()
        print("Snowflake connection closed.")
