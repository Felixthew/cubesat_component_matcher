from functools import lru_cache
from complete_backend_solution.src.json_types import Location, ColumnSpec
from complete_backend_solution.src.database import db
import pandas as pd

@lru_cache(maxsize=16)
def get_dtypes(location: Location) -> dict[str, str]:
    """
    Retrieves and caches the dtypes by column given a schema and table. {maxsize} retrievals will be cached before auto-eviction begins
    :param location: the schema and table to query to
    :return: dict of col -> dtype
    """
    return _load_dtypes(location)

def _load_dtypes(location: Location) -> dict[str, str]:
    result = db.execute(
        """
        SELECT column_name, dtype
        FROM metadata.data_types
        WHERE schema_name = :target_schema
        AND table_name = :target_table
        """,
        {"target_schema": location.schema, "target_table": location.table}
    )

    return {
        dict['column_name']: dict['dtype']
        for dict in result
    }

def load_candidates(location: Location) -> pd.DataFrame:
    return pd.read_sql_table(table_name=location.table, con=db.db_engine, schema=location.schema)

def load_request(specs: list[ColumnSpec]) -> dict[str, dict[str | int | float, float]]:
    return {
        col.name: {"value": col.value, "weight": col.weight}
        for col in specs
    }

def list_schema():
    return db.execute(
        """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN :blacklist_schema
        ORDER BY schema_name;  
        """,
        {"blacklist_schema": ", ".join(db.BLACKLIST_SCHEMA)}
    ).scalars().all()

def list_tables(schema: str):
    return db.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema
        ORDER BY table_name
        """,
        {"schema": schema}
    ).scalars.all()

def get_options(location: Location, dtype_profile: dict[str, str]) -> dict[str, list[str]]:
    options = {}
    for col, dtype in dtype_profile.items():
        if dtype == "string":
            result = db.execute(
                """
                SELECT {col}
                FROM {location.schema}.{location.table}
                """
            )
            options = {
                result[col]
                for _ in result
            }

        elif dtype == "list":


        else:
            options[name] = None

