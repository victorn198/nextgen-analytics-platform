import os
import time
from datetime import datetime, timedelta
from random import Random

import requests
import snowflake.connector
from dotenv import load_dotenv

API_BASE_URL = os.getenv("FAKESTORE_API_BASE_URL", "https://fakestoreapi.com")
API_TIMEOUT_SECONDS = int(os.getenv("FAKESTORE_TIMEOUT_SECONDS", "20"))
API_MAX_RETRIES = int(os.getenv("FAKESTORE_MAX_RETRIES", "3"))
ORDER_STATUSES = ["pending", "paid", "cancelled", "shipped", "completed"]
TARGET_ORDER_LINES = int(os.getenv("FAKESTORE_TARGET_ORDER_LINES", "100000"))
INSERT_BATCH_SIZE = int(os.getenv("FAKESTORE_INSERT_BATCH_SIZE", "5000"))
RANDOM_SEED = int(os.getenv("FAKESTORE_RANDOM_SEED", "42"))


def _fetch_json(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    last_error = None

    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise ValueError(
                    f"Unexpected payload format for {endpoint} (expected list)."
                )
            return payload
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < API_MAX_RETRIES:
                time.sleep(attempt)

    raise RuntimeError(f"Failed to fetch {endpoint} from Fake Store API: {last_error}")


def load_orders(conn):
    """
    Fetches carts from Fake Store API and scales order lines into RAW.ORDERS_RAW.
    Incremental behavior: inserts only missing order IDs up to target volume.
    """
    carts = _fetch_json("/carts")
    if not carts:
        raise RuntimeError("Carts endpoint returned no records.")

    cur = conn.cursor()
    cur.execute("SELECT CUSTOMER_ID FROM RAW.CUSTOMERS_RAW ORDER BY CUSTOMER_ID")
    customer_ids = [row[0] for row in cur.fetchall()]
    cur.execute(
        "SELECT PRODUCT_ID, UNIT_PRICE FROM RAW.PRODUCTS_RAW ORDER BY PRODUCT_ID"
    )
    product_rows = cur.fetchall()
    cur.close()

    if not customer_ids:
        raise RuntimeError("RAW.CUSTOMERS_RAW is empty before loading orders.")
    if not product_rows:
        raise RuntimeError("RAW.PRODUCTS_RAW is empty before loading orders.")

    product_ids = [row[0] for row in product_rows]
    product_prices = {row[0]: float(row[1]) for row in product_rows}
    rng = Random(RANDOM_SEED + 13)
    target_order_lines = max(
        sum(len(c.get("products", [])) for c in carts), TARGET_ORDER_LINES
    )
    base_start_date = datetime.utcnow() - timedelta(days=730)

    seed_quantities = []
    for cart in carts:
        for item in cart.get("products", []):
            quantity = int(item.get("quantity", 1) or 1)
            seed_quantities.append(max(1, quantity))
    if not seed_quantities:
        seed_quantities = [1, 2, 3]

    orders_data = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM RAW.ORDERS_RAW")
        existing_orders = int(cur.fetchone()[0] or 0)
        cur.execute(
            "SELECT COALESCE(MAX(TO_NUMBER(REGEXP_SUBSTR(ORDER_ID, '[0-9]+$'))), 0) FROM RAW.ORDERS_RAW"
        )
        max_order_number = int(cur.fetchone()[0] or 0)
        start_index = max_order_number

        if start_index >= target_order_lines:
            print(
                f"Orders already up-to-date (rows={existing_orders}, max_id={max_order_number}, target={target_order_lines}). No new records inserted."
            )
            return

        new_orders = target_order_lines - start_index
        print(
            f"Loading {new_orders} new orders from API templates (rows={existing_orders}, max_id={max_order_number}, target={target_order_lines})..."
        )

        for i in range(start_index, target_order_lines):
            customer_id = customer_ids[rng.randrange(len(customer_ids))]
            product_id = product_ids[rng.randrange(len(product_ids))]
            unit_price = product_prices[product_id]
            quantity_template = seed_quantities[i % len(seed_quantities)]
            quantity = max(1, quantity_template + rng.randint(-1, 3))
            order_date = base_start_date + timedelta(
                days=rng.randint(0, 730),
                minutes=rng.randint(0, 1439),
                seconds=rng.randint(0, 59),
            )
            status = ORDER_STATUSES[rng.randrange(len(ORDER_STATUSES))]

            orders_data.append(
                (
                    f"ORD_{i + 1:09d}",
                    customer_id,
                    product_id,
                    order_date,
                    quantity,
                    unit_price,
                    round(quantity * unit_price, 2),
                    status,
                )
            )

            if len(orders_data) >= INSERT_BATCH_SIZE:
                cur.executemany(
                    "INSERT INTO RAW.orders_raw (order_id, customer_id, product_id, order_date, quantity, unit_price, total_amount, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    orders_data,
                )
                orders_data.clear()

        if orders_data:
            cur.executemany(
                "INSERT INTO RAW.orders_raw (order_id, customer_id, product_id, order_date, quantity, unit_price, total_amount, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                orders_data,
            )
        conn.commit()
        print("Orders loaded successfully.")
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM RAW.ORDERS_RAW;")
        conn.commit()
        cursor.close()

        load_orders(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM RAW.orders_raw")
        print(f"Verification: {cursor.fetchone()[0]} orders in table.")
        cursor.close()
    finally:
        conn.close()
        print("Snowflake connection closed.")
