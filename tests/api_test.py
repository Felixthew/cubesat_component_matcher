import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from src.backend_solution.api import app
from src.backend_solution.database import Database, get_db

# Override path lets CI / other machines point at a different test DB without
# touching the source. Default matches what the user uploaded the mock data into.
TEST_DB_URL = os.getenv(
    "TEST_DB_URL", "postgresql://felix:postgres@localhost:5432/cubesat_test"
)
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_fixture(name: str) -> dict:
    with open(os.path.join(TESTS_DIR, "test_requests", name)) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def test_engine():
    return create_engine(TEST_DB_URL)


@pytest.fixture(scope="session")
def test_db(test_engine):
    return Database(test_engine)


@pytest.fixture(autouse=True)
def reset_session_data(test_engine):
    """Start each test with an empty session cache so prior runs don't leak."""
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE metadata.session_data"))
    yield


@pytest.fixture
def client(test_db):
    # Dtype cache lives on the Database instance; clear it between tests so a
    # mid-test schema change can't be hidden by a stale entry.
    test_db.dtype_cache.clear()
    app.dependency_overrides[get_db] = lambda: test_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


class TestOptionsAPI:
    def test_list_schemas_includes_test_schemas(self, client):
        r = client.get("/options")
        assert r.status_code == 200
        schemas = r.json()["schemas"]
        # cubesat_test was loaded from tests/component_data_MOCK/ with has_schema=True
        assert {"power_TEST", "platforms_TEST", "avionics_TEST"}.issubset(schemas)

    def test_list_tables_power(self, client):
        r = client.get("/options/power_TEST")
        assert r.status_code == 200
        assert r.json() == {"schema": "power_TEST", "tables": ["solar_arrays"]}

    def test_list_tables_avionics(self, client):
        r = client.get("/options/avionics_TEST")
        assert r.status_code == 200
        # information_schema.tables is queried with ORDER BY table_name → alphabetical
        assert r.json()["tables"] == ["boards", "sat_computer"]

    def test_list_tables_missing_schema_returns_404(self, client):
        r = client.get("/options/does_not_exist")
        assert r.status_code == 404

    def test_get_params_power_solar_arrays(self, client):
        r = client.get("/options/power_TEST/solar_arrays")
        assert r.status_code == 200
        cols = {c["name"]: c for c in r.json()["columns"]}

        assert cols["Company"]["dtype"] == "string"
        # 'string' is in EXPOSABLE_DTYPES → distinct values are populated
        assert "DHV Technologies" in cols["Company"]["options"]
        assert "MMA Design" in cols["Company"]["options"]

        assert cols["Specific Power (W/kg)"]["dtype"] == "number"
        # numbers are not exposable → options is None
        assert cols["Specific Power (W/kg)"]["options"] is None

    def test_get_kwargs(self, client):
        r = client.get("/kwargs")
        assert r.status_code == 200
        assert set(r.json().keys()) == {
            "number", "string", "tuple", "list", "boolean", "range"
        }


class TestSearchAPI:
    def test_search_exact_match_tops_results(self, client):
        # test_request.json: Company="DHV Technologies" (w=1.5), Specific Power=68 (w=200)
        # MockArray-Alpha is the only row exact on both → overall_score must be 1.0
        r = client.post("/search", json=_load_fixture("test_request.json"))
        assert r.status_code == 200
        body = r.json()

        assert isinstance(body["session_id"], str) and len(body["session_id"]) > 0
        # 9 rows in power_TEST.solar_arrays
        assert len(body["values"]) == 9

        top = body["values"][0]
        assert top["Product"] == "MockArray-Alpha"
        assert top["Company"] == "DHV Technologies"
        assert top["Specific Power (W/kg)"] == 68
        assert top["overall_score"] == pytest.approx(1.0)

        # Results returned by /search are sorted by overall_score descending
        scores = [v["overall_score"] for v in body["values"]]
        assert scores == sorted(scores, reverse=True)

    def test_search_platforms_returns_all_rows_sorted(self, client):
        # Fuzz ratios for org names are touchy to assert exactly; just sanity-check shape.
        r = client.post("/search", json=_load_fixture("test_req2.json"))
        assert r.status_code == 200
        body = r.json()

        # 8 rows in platforms_TEST.hosted_payloads
        assert len(body["values"]) == 8
        scores = [v["overall_score"] for v in body["values"]]
        assert scores == sorted(scores, reverse=True)
        # Every row has every requested score column populated
        for v in body["values"]:
            assert "Organization_score" in v
            assert "Intended Destination_score" in v
            assert "US Office_score" in v

    def test_search_tuple_exact_match(self, client):
        # test_req3.json: Dimensions="10,2,5" (w=10), TRL=5 (w=5)
        # MicroBoard has Dimensions="10, 2, 5" and TRL=5 → exact tuple+number match
        r = client.post("/search", json=_load_fixture("test_req3.json"))
        assert r.status_code == 200
        body = r.json()

        assert len(body["values"]) == 8  # 8 rows in avionics_TEST.boards
        top = body["values"][0]
        assert top["Product"] == "MicroBoard"
        assert top["overall_score"] == pytest.approx(1.0)
        assert top["Dimensions_score"] == pytest.approx(1.0)
        assert top["TRL_score"] == pytest.approx(1.0)

    def test_search_number_symmetric_around_request(self, client):
        # test_req4.json: Voltage=45 (w=10). Closest candidates are OBC-Pro (48) and
        # FlightCPU (42), both diff=3. Global max=50, min=5 → score = 1 - 3/50 = 0.94.
        r = client.post("/search", json=_load_fixture("test_req4.json"))
        assert r.status_code == 200
        body = r.json()

        assert len(body["values"]) == 7  # 7 rows in avionics_TEST.sat_computer
        # Top score is deterministic even though which of the two ties first is not
        assert body["values"][0]["overall_score"] == pytest.approx(1 - 3 / 50)
        assert body["values"][0]["Voltage"] in (42, 48)

    def test_search_with_kwargs_overrides(self, client):
        # test_req_kwargs.json applies:
        #   col_kwargs.Headquarters.contains_any = true (string)
        #   type_kwargs.list.match_mode = "contains"
        # Xplore (HQ=USA, Dest=LEO+GEO+MEO+GTO, Org=Xplore) matches all three at 1.0.
        r = client.post("/search", json=_load_fixture("test_req_kwargs.json"))
        assert r.status_code == 200
        body = r.json()

        top = body["values"][0]
        assert top["Organization"] == "Xplore"
        assert top["overall_score"] == pytest.approx(1.0)


class TestRetrieveAPI:
    def test_retrieve_filters_and_sorts(self, client):
        # Step 1: run the search to cache a scored df under a session_id
        r = client.post("/search", json=_load_fixture("test_request.json"))
        assert r.status_code == 200
        sid = r.json()["session_id"]

        # Step 2: reslice with min/max filters + ascending sort by Specific Power.
        # Filters: Specific Power in [50, 100] AND Peak BOL Solar Array Power ≥ 4.0.
        # Excluded rows from the 9-row table:
        #   HaWK-Mock (Specific Power=45 < 50)
        #   Mock-Mini (30 < 50)
        #   Mock-Max  (110 > 100)
        #   Mock-Tiny (Peak BOL=2.0 < 4.0)
        # Remaining 5, sorted by Specific Power asc: 55, 65, 68, 75, 90
        r = client.post(f"/search/{sid}", json=_load_fixture("test_retrieve.json"))
        assert r.status_code == 200
        body = r.json()

        assert [v["Product"] for v in body["values"]] == [
            "Photon-Mock",
            "UltraTriple-Mock",
            "MockArray-Alpha",
            "MockArray-Beta",
            "MockArray-Gamma",
        ]
        assert [v["Specific Power (W/kg)"] for v in body["values"]] == [55, 65, 68, 75, 90]

    def test_retrieve_unknown_session_returns_404(self, client):
        r = client.post(
            "/search/00000000-0000-0000-0000-000000000000",
            json=_load_fixture("test_retrieve.json"),
        )
        assert r.status_code == 404
