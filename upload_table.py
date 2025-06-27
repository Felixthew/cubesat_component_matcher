# AI usage:
# Claude Sonnet 4 was used to advise what to use and for writing
# individual sections of code. I (Felix) the put everything together
# edited and documented the code.
import os
import re
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from sqlalchemy import create_engine, text, inspect, Engine
from sqlalchemy.exc import SQLAlchemyError

# The database public url for the railway server
connection_string = "postgresql://postgres:PzcglEfINUtMgDzqZAtEhvVexsfWIrZT@switchyard.proxy.rlwy.net:12039/railway"


def upload_excel(file_path, schema="public"):
    """
    Uploads each sheet of an Excel spreadsheet file to the postgresql database as a table.

    :param file_path: the file path of the Excel file to upload.
    :param schema: The schema for the table to be added. Defaults to public, which is the default schema in SQL.
    """
    try:
        excel_file = pd.ExcelFile(file_path)
        filename = re.split("[/\\\\]", file_path)[-1]
        sheet_names = excel_file.sheet_names

        # Connects to the server
        engine = create_engine(connection_string)

        _create_metadata_table(engine)
        if schema != "public":
            with engine.connect() as conn:
                conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
                conn.commit()

        for sheet_name in sheet_names:
            # The tabel name, this can be anything we want.
            if len(sheet_names) == 1:
                # If there's only one sheet the table name will just be the name of the file.
                # Ignore any SyntaxWarning pycharm gives about this line.
                table_name = filename.replace('.xlsx', '')
            else:
                table_name = sheet_name

            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Writing to the database
            df.to_sql(table_name, engine, schema=schema, if_exists='replace')
            _upload_data(engine, df, schema, table_name)
            print(
                f"Successfully uploaded the Excel sheet {filename}#{sheet_name} as table {'.'.join([schema, table_name])}.")

    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
    except SQLAlchemyError as e:
        print(f"Database error for file {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error for file {file_path}: {e}")


def remove_table(table_name):
    """
    Removes a table from the postgresql database.

    :param table_name: the name of the table to remove i.e. "table" or "schema.table".
    """
    try:
        engine = create_engine(connection_string)

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if table_name in existing_tables:
            # Drop the table
            with engine.connect() as conn:
                conn.execute(text(f'DROP TABLE "{table_name}"'))
                conn.commit()
            print(f"Successfully removed the table: {table_name}")
        else:
            print(f'Could not find table "{table_name}"')
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def upload_all(directory_path, has_schema=False):
    """
    Uploads all xlsx files in a directory as tables to the postgresql database.
    
    :param directory_path: the directory path of the directory to upload.
    :param has_schema: If true, will treat any subdirectory as schema.
    """
    # all Excel files must end with .xlsx
    xlsx_files = [os.path.join(root, file)
                  for root, dirs, files in os.walk(".")
                  for file in files
                  if file.endswith('.xlsx')]

    for xlsx_file in xlsx_files:
        if has_schema:
            # A lot is happening here, but stay with me now

            # Remove everything before and including directory provided
            schema = (xlsx_file
                      .removeprefix(".\\")
                      .removeprefix(directory_path + "\\"))
            # Split by / or \ and remove the filename so that only the subdirectory is left
            schema = re.split("[/\\\\]", schema)[:-1]
            if len(schema) > 1:  # in case of multiple subdirectories
                # This is a quirk of SQL
                print(f"creation of schema {'.'.join(schema)} failed; schema may only be one layer deep. "
                      f"file {xlsx_file} not uploaded")
            else:
                schema = schema[0] if schema else "public"
                upload_excel(xlsx_file, schema=schema)
        else:
            upload_excel(xlsx_file)
    print(f"Finished directory upload of {directory_path}.")


def _create_metadata_table(engine: Engine):
    query = f"""
        CREATE SCHEMA IF NOT EXISTS "metadata";
        CREATE TABLE IF NOT EXISTS metadata.data_types (
        schema_name TEXT NOT NULL,
        table_name TEXT NOT NULL,
        column_name TEXT NOT NULL,
        type TEXT NOT NULL
        );
    """

    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


def _upload_data(engine, df, schema_name: str, table_name: str):
    df_data = df.drop(index=1).reset_index(drop=True) # remove metadata
    df_data.to_sql(table_name, engine, schema=schema_name, index=False) # export clean data
    metadata = df.iloc[1] # read metadata
    metadata_entry = [ # parse metadata
        {"schema_name": schema_name, "table_name": table_name, "column_name": col, "type": metadata[col]}
        for col in df.columns
    ]

    # export metadata
    query = """
        INSERT INTO metadata.data_types (schema_name, table_name, column_name, type)
        VALUES (:schema_name, :table_name, :column_name, :type);
    """

    with engine.begin() as conn:
        conn.execute(text(query), metadata_entry)


# call whatever method you want to run here, below is an example:
upload_all("test_data_main_directory", has_schema=True)