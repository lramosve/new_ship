from starlette.websockets import WebSocketDisconnect


def test_project_management_websocket_streams_task_events(client, auth_headers):
    with client.websocket_connect('/ws/project-management?token=' + auth_headers['Authorization'].split(' ', 1)[1]) as websocket:
        connected = websocket.receive_json()
        assert connected == {'type': 'connected', 'channel': 'project-management'}

        project_response = client.post(
            '/projects/',
            json={'name': 'Realtime Project', 'description': 'Project for websocket test'},
            headers=auth_headers,
        )
        assert project_response.status_code == 201
        project_id = project_response.json()['id']

        created = client.post(
            '/tasks/',
            json={
                'title': 'Realtime task',
                'description': 'Created while websocket is open',
                'status': 'todo',
                'priority': 'medium',
                'progress': 5,
                'project_id': project_id,
            },
            headers=auth_headers,
        )
        assert created.status_code == 201
        created_task = created.json()

        event = websocket.receive_json()
        assert event['type'] == 'task.created'
        assert event['entity'] == 'task'
        assert event['task_id'] == created_task['id']
        assert event['task']['title'] == 'Realtime task'


def test_project_management_websocket_rejects_invalid_token(client):
    try:
        with client.websocket_connect('/ws/project-management?token=invalid-token'):
            raise AssertionError('websocket connection unexpectedly succeeded')
    except WebSocketDisconnect as error:
        assert error.code == 1008
