def test_task_crud_with_assignment_and_schedule(client, auth_headers):
    project_response = client.post(
        '/projects/',
        json={'name': 'Task Project', 'description': 'Project for task testing'},
        headers=auth_headers,
    )
    assert project_response.status_code == 201
    project_id = project_response.json()['id']

    user_response = client.post(
        '/users/',
        json={'name': 'Task Owner', 'email': 'task.owner@example.com', 'password': 'password123'},
    )
    assert user_response.status_code == 201
    assignee_id = user_response.json()['id']

    created = client.post(
        '/tasks/',
        json={
            'title': 'Build Kanban board',
            'description': 'Create the first board view',
            'status': 'todo',
            'priority': 'high',
            'progress': 15,
            'start_date': '2026-03-26',
            'due_date': '2026-04-02',
            'project_id': project_id,
            'assignee_id': assignee_id,
        },
        headers=auth_headers,
    )
    assert created.status_code == 201
    payload = created.json()
    task_id = payload['id']
    assert payload['assignee']['email'] == 'task.owner@example.com'
    assert payload['project']['name'] == 'Task Project'

    fetched = client.get(f'/tasks/{task_id}')
    assert fetched.status_code == 200
    assert fetched.json()['title'] == 'Build Kanban board'

    updated = client.put(
        f'/tasks/{task_id}',
        json={
            'title': 'Build Gantt view',
            'description': 'Timeline UI with progress',
            'status': 'in_progress',
            'priority': 'urgent',
            'progress': 60,
            'start_date': '2026-03-26',
            'due_date': '2026-04-05',
            'project_id': project_id,
            'assignee_id': assignee_id,
        },
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()['status'] == 'in_progress'
    assert updated.json()['priority'] == 'urgent'
    assert updated.json()['progress'] == 60

    listed = client.get('/tasks/')
    assert listed.status_code == 200
    list_payload = listed.json()
    assert list_payload['total'] >= 1
    assert any(item['id'] == task_id for item in list_payload['items'])

    deleted = client.delete(f'/tasks/{task_id}', headers=auth_headers)
    assert deleted.status_code == 204

    missing = client.get(f'/tasks/{task_id}')
    assert missing.status_code == 404



def test_task_rejects_invalid_dates(client, auth_headers):
    response = client.post(
        '/tasks/',
        json={
            'title': 'Impossible schedule',
            'description': 'Dates are reversed',
            'status': 'todo',
            'priority': 'low',
            'progress': 0,
            'start_date': '2026-04-10',
            'due_date': '2026-04-01',
        },
        headers=auth_headers,
    )
    assert response.status_code == 422
