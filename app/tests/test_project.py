import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_project():
    response = client.post("/projects/", json={"name": "Test Project", "description": "A test project."})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

def test_get_projects():
    response = client.get("/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_project():
    # Create a project to test retrieval
    create_response = client.post("/projects/", json={"name": "Single Project", "description": "Single project test."})
    project_id = create_response.json()["id"]
    # Retrieve the created project
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id

def test_update_project():
    # Create a project to test update
    create_response = client.post("/projects/", json={"name": "Update Project", "description": "Project before update."})
    project_id = create_response.json()["id"]
    # Update the project
    response = client.put(f"/projects/{project_id}", json={"name": "Updated Project", "description": "Project after update."})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"

def test_delete_project():
    # Create a project to test deletion
    create_response = client.post("/projects/", json={"name": "Delete Project", "description": "Project to delete."})
    project_id = create_response.json()["id"]
    # Delete the created project
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    # Verify deletion
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 404
