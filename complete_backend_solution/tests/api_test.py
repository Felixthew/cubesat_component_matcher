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
        """Test retrieving all users"""
        response = client.get("/solutions")
        print(response.json())

        # assert response.status_code == 200
        #
        # users = response.json()
        # assert isinstance(users, list)
        # assert len(users) == 2
        #
        # # Check first user structure
        # assert users[0]["id"] == 1
        # assert users[0]["name"] == "John Doe"
        # assert users[0]["email"] == "john@example.com"

    def test_get_scores(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        response_json = response.json()
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(response_json, f, ensure_ascii=False, indent=2)
        print(response.json())
