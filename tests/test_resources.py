def test_document_crud(client, auth_headers):
    created = client.post(
        '/documents/',
        json={'title': 'Spec', 'type': 'markdown', 'content': 'Initial content'},
        headers=auth_headers,
    )
    assert created.status_code == 201
    document_id = created.json()['id']

    updated = client.put(
        f'/documents/{document_id}',
        json={'title': 'Spec v2', 'type': 'spec', 'content': None},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()['title'] == 'Spec v2'
    assert updated.json()['content'] is None

    deleted = client.delete(f'/documents/{document_id}', headers=auth_headers)
    assert deleted.status_code == 204

    missing = client.get(f'/documents/{document_id}')
    assert missing.status_code == 404



def test_issue_crud(client, auth_headers):
    created = client.post(
        '/issues/',
        json={'title': 'Fix login', 'description': 'Users cannot sign in', 'status': 'open'},
        headers=auth_headers,
    )
    assert created.status_code == 201
    issue_id = created.json()['id']

    updated = client.put(
        f'/issues/{issue_id}',
        json={'title': 'Fix login flow', 'description': None, 'status': 'in_progress'},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()['status'] == 'in_progress'

    deleted = client.delete(f'/issues/{issue_id}', headers=auth_headers)
    assert deleted.status_code == 204

    missing = client.get(f'/issues/{issue_id}')
    assert missing.status_code == 404



def test_plan_crud(client, auth_headers):
    created = client.post(
        '/plans/',
        json={'description': 'Ship CRUD dashboard', 'week_number': 12},
        headers=auth_headers,
    )
    assert created.status_code == 201
    plan_id = created.json()['id']

    updated = client.put(
        f'/plans/{plan_id}',
        json={'description': 'Ship validated CRUD dashboard', 'week_number': 13},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()['week_number'] == 13

    deleted = client.delete(f'/plans/{plan_id}', headers=auth_headers)
    assert deleted.status_code == 204

    missing = client.get(f'/plans/{plan_id}')
    assert missing.status_code == 404
