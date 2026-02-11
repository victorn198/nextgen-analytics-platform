import os
import random

import snowflake.connector
from dotenv import load_dotenv


def load_products(conn):
    """
    Generates and loads 100 sample products into the RAW.products_raw table.
    """
    cur = conn.cursor()
    try:
        print("📦 Generating and loading 100 products...")
        products_data = []
        for i in range(1, 101):
            products_data.append(
                (
                    f"PROD_{i:04d}",
                    f"Product {i}",
                    random.choice(["Electronics", "Apparel", "Home Goods"]),
                    round(random.uniform(10.0, 500.0), 2),
                    random.randint(0, 100),
                )
            )

        cur.executemany(
            "INSERT INTO RAW.products_raw (product_id, product_name, category, unit_price, stock_quantity) VALUES (%s, %s, %s, %s, %s)",
            products_data,
        )
        conn.commit()
        print("✅ Products loaded successfully.")
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
        print("🧹 Cleaning old product data...")
        cursor.execute("DELETE FROM RAW.PRODUCTS_RAW;")
        conn.commit()
        cursor.close()

        load_products(conn)

        # Verification
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM RAW.products_raw")
        print(f"   - Verification: {cursor.fetchone()[0]} products in the table.")
        cursor.close()

    finally:
        conn.close()
        print("Snowflake connection closed.")
