import uuid
import json
from typing import Any

from psycopg2.extras import Json

from complete_backend_solution.src.database import db
from complete_backend_solution.src import json_types as jt

# sessions stay cached for a week by default
DEFAULT_EXPIRATION_TIME_HOURS = 168

# whitelisted columns to query from. MUST BE UPDATED IF TABLE CHANGES
ALLOWED_DATA = {"request_data", "results_data"}

def generate_session_id() -> str:
    """
    Generates new session id to be cached and recalled during reslicing
    :return: string uuid
    """
    return str(uuid.uuid4())

def save_request(session_id: str, request_data: dict):
    """
    Saves request data in metadata.session_data table
    :param session_id: previously-generated session id
    :param request_data: dict of the request json, including schema/table, specs, weights, filters, sorts, and pages
    """
    db.execute(
        """
        INSERT INTO metadata.session_data (session_id, request_data, created_at)
        VALUES (:sid, :data, now())
        ON CONFLICT (session_id) DO UPDATE
        SET request_data = :data, created_at = now()
        """,
        {
            "sid": session_id,
            "data": json.dumps(request_data)
        }
    )

def save_results(session_id: str, results_data: dict):
    """
    Saves returned data after a request in metadata.session_data table
    :param session_id: previously-generated session id
    :param results_data: dict of the results json as a DB retrieval
    """
    db.execute(
        """
        UPDATE metadata.session_data
        SET results_data = :data
        WHERE session_id = :sid
        """,
        {
            "sid": session_id,
            "data": Json(results_data)
         }
    )


def save_results_bm(results: jt.SearchResponse):
    db.execute(
        """
        UPDATE metadata.session_data
        SET results_data = :data
            WHERE session_id = :sid
        """,
        {"sid": results.session_id,
         "data": Json({"values": results.values, "order": results.order})}
    )

def load_request(session_id: str) -> dict:
    """
    Retrieves request data from initial DB query given a session id
    :param session_id: session id
    :return: dict of request data, including schema/table, specs, weights, filters, sorts, and pages
    """
    return _load_data(session_id, "request_data")

def load_results(session_id: str) -> dict[str, Any]:
    """
    Retrieves results data from initial DB query given a session id
    :param session_id: session id
    :return: dict of all results data
    """
    return _load_data(session_id, "results_data")

def _load_data(session_id: str, data_name: str) -> dict | list[dict]:
    if session_id is None:
        raise ValueError("No session ID")

    _validate_input(data_name)

    result = db.execute(
        f"""
        SELECT {data_name}
        FROM metadata.session_data
        WHERE session_id = :sid
        """,
        {
            "sid": session_id,
            "data": data_name
        }
    )
    return result[0][0] if result else None

def _validate_input(input: str):
    if input not in ALLOWED_DATA:
        raise ValueError("Invalid data input")

def prune_expired_sessions(lifetime_hours: int = DEFAULT_EXPIRATION_TIME_HOURS):
    db.execute(
        """
        DELETE FROM metadata.session_data
         WHERE created_at < now() - interval ':hours hours'
        """,
        {"hours": lifetime_hours}
    )
