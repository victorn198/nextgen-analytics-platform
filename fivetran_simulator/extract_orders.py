import os
import random
from datetime import datetime, timedelta

import snowflake.connector
from dotenv import load_dotenv


def load_orders(conn):
    """
    Generates and loads 1000 sample orders into the RAW.orders_raw table.
    """
    cur = conn.cursor()
    try:
        print("🛒 Generating and loading 1000 orders...")
        customer_ids = [f"CUST_{i:04d}" for i in range(1, 501)]
        product_ids = [f"PROD_{i:04d}" for i in range(1, 101)]
        base_date = datetime(2025, 1, 1)
        orders_data = []
        for i in range(1000):
            quantity = random.randint(1, 5)
            unit_price = 99.99
            orders_data.append(
                (
                    f"ORD_{i + 1:06d}",
                    random.choice(customer_ids),
                    random.choice(product_ids),
                    base_date + timedelta(days=random.randint(0, 365)),
                    quantity,
                    unit_price,
                    round(quantity * unit_price, 2),
                    random.choice(["completed", "pending", "cancelled"]),
                )
            )

        cur.executemany(
            "INSERT INTO RAW.orders_raw (order_id, customer_id, product_id, order_date, quantity, unit_price, total_amount, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            orders_data,
        )
        conn.commit()
        print("✅ Orders loaded successfully.")
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
        print("🧹 Cleaning old order data...")
        cursor.execute("DELETE FROM RAW.ORDERS_RAW;")
        conn.commit()
        cursor.close()

        load_orders(conn)

        # Verification
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM RAW.orders_raw")
        print(f"   - Verification: {cursor.fetchone()[0]} orders in the table.")
        cursor.close()

    finally:
        conn.close()
        print("Snowflake connection closed.")
