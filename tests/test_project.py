import pytest


def test_create_project(client, db_session):
    response = client.post(
        "/projects/",
        json={"name": "Test Project", "description": "A test project."}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"


def test_read_project(client, db_session):
    # First create a project
    create_response = client.post(
        "/projects/",
        json={"name": "Test Project", "description": "A test project."}
    )
    project_id = create_response.json()["id"]

    # Read the created project
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"


def test_update_project(client, db_session):
    # First create a project
    create_response = client.post(
        "/projects/",
        json={"name": "Test Project", "description": "A test project."}
    )
    project_id = create_response.json()["id"]

    # Update the created project
    response = client.put(
        f"/projects/{project_id}",
        json={"name": "Updated Project", "description": "An updated test project."}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"


def test_delete_project(client, db_session):
    # First create a project
    create_response = client.post(
        "/projects/",
        json={"name": "Test Project", "description": "A test project."}
    )
    project_id = create_response.json()["id"]

    # Delete the created project
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200

    # Verify deletion
    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 404
