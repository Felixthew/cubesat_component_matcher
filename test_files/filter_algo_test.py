from sqlalchemy import text


def get_schemas(engine):
    query = f"""
       SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'public')
        ORDER BY schema_name;  
    """
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return [row[0] for row in result]


def get_systems(engine, schema_name: str):
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema_name;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"schema_name": schema_name })
        return [row[0] for row in result]


def get_parameters(engine, schema_name: str, table_name: str):
    query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = :schema_name AND table_name = :table_name;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"schema_name": schema_name, "table_name": table_name})
        return [row[0] for row in result]
