import json
from urllib import request

BASE_URL = 'http://127.0.0.1:8000'


def call(path: str, method: str, payload: dict | None = None) -> str:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {'Content-Type': 'application/json'} if payload is not None else {}
    req = request.Request(f'{BASE_URL}{path}', data=data, headers=headers, method=method)
    with request.urlopen(req) as response:
        return response.read().decode()


created = call(
    '/projects/',
    'POST',
    {'name': 'Frontend CRUD Smoke Test', 'description': 'created from integration verification'},
)
print(created)
project_id = json.loads(created)['id']

updated = call(
    f'/projects/{project_id}',
    'PUT',
    {'name': 'Frontend CRUD Smoke Test Updated', 'description': 'updated from integration verification'},
)
print(updated)

deleted = call(f'/projects/{project_id}', 'DELETE')
print(deleted)
