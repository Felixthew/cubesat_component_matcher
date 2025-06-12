# AI usage:
# Claude Sonnet 4 was used to advise what to use and for writing
# individual sections of code. I (Felix) the put everything together
# edited and documented the code.
import os
import re
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# The database public url for the railway server
connection_string = "postgresql://postgres:PzcglEfINUtMgDzqZAtEhvVexsfWIrZT@switchyard.proxy.rlwy.net:12039/railway"


def upload_excel(file_path):
    """
    Uploads each sheet of an Excel spreadsheet file to the postgresql database as a table.

    :param file_path: the file path of the Excel file to upload.
    """
    try:
        excel_file = pd.ExcelFile(file_path)
        filename = re.split("[/\\\]", file_path)[-1]
        sheet_names = excel_file.sheet_names

        # Connects to the server
        engine = create_engine(connection_string)

        for sheet_name in sheet_names:
            # The tabel name, this can be anything we want.
            if len(sheet_name) == 0:
                # If there's only one sheet the table name will just be the name of the file.
                # Ignore any SyntaxWarning pycharm gives about this line.
                table_name = filename.replace('.xlsx', '')
            else:
                table_name = sheet_name

            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Writing to the database
            df.to_sql(table_name, engine, if_exists='replace')
            print(f"Successfully uploaded the Excel sheet {filename}#{sheet_name} as table {table_name}.")

    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
    except SQLAlchemyError as e:
        print(f"Database error for file {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error for file {file_path}: {e}")

def remove_table(table_name):
    """
    Removes a table from the postgresql database.

    :param table_name: the name of the table to remove.
    """
    try:
        engine = create_engine(connection_string)

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if table_name in existing_tables:
            # Drop the table
            with engine.connect() as conn:
                print(table_name)
                conn.execute(text(f'DROP TABLE "{table_name}"'))
                conn.commit()
            print(f"Successfully removed the table, {table_name}")
        else:
            print(f"Could not find table {table_name}")
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def upload_all(directory_path):
    """
    Uploads all xlsx files in a directory as tables to the postgresql database.
    
    :param directory_path: the directory path of the directory to upload.
    """
    # all Excel files must end with .xlsx
    xlsx_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.xlsx')]

    for xlsx_file in xlsx_files:
        upload_excel(xlsx_file)
    print(f"Successfully uploaded the xlsx files in {directory_path}.")

# call whatever method you want to run here, below is an example:
remove_table(input("Table to drop: "))
