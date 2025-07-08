from aiden_halfstack_solution.src.json_types import Location
from database import db
import json_types

def load_dtypes(location: Location) -> dict[str, str]:
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
        for col, dtype in result.items()
    }

def load_candidates(location: Location) -> pd.DataFrame:
    return pd.read_sql_table(table_name=location.table, con=db.db_engine, schema=location.schema)

def load_request(specs: list[ColumnSpec]) -> dict[str, dict[str | int | float, float]]:
    return {
        col.name: {"value": col.value, "weight": col.weight}
        for col in specs
    }