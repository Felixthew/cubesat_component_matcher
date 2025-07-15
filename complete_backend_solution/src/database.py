import os
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", "postgresql://postgres:YKOFNCLsAncBgawWEMQJfnuljPaaWXot@turntable.proxy.rlwy.net:46609/railway")
db_engine = create_engine(DB_URL)

class Database:
    def __init__(self, engine):
        self.db_engine = engine

    BLACKLIST_SCHEMA = {
        "information_schema",
        "pg_catalog",
        "public"
    }

    def execute(self, sql_str: str, params: dict = None):
        """
        Executes Core SQL queries with the given database
        :param sql_str: string query
        :param params: SQL parameters to inject
        :return: Result object if the query returns a table, otherwise just the row count after performing the operation
        """
        params = params or {}
        with self.db_engine.begin() as conn:
            result = conn.execute(text(sql_str), params)

            if result.returns_rows:
                return result.fetchall()
            else:
                return result.rowcount

db = Database(db_engine)