import uuid
import json
from database import db

def generate_session_id() -> str:
    return str(uuid.uuid4())

def save_request(session_id: str, request_data: dict):
    pass

def save_results(session_id: str, results_data: dict):
    pass

def load_request(session_id: str) -> dict:
    pass

def load_results(session_id: str) -> dict:
    pass

def prune_expired_sessions(lifetime_hours: int):
    db.execute(
        """
        DELETE FROM metadata.session_data
            WHERE created_at < now() - interval ':hours hours'
        """,
        {"hours": lifetime_hours}
    )
