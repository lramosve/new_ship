def seed_project_management_data(client, auth_headers):
    project_alpha = client.post(
        '/projects/',
        json={'name': 'Alpha Delivery', 'description': 'Primary project'},
        headers=auth_headers,
    )
    assert project_alpha.status_code == 201
    project_alpha_id = project_alpha.json()['id']

    project_beta = client.post(
        '/projects/',
        json={'name': 'Beta Launch', 'description': 'Secondary project'},
        headers=auth_headers,
    )
    assert project_beta.status_code == 201
    project_beta_id = project_beta.json()['id']

    alex = client.post(
        '/users/',
        json={'name': 'Alex Builder', 'email': 'alex.builder@example.com', 'password': 'password123'},
    )
    assert alex.status_code == 201
    alex_id = alex.json()['id']

    sam = client.post(
        '/users/',
        json={'name': 'Sam Planner', 'email': 'sam.planner@example.com', 'password': 'password123'},
    )
    assert sam.status_code == 201
    sam_id = sam.json()['id']

    task_payloads = [
        {
            'title': 'Define backlog',
            'description': 'Prepare initial task list',
            'status': 'todo',
            'priority': 'medium',
            'progress': 10,
            'start_date': '2026-03-24',
            'due_date': '2026-03-28',
            'project_id': project_alpha_id,
            'assignee_id': alex_id,
        },
        {
            'title': 'Build API',
            'description': 'Create task endpoints',
            'status': 'in_progress',
            'priority': 'high',
            'progress': 55,
            'start_date': '2026-03-25',
            'due_date': '2026-04-01',
            'project_id': project_alpha_id,
            'assignee_id': alex_id,
        },
        {
            'title': 'Review UI',
            'description': 'Check kanban interactions',
            'status': 'in_review',
            'priority': 'urgent',
            'progress': 80,
            'start_date': '2026-03-27',
            'due_date': '2026-04-03',
            'project_id': project_beta_id,
            'assignee_id': sam_id,
        },
        {
            'title': 'Release milestone',
            'description': 'Ship project dashboard',
            'status': 'done',
            'priority': 'high',
            'progress': 100,
            'start_date': '2026-03-20',
            'due_date': '2026-03-26',
            'project_id': project_beta_id,
            'assignee_id': None,
        },
    ]

    created_ids = []
    for payload in task_payloads:
        response = client.post('/tasks/', json=payload, headers=auth_headers)
        assert response.status_code == 201
        created_ids.append(response.json()['id'])

    return {
        'project_alpha_id': project_alpha_id,
        'project_beta_id': project_beta_id,
        'alex_id': alex_id,
        'sam_id': sam_id,
        'task_ids': created_ids,
    }


def test_task_filters_support_project_assignment_and_schedule_queries(client, auth_headers):
    seeded = seed_project_management_data(client, auth_headers)

    by_project = client.get(f"/tasks/?project_id={seeded['project_alpha_id']}")
    assert by_project.status_code == 200
    assert by_project.json()['total'] == 2

    by_assignee = client.get(f"/tasks/?assignee_id={seeded['alex_id']}")
    assert by_assignee.status_code == 200
    assert by_assignee.json()['total'] == 2

    by_status = client.get('/tasks/?status=in_review')
    assert by_status.status_code == 200
    payload = by_status.json()
    assert payload['total'] == 1
    assert payload['items'][0]['title'] == 'Review UI'

    scheduled_only = client.get('/tasks/?scheduled_only=true')
    assert scheduled_only.status_code == 200
    assert scheduled_only.json()['total'] == 4


def test_project_management_overview_returns_kanban_gantt_and_assignment_metrics(client, auth_headers):
    seed_project_management_data(client, auth_headers)

    response = client.get('/project-management/overview')
    assert response.status_code == 200
    payload = response.json()

    assert payload['summary']['total_projects'] == 2
    assert payload['summary']['total_tasks'] == 4
    assert payload['summary']['unassigned_tasks'] == 1
    assert payload['summary']['completed_tasks'] == 1
    assert payload['summary']['completion_rate'] == 25

    kanban = {column['status']: column for column in payload['kanban']}
    assert kanban['todo']['count'] == 1
    assert kanban['in_progress']['count'] == 1
    assert kanban['in_review']['count'] == 1
    assert kanban['done']['count'] == 1

    assert payload['timeline']['start_date'] == '2026-03-20'
    assert payload['timeline']['end_date'] == '2026-04-03'
    assert payload['timeline']['total_days'] == 15

    gantt_titles = [entry['task']['title'] for entry in payload['gantt']]
    assert gantt_titles == ['Release milestone', 'Define backlog', 'Build API', 'Review UI']

    workloads = {entry['assignee_name']: entry for entry in payload['assignment_workload']}
    assert workloads['Alex Builder']['total_tasks'] == 2
    assert workloads['Alex Builder']['avg_progress'] == 32
    assert workloads['Sam Planner']['in_progress_tasks'] == 1
    assert workloads['Unassigned']['completed_tasks'] == 1
