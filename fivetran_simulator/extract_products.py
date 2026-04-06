import os
from random import Random

import psycopg2
from dotenv import load_dotenv

load_dotenv()

TARGET_PRODUCTS = int(os.getenv("FAKESTORE_TARGET_PRODUCTS", "2000"))
INSERT_BATCH_SIZE = int(os.getenv("FAKESTORE_INSERT_BATCH_SIZE", "5000"))
RANDOM_SEED = int(os.getenv("FAKESTORE_RANDOM_SEED", "42"))


def _fetch_products():
    """
    Mocks the FakeStoreAPI products endpoint.
    Returns templates that the load_products function scales.
    """
    templates = []
    categories = ["electronics", "jewelery", "men's clothing", "women's clothing", "home goods"]
    titles = ["Widget", "Gadget", "Thingamajig", "Doohickey", "Contraption", "Apparatus", "Device", "Module"]
    
    for i in range(50):
        templates.append({
            "title": f"{titles[i % len(titles)]} {i}",
            "price": 10.0 + (i * 2.5) % 100,
            "category": categories[i % len(categories)],
            "rating": {
                "count": 50 + i * 10
            }
        })
    return templates


def load_products(conn):
    """
    Generates product rows from local templates and scales them into
    raw.products_raw.
    Incremental behavior: inserts only missing product IDs.
    """
    products = _fetch_products()
    if not products:
        raise RuntimeError("Products endpoint returned no records.")

    target_products = max(len(products), TARGET_PRODUCTS)
    rng = Random(RANDOM_SEED + 7)
    products_data = []

    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM raw.products_raw")
        existing_products = int(cur.fetchone()[0] or 0)
        cur.execute(
            "SELECT COALESCE(MAX(CAST(NULLIF(REGEXP_REPLACE(product_id, '\\D', '', 'g'), '') AS BIGINT)), 0) FROM raw.products_raw"
        )
        max_product_number = int(cur.fetchone()[0] or 0)
        start_index = max_product_number

        if start_index >= target_products:
            print(
                f"Products already up-to-date (rows={existing_products}, max_id={max_product_number}, target={target_products}). No new records inserted."
            )
            return

        new_products = target_products - start_index
        print(
            f"Loading {new_products} new products from API templates (rows={existing_products}, max_id={max_product_number}, target={target_products})..."
        )

        for i in range(start_index, target_products):
            template = products[i % len(products)]
            product_number = i + 1
            rating = template.get("rating", {})
            base_stock = int(rating.get("count", 0) or 0)
            base_price = round(float(template.get("price", 10.0) or 10.0), 2)
            price_multiplier = 0.85 + (rng.random() * 0.5)
            unit_price = round(max(1.0, base_price * price_multiplier), 2)
            stock_quantity = max(0, base_stock + rng.randint(0, 250))

            products_data.append(
                (
                    f"PROD_{product_number:06d}",
                    f"{str(template.get('title', 'Product')).strip()} | SKU-{product_number:06d}",
                    str(template.get("category", "uncategorized")),
                    unit_price,
                    stock_quantity,
                )
            )

            if len(products_data) >= INSERT_BATCH_SIZE:
                cur.executemany(
                    "INSERT INTO raw.products_raw (product_id, product_name, category, unit_price, stock_quantity) VALUES (%s, %s, %s, %s, %s)",
                    products_data,
                )
                products_data.clear()

        if products_data:
            cur.executemany(
                "INSERT INTO raw.products_raw (product_id, product_name, category, unit_price, stock_quantity) VALUES (%s, %s, %s, %s, %s)",
                products_data,
            )
        conn.commit()
        print("Products loaded successfully.")
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
        cursor.execute("DELETE FROM raw.products_raw;")
        conn.commit()
        cursor.close()

        load_products(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM raw.products_raw")
        print(f"Verification: {cursor.fetchone()[0]} products in table.")
        cursor.close()
    finally:
        conn.close()
        print("PostgreSQL connection closed.")
