from datetime import date, timedelta

from jose import jwt


def test_analytics_overview_returns_aggregated_metrics(client, auth_headers):
    project_response = client.post(
        '/projects/',
        json={'name': 'Analytics Project', 'description': 'Project for analytics validation'},
        headers=auth_headers,
    )
    assert project_response.status_code == 201
    project_id = project_response.json()['id']

    token = auth_headers['Authorization'].split(' ', 1)[1]
    assignee_id = int(jwt.get_unverified_claims(token)['sub'])

    today = date.today()

    payloads = [
        {
            'title': 'Completed urgent task',
            'description': 'Finished work item',
            'status': 'done',
            'priority': 'urgent',
            'progress': 100,
            'start_date': str(today - timedelta(days=3)),
            'due_date': str(today - timedelta(days=1)),
            'project_id': project_id,
            'assignee_id': assignee_id,
        },
        {
            'title': 'In progress scheduled task',
            'description': 'Active work item',
            'status': 'in_progress',
            'priority': 'high',
            'progress': 50,
            'start_date': str(today),
            'due_date': str(today + timedelta(days=3)),
            'project_id': project_id,
            'assignee_id': assignee_id,
        },
        {
            'title': 'Overdue unassigned task',
            'description': 'Past due work item',
            'status': 'todo',
            'priority': 'low',
            'progress': 0,
            'start_date': str(today - timedelta(days=5)),
            'due_date': str(today - timedelta(days=2)),
            'project_id': None,
            'assignee_id': None,
        },
    ]

    for payload in payloads:
        created = client.post('/tasks/', json=payload, headers=auth_headers)
        assert created.status_code == 201

    response = client.get('/analytics/overview')
    assert response.status_code == 200

    payload = response.json()
    summary = payload['summary']
    assert summary == {
        'total_tasks': 3,
        'completed_tasks': 1,
        'in_progress_tasks': 1,
        'overdue_tasks': 1,
        'completion_rate': 33,
        'average_progress': 50,
    }

    status_distribution = {item['status']: item['count'] for item in payload['status_distribution']}
    assert status_distribution == {
        'todo': 1,
        'in_progress': 1,
        'in_review': 0,
        'done': 1,
    }

    priority_distribution = {item['priority']: item['count'] for item in payload['priority_distribution']}
    assert priority_distribution == {
        'low': 1,
        'medium': 0,
        'high': 1,
        'urgent': 1,
    }

    project_progress = {item['project_name']: item for item in payload['project_progress']}
    assert project_progress['Analytics Project']['total_tasks'] == 2
    assert project_progress['Analytics Project']['completed_tasks'] == 1
    assert project_progress['Analytics Project']['average_progress'] == 75
    assert project_progress['Analytics Project']['completion_rate'] == 50
    assert project_progress['Unassigned']['total_tasks'] == 1
    assert project_progress['Unassigned']['completed_tasks'] == 0
    assert project_progress['Unassigned']['average_progress'] == 0
    assert project_progress['Unassigned']['completion_rate'] == 0

    assert len(payload['task_trends']) >= 1
    for point in payload['task_trends']:
        assert {'date', 'created_tasks', 'completed_tasks'} <= point.keys()
