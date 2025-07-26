import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from complete_backend_solution.src.api2 import app
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

    def test_get_solutions(self, client):
        """Test retrieving options"""
        response = client.get("/solutions")
        print(response.json())


    def test_get_params(self, client):
        response = client.get("/options/power_TEST/solar_arrays")
        print(response.json())

        assert response.status_code == 200

    def test_get_scores(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_request.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        print(response.json())
        with open("results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)

    def test_get_scores_list(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_req2.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        print(response.json())
        with open("list_results.json", "w") as json_file:
            json.dump(response.json(), json_file, indent=4)
