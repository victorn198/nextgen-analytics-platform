from __future__ import annotations

from collections.abc import Callable
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql


def connect_postgres_from_env():
    """Open the project PostgreSQL connection using the documented environment variables."""
    load_dotenv()
    return psycopg2.connect(
        host=_env("POSTGRES_HOST", "localhost"),
        port=int(_env("POSTGRES_PORT", "5432")),
        dbname=_env("POSTGRES_DB", "analytics"),
        user=_env("POSTGRES_USER", "postgres"),
        password=_env("POSTGRES_PASSWORD", "postgres"),
    )


def run_full_refresh(
    conn: Any,
    relation: tuple[str, str],
    load_rows: Callable[[Any], None],
    label: str,
) -> int:
    """Reset one RAW relation, invoke its loader, and return the verified row count."""
    schema, table = relation
    relation_sql = sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(table))
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("DELETE FROM {}").format(relation_sql))
        conn.commit()

    load_rows(conn)

    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(relation_sql))
        count = int(cursor.fetchone()[0])
    print(f"Verification: {count} {label} in table.")
    return count


def _env(name: str, default: str) -> str:
    import os

    return os.getenv(name, default)
