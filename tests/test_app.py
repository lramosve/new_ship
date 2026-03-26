import pytest
from starlette.testclient import TestClient


def test_read_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up and running"}


def test_create_project(client, db_session):
    project_data = {
        "name": "New Project",
        "description": "A new project description"
    }
    response = client.post("/projects/", json=project_data)
    assert response.status_code == 200
    assert "id" in response.json()


def test_get_projects(client, db_session):
    response = client.get("/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)