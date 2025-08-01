from functools import lru_cache
from sqlalchemy import MetaData, Table, select, distinct

from complete_backend_solution.src.json_types import Location, ColumnSpec
from complete_backend_solution.src.database import db
import pandas as pd

EXPOSABLE_DTYPES = {
    "string",
    "list"
}

# can't use location cause it has to be hashable
@lru_cache(maxsize=16)
def get_dtypes(schema: str, table: str) -> dict[str, str]:
    """
    Retrieves and caches the dtypes by column given a schema and table. {maxsize} retrievals will be cached before auto-eviction begins
    :param schema: the schema to query to
    :param table: the table to query to
    :return: dict of col -> dtype
    """
    location = Location(schema=schema, table=table)
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
    """
    Retrieves a dataframe of the candidate table, given a schema and table
    :param location: the schema and table to retrieve from
    :return: Pandas dataframe of the specified table
    """
    return pd.read_sql_table(table_name=location.table, con=db.db_engine, schema=location.schema)

def load_request(specs: list[ColumnSpec]) -> dict[str, dict[str | int | float, float]]:
    """
    Parses a list of ColumnSpec objects into a dict that can be used in the engine
    :param specs: list of ColumnSpec objects received from the JSON payload
    :return: {name: {"value": value, "weight": weight}, ...} formatted dict that contains all request info about a table
    """
    return {
        col.name: {"value": col.value, "weight": col.weight}
        for col in specs
    }

def list_schema() -> list[str]:
    """
    Retrieve all data schema. Excludes defaults seen in database.BLACKLIST_SCHEMA
    :return: list of working schema names
    """
    schema = db.execute(
        """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN :blacklist_schema
        ORDER BY schema_name;  
        """,
        {"blacklist_schema": tuple(db.BLACKLIST_SCHEMA)}
    )
    return [s[0] for s in schema]

    # return [s["schema_name"] for s in schema]

def list_tables(schema: str) -> list[str]:
    """
    List all tables (systems) in a given schema
    :param schema: the schema name to query from
    :return: List of all table names in schema
    """
    tables = db.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema
        ORDER BY table_name
        """,
        {"schema": schema}
    )
    return [t[0] for t in tables]
    #return [t["table_name"] for t in tables]

def list_choices(location: Location, col_name: str, dtype: str) -> list[str] | None:
    """
    Retrieves all possible single values from a column of an eligible type (as seen in EXPOSABLE_TYPES). This is
    intended to be a way to create efficient options for an end-user via dropdown menus. Example:
    A column containing list values of "LEO, MEO", "LEO", and "MEO, GEO, LLO" will return ["LEO", "MEO", "GEO", "LLO"].
    A column containing string values of "USA", "Japan", "Sweden", and "USA" will return ["USA", "Japan", "Sweden"].
    If a new datatype is made exposable, its logic must be added into a new conditional statement below.
    :param location: the schema and table to query from
    :param col_name: the name of the column to collect results from
    :param dtype: the datatype of the column
    :return: a list of word options representing every individual value in that column
    """
    # sets up table access using sqlalchemy Core
    metadata = MetaData()
    table = Table(location.table, metadata, schema=location.schema, autoload_with=db.db_engine)

    # if the type requires exposing, i.e. the method is being used as intended
    if dtype in EXPOSABLE_DTYPES:
        with db.db_engine.connect() as conn:

            # retrieve all unique scalars for the column
            col = table.c[col_name]
            query = select(distinct(col)).where(col.isnot(None))
            result = conn.execute(query).scalars().all()

            # if string, just return the scalars
            if dtype == "string":
                return result

            # if list, split, dedupe, then return
            elif dtype == "list":
                deduped_results = set()
                for list_data in result:
                    for item in list_data.split(", "):
                        deduped_results.add(item.strip())
                return list(deduped_results)

    # if not an exposable type, it has no options
    return None