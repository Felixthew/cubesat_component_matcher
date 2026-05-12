import os
from functools import lru_cache
from sqlalchemy import create_engine, text, bindparam, Engine

DEFAULT_DB_URL = "postgresql://felix:postgres@localhost:5432/cubesat"

class Database:
    BLACKLIST_SCHEMA = {
        "information_schema",
        "pg_catalog",
        "pg_toast",
        "public"
    }

    def __init__(self, engine: Engine):
        self.db_engine = engine
        # per-instance dtype cache, populated by data_loader.get_dtypes.
        # scoped to the Database so swapping in a test db doesn't share entries with prod.
        self.dtype_cache: dict[tuple[str, str], dict[str, str]] = {}

    def execute(self, sql_str: str, params: dict = None, expanding: list[str] = None):
        """
        Executes raw SQL queries with the given database
        :param sql_str: string query
        :param params: SQL parameters to inject
        :param expanding: names of params that should bind as expanding collections.
            Required for IN-clauses fed a list/tuple — without this SQLAlchemy will not
            expand them and the query will fail or behave unexpectedly across drivers.
        :return: Result object if the query returns a table, otherwise just the row count after performing the operation
        """
        params = params or {}
        stmt = text(sql_str)
        if expanding:
            stmt = stmt.bindparams(*[bindparam(name, expanding=True) for name in expanding])
        with self.db_engine.begin() as conn:
            result = conn.execute(stmt, params)
            if result.returns_rows:
                return result.all()
            else:
                return result.rowcount


@lru_cache(maxsize=1)
def _default_db() -> Database:
    url = os.getenv("DB_URL", DEFAULT_DB_URL)
    return Database(create_engine(url))


def get_db() -> Database:
    """FastAPI dependency returning the process-wide default Database.
    Tests can swap the live db by setting app.dependency_overrides[get_db]."""
    return _default_db()
