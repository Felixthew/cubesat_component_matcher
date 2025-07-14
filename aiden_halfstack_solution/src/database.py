import os
import pandas as pd
from pandas.io.sql import execute
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", "postgresql://postgres:vWhRGCabfMySJMDkrrmZQhxiUNFDuYyn@tramway.proxy.rlwy.net:31947/railway")
db_engine = create_engine(DB_URL)

class Database:
    def __init__(self, engine):
        self.db_engine = engine

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

    # def df_table(self, schema: str, table: str) -> pd.DataFrame:
    #     """
    #     Loads a requested table as a pandas Dataframe
    #     :param schema: requested schema
    #     :param table: requested table
    #     :return: dataframe of table
    #     """
    #     return pd.read_sql_table(table_name=table, con=self.db_engine, schema=schema)

db = Database(db_engine)