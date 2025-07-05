import os
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", "postgresql://postgres:PzcglEfINUtMgDzqZAtEhvVexsfWIrZT@switchyard.proxy.rlwy.net:12039/railway")
db_engine = create_engine(DB_URL)

class Database:
    def __init__(self, engine):
        self.db_engine = engine

    def execute(self, sql_str: str, params: dict = None):
        params = params or {}
        with self.db_engine.begin() as conn:
            result = conn.execute(text(sql_str), params)

            if result.returns_rows:
                return result.fetchall()
            else:
                return result.rowcount

db = Database(db_engine)