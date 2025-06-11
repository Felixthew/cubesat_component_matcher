# assisted by claude
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# The database public url for the railway server
connection_string = "postgresql://postgres:PzcglEfINUtMgDzqZAtEhvVexsfWIrZT@switchyard.proxy.rlwy.net:12039/railway"


def upload_excel(file_path):
    """
    Uploads an Excel file as a table to the postgresql database.

    :param file_path: the file path of the Excel file to upload.
    """
    try:
        df = pd.read_excel(file_path)

        # Connects to the server
        engine = create_engine(connection_string)

        # The tabel name, this can be anything we want
        # configured for mac
        table_name = file_path.split('/')[-1].replace('.xlsx', '')

        # Writing to the database
        df.to_sql(table_name, engine, if_exists='replace')

    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def remove_table(table_name):
    """
    Removes a table from the postgresql database.

    :param table_name: the name of the table to remove.
    """
    try:
        engine = create_engine(connection_string)

        # Drop the table
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.commit()
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

# call whatever method you want to run here, below is an example:
upload_all(input("Enter the directory path: "))
