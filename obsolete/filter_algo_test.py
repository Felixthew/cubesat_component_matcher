from sqlalchemy import text


def get_schemas(engine):
    """
    Queries the database for all of the working schema, i.e. all of the categories a client could request.
    :param engine: database engine
    :return: all working schema
    """
    # non-working schema must be manually blacklisted here
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
    """
    Queries the database for all of the table names given a specific schema
    :param engine: database engine
    :param schema_name: schema name
    :return: all tables in schema
    """
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema_name;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"schema_name": schema_name })
        return [row[0] for row in result]


def get_parameters(engine, schema_name: str, table_name: str):
    """
    Queries the database for all of the column headers given a table and schema, i.e. all the specs a
    client has control
    over
    :param engine: database engine
    :param schema_name: schema name
    :param table_name: table name
    :return: all parameter names in the table
    """
    query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = :schema_name AND table_name = :table_name;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"schema_name": schema_name, "table_name": table_name})
        return [row[0] for row in result]
