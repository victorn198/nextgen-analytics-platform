from pipeline_runtime import postgres


def test_connect_postgres_uses_project_environment(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return "connection"

    monkeypatch.setenv("POSTGRES_HOST", "db.internal")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    monkeypatch.setenv("POSTGRES_DB", "warehouse")
    monkeypatch.setenv("POSTGRES_USER", "analytics")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setattr(postgres.psycopg2, "connect", fake_connect)

    assert postgres.connect_postgres_from_env() == "connection"
    assert captured == {
        "host": "db.internal",
        "port": 6543,
        "dbname": "warehouse",
        "user": "analytics",
        "password": "secret",
    }


def test_run_full_refresh_resets_loads_and_counts() -> None:
    queries: list[object] = []
    loaded: list[str] = []

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def execute(self, query) -> None:
            queries.append(query)

        def fetchone(self):
            return (12,)

    class Connection:
        def __init__(self) -> None:
            self.commits = 0

        def cursor(self):
            return Cursor()

        def commit(self) -> None:
            self.commits += 1

    connection = Connection()
    count = postgres.run_full_refresh(
        connection,
        ("raw", "orders_raw"),
        lambda _conn: loaded.append("orders"),
        "order lines",
    )

    assert count == 12
    assert connection.commits == 1
    assert loaded == ["orders"]
    assert len(queries) == 2
