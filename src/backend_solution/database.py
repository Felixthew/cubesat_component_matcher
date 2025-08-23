import os
from sqlalchemy import create_engine, text, Engine, Row, Sequence

# DB_URL = os.getenv("DB_URL", "postgresql://postgres:YKOFNCLsAncBgawWEMQJfnuljPaaWXot@turntable.proxy.rlwy.net:46609/railway")
DB_URL = os.getenv("DB_URL", "postgresql://felixwatt@localhost:5432/testdb")
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

    def execute(self, sql_str: str, params: dict = None):
        """
        Executes raw SQL queries with the given database
        :param sql_str: string query
        :param params: SQL parameters to inject
        :return: Result object if the query returns a table, otherwise just the row count after performing the operation
        """
        params = params or {}
        with self.db_engine.begin() as conn:
            result = conn.execute(text(sql_str), params)
            if result.returns_rows:
                return result.all()
            else:
                return result.rowcount

db = Database(db_engine)