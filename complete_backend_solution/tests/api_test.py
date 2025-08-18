import pytest
from fastapi.testclient import TestClient
from complete_backend_solution.src.api import app
import json

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    pass


class TestUserAPI:

    def test_get_options(self, client):
        """Test retrieving options"""
        response = client.get("/options")
        print(response.json())

    def test_get_tables(self, client):
        """Test retrieving options"""
        response = client.get("/options/avionics")
        print(response.json())


    def test_get_params(self, client):
        response = client.get("/options/power/solar_arrays")
        print(response.json())

        assert response.status_code == 200

    def test_get_scores(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_requests/test_request.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        print(response.json())
        with open("test_results/results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

    def test_get_scores_list(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_requests/test_req2.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        print(response.json())
        with open("test_results/list_results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

    def test_get_scores_tuple(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_requests/test_req3.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        print(response.json())
        with open("test_results/tuple_results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

    def test_get_scores_range(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_requests/test_req4.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        print(response.json())
        with open("test_results/range_results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

    def test_get_scores_kwargs(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_requests/test_req_kwargs.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        print(response.json())
        with open("test_results/kwargs_results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

    def test_filter(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_requests/test_retrieve.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search/4c3d84f1-88df-4dba-a2ac-225c56929114", json=search_request)
        print(response.json())
        with open("test_results/filtered_results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)