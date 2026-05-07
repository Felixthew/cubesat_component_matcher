import os
from sqlalchemy import create_engine, text, bindparam, Engine

DB_URL = os.getenv("DB_URL", "postgresql://felix:postgres@localhost:5432/cubesat")
db_engine = create_engine(DB_URL)

class Database:
    def __init__(self, engine: Engine):
        self.db_engine = engine

    BLACKLIST_SCHEMA = {
        "information_schema",
        "pg_catalog",
        "pg_toast",
        "public"
    }

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

db = Database(db_engine)