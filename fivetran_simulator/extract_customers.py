import os
from datetime import datetime, timedelta
from random import Random

import psycopg2
from dotenv import load_dotenv

load_dotenv()

TARGET_CUSTOMERS = int(os.getenv("FAKESTORE_TARGET_CUSTOMERS", "10000"))
INSERT_BATCH_SIZE = int(os.getenv("FAKESTORE_INSERT_BATCH_SIZE", "5000"))
RANDOM_SEED = int(os.getenv("FAKESTORE_RANDOM_SEED", "42"))


def _fetch_users():
    """
    Mocks the FakeStoreAPI users endpoint since it is frequently down.
    Returns a large list of templates that the load_customers function scales.
    """
    templates = []
    firsts = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    lasts = ["Smith", "Doe", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego"]
    
    for i in range(50):
        templates.append({
            "name": {
                "firstname": firsts[i % len(firsts)],
                "lastname": lasts[i % len(lasts)]
            },
            "address": {
                "city": cities[i % len(cities)],
                "zipcode": f"{(10000 + i*17) % 99999:05d}"
            }
        })
    return templates


def load_customers(conn):
    """
    Generates customer rows from local templates and scales them into
    raw.customers_raw.
    Incremental behavior: inserts only missing customer IDs.
    """
    users = _fetch_users()
    if not users:
        raise RuntimeError("Users endpoint returned no records.")

    target_customers = max(len(users), TARGET_CUSTOMERS)
    rng = Random(RANDOM_SEED)
    now_utc = datetime.utcnow()
    customers_data = []

    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM raw.customers_raw")
        existing_customers = int(cur.fetchone()[0] or 0)
        cur.execute(
            "SELECT COALESCE(MAX(CAST(NULLIF(REGEXP_REPLACE(customer_id, '\\D', '', 'g'), '') AS BIGINT)), 0) FROM raw.customers_raw"
        )
        max_customer_number = int(cur.fetchone()[0] or 0)
        start_index = max_customer_number

        if start_index >= target_customers:
            print(
                f"Customers already up-to-date (rows={existing_customers}, max_id={max_customer_number}, target={target_customers}). No new records inserted."
            )
            return

        new_customers = target_customers - start_index
        print(
            f"Loading {new_customers} new customers from API templates (rows={existing_customers}, max_id={max_customer_number}, target={target_customers})..."
        )

        for i in range(start_index, target_customers):
            template = users[i % len(users)]
            name = template.get("name", {})
            first_name = str(name.get("firstname", "")).strip() or "customer"
            last_name = str(name.get("lastname", "")).strip() or "template"
            customer_number = i + 1
            address = template.get("address", {})
            city = str(address.get("city", "")).strip() or "unknown_city"
            zipcode = str(address.get("zipcode", "")).strip() or "00000"
            created_date = now_utc - timedelta(days=rng.randint(0, 3650))

            customers_data.append(
                (
                    f"CUST_{customer_number:06d}",
                    f"{first_name.title()} {last_name.title()} {customer_number}",
                    f"{first_name.lower()}.{last_name.lower()}.{customer_number}@portfolio-company.com",
                    city,
                    zipcode,
                    created_date,
                )
            )

            if len(customers_data) >= INSERT_BATCH_SIZE:
                cur.executemany(
                    "INSERT INTO raw.customers_raw (customer_id, customer_name, email, city, state, created_date) VALUES (%s, %s, %s, %s, %s, %s)",
                    customers_data,
                )
                customers_data.clear()

        if customers_data:
            cur.executemany(
                "INSERT INTO raw.customers_raw (customer_id, customer_name, email, city, state, created_date) VALUES (%s, %s, %s, %s, %s, %s)",
                customers_data,
            )
        conn.commit()
        print("Customers loaded successfully.")
    finally:
        cur.close()


if __name__ == "__main__":
    load_dotenv()

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "analytics"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM raw.customers_raw;")
        conn.commit()
        cursor.close()

        load_customers(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM raw.customers_raw")
        print(f"Verification: {cursor.fetchone()[0]} customers in table.")
        cursor.close()
    finally:
        conn.close()
        print("PostgreSQL connection closed.")
