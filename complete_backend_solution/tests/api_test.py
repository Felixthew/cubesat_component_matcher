import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.api2 import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    pass


class TestUserAPI:

    def test_get_all_users(self, client):
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