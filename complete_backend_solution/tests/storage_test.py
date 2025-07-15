import pytest
import complete_backend_solution.src.storage as st
from complete_backend_solution.src.database import db
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer

@pytest.fixture(autouse=True)
def storage_db(test_db):
    db.execute("""
    CREATE SCHEMA IF NOT EXISTS "metadata"
    CREATE TABLE IF NOT EXISTS metadata.session_data (
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    dtype TEXT NOT NULL
    );
    """
    )
    yield


def test_save_load_all(test_db):
    sid = st.generate_session_id()
    st.save_request(sid, {"a": {"b": "c"}, "d": "e"})
    assert st.load_request(sid) == {"a": {"b": "c"}, "d": "e"}