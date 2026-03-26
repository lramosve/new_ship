def test_read_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'up and running'}



def test_create_project_requires_auth(client):
    response = client.post('/projects/', json={'name': 'New Project', 'description': 'A new project description'})
    assert response.status_code == 401



def test_get_projects_returns_wrapped_list(client):
    response = client.get('/projects/')
    assert response.status_code == 200
    payload = response.json()
    assert 'items' in payload
    assert 'total' in payload
    assert isinstance(payload['items'], list)
