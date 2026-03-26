def test_create_project(client, auth_headers):
    response = client.post(
        '/projects/',
        json={'name': 'Test Project', 'description': 'A test project.'},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()['name'] == 'Test Project'



def test_read_project(client, auth_headers):
    create_response = client.post(
        '/projects/',
        json={'name': 'Test Project', 'description': 'A test project.'},
        headers=auth_headers,
    )
    project_id = create_response.json()['id']

    response = client.get(f'/projects/{project_id}')
    assert response.status_code == 200
    assert response.json()['name'] == 'Test Project'



def test_update_project(client, auth_headers):
    create_response = client.post(
        '/projects/',
        json={'name': 'Test Project', 'description': 'A test project.'},
        headers=auth_headers,
    )
    project_id = create_response.json()['id']

    response = client.put(
        f'/projects/{project_id}',
        json={'name': 'Updated Project', 'description': 'An updated test project.'},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()['name'] == 'Updated Project'



def test_delete_project(client, auth_headers):
    create_response = client.post(
        '/projects/',
        json={'name': 'Test Project', 'description': 'A test project.'},
        headers=auth_headers,
    )
    project_id = create_response.json()['id']

    response = client.delete(f'/projects/{project_id}', headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f'/projects/{project_id}')
    assert get_response.status_code == 404
