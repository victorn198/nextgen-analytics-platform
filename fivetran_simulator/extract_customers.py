from fivetran_simulator.online_retail import customer_rows
from pipeline_runtime.postgres import connect_postgres_from_env, run_full_refresh
from dotenv import load_dotenv

import os

load_dotenv()
INSERT_BATCH_SIZE = int(os.getenv("RETAIL_INSERT_BATCH_SIZE", "5000"))


def load_customers(conn):
    """
    Loads customers derived from the canonical UCI Online Retail transaction set.
    Incremental behavior: inserts only missing customer IDs.
    """
    rows = customer_rows()
    cur = conn.cursor()
    try:
        cur.execute("SELECT customer_id FROM raw.customers_raw")
        existing_ids = {row[0] for row in cur.fetchall()}
        rows_to_insert = [row for row in rows if row[0] not in existing_ids]
        if not rows_to_insert:
            print(f"Customers already up-to-date (rows={len(existing_ids)}).")
            return

        print(
            f"Loading {len(rows_to_insert)} customers from canonical Online Retail transactions..."
        )
        for start in range(0, len(rows_to_insert), INSERT_BATCH_SIZE):
            batch = rows_to_insert[start : start + INSERT_BATCH_SIZE]
            cur.executemany(
                "INSERT INTO raw.customers_raw (customer_id, customer_name, email, city, state, created_date) VALUES (%s, %s, %s, %s, %s, %s)",
                batch,
            )
        conn.commit()
        print("Customers loaded successfully.")
    finally:
        cur.close()


if __name__ == "__main__":
    conn = connect_postgres_from_env()

    try:
        run_full_refresh(conn, ("raw", "customers_raw"), load_customers, "customers")
    finally:
        conn.close()
        print("PostgreSQL connection closed.")
