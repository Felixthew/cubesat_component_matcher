from database import db
#, metadata_headers as md)

def load_dtypes(schema: str, table: str) -> dict[str, str]:
    result = db.execute(
        """
        SELECT column_name, dtype
        FROM metadata.data_types
        WHERE schema_name = :target_schema
            AND table_name = :target_table
        """,
        {"target_schema": schema, "target_table": table}
    )

    return {
        entry["column_name"]: entry["data_type"]
        for entry in result
    }