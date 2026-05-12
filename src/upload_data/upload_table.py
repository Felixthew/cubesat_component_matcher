# AI usage:
# Claude Sonnet 4 was used to advise what to use and for writing
# individual sections of code. I (Felix) the put everything together
# edited and documented the code.
import argparse
import os
import re
import pandas as pd
from sqlalchemy import create_engine, text, inspect, Engine
from sqlalchemy.exc import SQLAlchemyError


def upload_excel(engine: Engine, file_path, schema="public", verbose=False):
    """
    Uploads each sheet of an Excel spreadsheet file to the postgresql database as a table.

    :param engine: SQLAlchemy engine pointing at the target database.
    :param file_path: the file path of the Excel file to upload.
    :param schema: The schema for the table to be added. Defaults to public, which is the default schema in SQL.
    :param verbose: will print progress messages and useful info to the console if true.
    """
    try:
        excel_file = pd.ExcelFile(file_path)
        filename = re.split("[/\\\\]", file_path)[-1]
        sheet_names = excel_file.sheet_names

        _create_metadata_schema(engine)
        if schema != "public":
            with engine.connect() as conn:
                conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
                conn.commit()

        for sheet_name in sheet_names:
            table_name = sheet_name
            if verbose:
                print(f"\nUploading {filename}#{table_name}...")

            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Writing to the database
            _upload_data(engine, df, schema, table_name, verbose=verbose)
            if verbose:
                print(
                f"Successfully uploaded the Excel sheet {filename}#{sheet_name} as table {'.'.join([schema, table_name])}.")

    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
    except SQLAlchemyError as e:
        print(f"Database error for file {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error for file {file_path}: {e}")


def remove_table(engine: Engine, table_name):
    """
    Removes a table from the postgresql database.

    :param engine: SQLAlchemy engine pointing at the target database.
    :param table_name: the name of the table to remove i.e. "table" or "schema.table".
    """
    try:
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


def upload_all(engine: Engine, directory_path, has_schema=False, verbose=False):
    """
    Uploads all xlsx files in a directory as tables to the postgresql database.

    :param engine: SQLAlchemy engine pointing at the target database.
    :param directory_path: the directory path of the directory to upload.
    :param has_schema: If true, will treat any subdirectory as schema.
    :param verbose: will print progress messages and useful info to the console if true.
    """
    # all Excel files must end with .xlsx
    xlsx_files = [os.path.join(root, file)
                  for root, dirs, files in os.walk(directory_path)
                  for file in files
                  if file.endswith('.xlsx')]

    for xlsx_file in xlsx_files:
        if has_schema:
            # A lot is happening here, but stay with me now

            # Remove everything before and including directory provided
            schema = (xlsx_file
                      .removeprefix(".\\")
                      .removeprefix("./")
                      .removeprefix(directory_path + "\\")
                      .removeprefix(directory_path + "/"))
            # Split by / or \ and remove the filename so that only the subdirectory is left
            schema = re.split("[/\\\\]", schema)[:-1]
            if len(schema) > 1 and verbose:  # in case of multiple subdirectories
                # This is a quirk of SQL
                print(f"WARNING: Multi-layer schema not allowed, trimming schema {'.'.join(schema)} to {schema[-1]} for file {xlsx_file}")

            # take parent dir of file as schema
            schema = schema[-1] if schema else "public"
            upload_excel(engine, xlsx_file, schema=schema, verbose=verbose)
        else:
            upload_excel(engine, xlsx_file, verbose=verbose)
    if verbose:
        print(f"Finished directory upload of {directory_path}.")


def _create_metadata_schema(engine: Engine):
    query = """
        CREATE SCHEMA IF NOT EXISTS "metadata";
        CREATE TABLE IF NOT EXISTS metadata.data_types (
        schema_name TEXT NOT NULL,
        table_name TEXT NOT NULL,
        column_name TEXT NOT NULL,
        dtype TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS metadata.session_data (
        session_id VARCHAR(36) PRIMARY KEY,
        request_data JSONB NOT NULL,
        results_data JSONB,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """

    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


def _upload_data(engine: Engine, df: pd.DataFrame, schema_name: str, table_name: str, verbose=False):
    df_data = df.drop(index=0).reset_index(drop=True) # remove metadata
    # force columns with int and floats to float
    df_data = _convert_numeric(df_data, verbose=verbose)
    df_data.to_sql(table_name, engine, schema=schema_name, index=False, if_exists='replace') # export clean data
    metadata = df.iloc[0] # read metadata
    metadata_entry = [ # parse metadata
        {"schema_name": schema_name, "table_name": table_name, "column_name": col, "dtype": metadata[col]}
        for col in df.columns
    ]

    # export metadata
    query = """
        INSERT INTO metadata.data_types (schema_name, table_name, column_name, dtype)
        VALUES (:schema_name, :table_name, :column_name, :dtype);
    """

    with engine.begin() as conn:
        conn.execute(text(query), metadata_entry)

def _convert_numeric(df, verbose=False):
    # Step 2: Loop over object columns and check if they contain only numbers (ignoring NaNs)
    for col in df.select_dtypes(include='object').columns:
        # Try converting to numeric
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
            if verbose:
                print(f" -- Successfully converted {col} to numeric.")
        except ValueError:
            if verbose:
                print(f" -- Could not convert column {col} to numeric.")
    if verbose:
        print(f"Dataframe dtypes: ")
        for col, dtype in df.dtypes.items():
            print(f"\t{col}: {dtype}")
    return df


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Upload Excel data into a PostgreSQL database. "
                    "--db-url is required so the prod DB is never hit by accident."
    )
    parser.add_argument("directory", help="Directory containing .xlsx files to upload.")
    parser.add_argument("--db-url", required=True,
                        help="PostgreSQL connection string for the target database. "
                             "Be explicit — there is no default fallback.")
    parser.add_argument("--has-schema", action="store_true",
                        help="Treat subdirectories of <directory> as target schemas.")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    engine = create_engine(args.db_url)
    upload_all(engine, args.directory, has_schema=args.has_schema, verbose=args.verbose)
