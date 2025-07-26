from functools import lru_cache
from sqlalchemy import MetaData, Table, select, distinct

from complete_backend_solution.src.json_types import Location, ColumnSpec
from complete_backend_solution.src.database import db
import pandas as pd

EXPOSABLE_DTYPES = {
    "string",
    "list"
}

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
        col: dtype
        for col, dtype in result
    }

def load_candidates(location: Location) -> pd.DataFrame:
    return pd.read_sql_table(table_name=location.table, con=db.db_engine, schema=location.schema)

def load_request(specs: list[ColumnSpec]) -> dict[str, dict[str | int | float, float]]:
    return {
        col.name: {"value": col.value, "weight": col.weight}
        for col in specs
    }

def list_schema() -> list[str]:
    schema = db.execute(
        """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN :blacklist_schema
        ORDER BY schema_name;  
        """,
        {"blacklist_schema": tuple(db.BLACKLIST_SCHEMA)}
    )
    return [s["schema_name"] for s in schema]

def list_tables(schema: str) -> list[str]:
    tables = db.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema
        ORDER BY table_name
        """,
        {"schema": schema}
    )
    return [t["table_name"] for t in tables]

# def list_options(location: Location, dtype_profile: dict[str, str]) -> dict[str, list[str]]:
#
#     # sets up table access using sqlalchemy Core
#     metadata = MetaData()
#     table = Table(location.table, metadata, schema=location.schema, autoload_with=db.db_engine)
#
#     # initialize results dict
#     options = {}
#     with db.db_engine.connect() as conn:
#         for col_name, dtype in dtype_profile.items():
#             col = table.c[col_name]
#
#             # if the column is of type string, collect all distinct values and enter to dict under the column name
#             if dtype == "string":
#                 query = select(distinct(col))
#
#                 result = conn.execute(query).scalars().all()
#                 options[col_name] = list(result)
#
#             # if type list, collect all distinct (string) values, split, make unique, then enter under column name
#             elif dtype == "list":
#                 query = select(distinct(col))
#
#                 result = conn.execute(query).scalars().all()
#
#                 list_results = set()
#                 for data_list in result:
#                     list_results.add(data_list.split(", "))
#
#                 options[col_name] = list(list_results)
#
#     return options

def list_options(location: Location, col_name: str, dtype: str) -> list[str] | None:
    # sets up table access using sqlalchemy Core
    metadata = MetaData()
    table = Table(location.table, metadata, schema=location.schema, autoload_with=db.db_engine)

    # if the type requires exposing, i.e. the method is being used as intended
    if dtype in EXPOSABLE_DTYPES:
        with db.db_engine.connect() as conn:

            # retrieve all unique scalars for the column
            col = table.c[col_name]
            query = select(distinct(col))
            result = conn.execute(query).scalars().all()

            # if string, just return the scalars
            if dtype == "string":
                return result

            # if list, split, dedupe, then return
            elif dtype == "list":
                deduped_results = set()
                for list_data in result:
                    deduped_results.add(list_data.split(", "))
                return list(deduped_results)

    # if not an exposable type, it has no options
    return None