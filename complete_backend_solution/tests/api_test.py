from http.client import responses

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from complete_backend_solution.src.api2 import app, retrieve
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
        response = client.get("/options")
        print(response.json())

        assert response.status_code == 200

    def test_get_systems(self, client):
        response = client.get("/options/power_TEST")
        print(response.json())

        assert response.status_code == 200

    def test_get_scores(self, client):
        # Load the JSON data from a file
        with open('component_data_TEST/test_request.json', 'r') as f:
            search_request = json.load(f)
        response = client.post("/search", json=search_request)
        response_json = response.json()
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(response_json, f, ensure_ascii=False, indent=2)
        print(response.json())


    def test_retrieve(self, client):
        with open('component_data_TEST/test_retrieve.json', 'r') as f:
            retrieve_request = json.load(f)
        response = client.post("/search/3ffc8d0d-f9fb-489b-90dc-eaf4bbe2d485", json=retrieve_request)
        response_json = response.json()
        with open("filtered_results.json", "w", encoding="utf-8") as f:
            json.dump(response_json, f, ensure_ascii=False, indent=2)
        print(response.json())
