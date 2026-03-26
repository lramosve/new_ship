import pytest


def test_read_main(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up and running"}

# Add more tests for CRUD operations on documents, users, issues, plans, and projects
