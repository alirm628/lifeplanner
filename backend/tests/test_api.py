import os
from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

os.environ['DATABASE_URL'] = 'sqlite:///./test_lifeplanner.db'
os.environ['ADMIN_EMAIL'] = 'admin@test.dev'
os.environ['ADMIN_PASSWORD'] = 'password123'
os.environ['SECRET_KEY'] = 'test-secret'

from app.main import app  # noqa: E402


@pytest.fixture(scope='module')
def client():
    db_path = 'test_lifeplanner.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    with TestClient(app) as c:
        yield c

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass


def _auth_headers(client: TestClient):
    res = client.post('/api/v1/auth/login', json={'email': 'admin@test.dev', 'password': 'password123'})
    assert res.status_code == 200
    token = res.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_auth_me(client: TestClient):
    headers = _auth_headers(client)
    res = client.get('/api/v1/auth/me', headers=headers)
    assert res.status_code == 200
    assert res.json()['email'] == 'admin@test.dev'


def test_category_event_scheduler_flow(client: TestClient):
    headers = _auth_headers(client)

    cat_res = client.post(
        '/api/v1/categories',
        headers=headers,
        json={
            'name': 'School',
            'color': '#0ea5e9',
            'priority': 2,
            'weekly_target_hours': 4,
            'min_session_minutes': 60,
            'max_session_minutes': 120,
            'preferred_days': 'mon,wed,fri',
            'preferred_times': 'morning',
        },
    )
    assert cat_res.status_code == 200
    category_id = cat_res.json()['id']

    now = datetime.now(UTC).replace(tzinfo=None)
    fixed_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    fixed_end = fixed_start + timedelta(hours=2)

    event_res = client.post(
        '/api/v1/events',
        headers=headers,
        json={
            'title': 'Class',
            'start_time': fixed_start.isoformat(),
            'end_time': fixed_end.isoformat(),
            'event_type': 'fixed',
            'lock_mode': 'locked',
            'category_id': category_id,
        },
    )
    assert event_res.status_code == 200

    week_start = date.today() - timedelta(days=date.today().weekday())
    gen_res = client.post(
        '/api/v1/scheduler/generate',
        headers=headers,
        json={'week_start': week_start.isoformat(), 'mode': 'full_auto'},
    )
    assert gen_res.status_code == 200
    run_id = gen_res.json()['run_id']
    assert len(gen_res.json()['proposed_events']) >= 1

    apply_res = client.post('/api/v1/scheduler/apply', headers=headers, json={'run_id': run_id})
    assert apply_res.status_code == 200

    list_res = client.get('/api/v1/events', headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
    fixed_count = len([event for event in list_res.json() if event['event_type'] == 'fixed'])
    assert fixed_count == 1
    assert 'diagnostics' in gen_res.json()


def test_cannot_move_fixed_or_locked_event(client: TestClient):
    headers = _auth_headers(client)
    list_res = client.get('/api/v1/events', headers=headers)
    fixed_event = next(event for event in list_res.json() if event['event_type'] == 'fixed')
    original_start = datetime.fromisoformat(fixed_event['start_time'])

    res = client.patch(
        f"/api/v1/events/{fixed_event['id']}",
        headers=headers,
        json={'start_time': (original_start + timedelta(hours=1)).isoformat()},
    )
    assert res.status_code == 400


def test_tasks_goals_templates_and_search(client: TestClient):
    headers = _auth_headers(client)

    task_res = client.post(
        '/api/v1/tasks',
        headers=headers,
        json={'title': 'Read chapter', 'priority': 2, 'status': 'todo', 'estimated_minutes': 45},
    )
    assert task_res.status_code == 200

    goal_res = client.post(
        '/api/v1/goals',
        headers=headers,
        json={'title': 'Study target', 'target_hours': 5, 'status': 'active'},
    )
    assert goal_res.status_code == 200

    template_res = client.post(
        '/api/v1/templates',
        headers=headers,
        json={'name': 'Week Plan', 'description': 'sample', 'template_data': {'events': []}},
    )
    assert template_res.status_code == 200

    search_res = client.get('/api/v1/search', headers=headers, params={'q': 'Study'})
    assert search_res.status_code == 200
    assert isinstance(search_res.json().get('results'), list)


def test_analytics_endpoints(client: TestClient):
    headers = _auth_headers(client)
    summary = client.get('/api/v1/analytics/summary', headers=headers)
    breakdown = client.get('/api/v1/analytics/breakdown', headers=headers)
    trends = client.get('/api/v1/analytics/trends', headers=headers)
    heatmap = client.get('/api/v1/analytics/heatmap', headers=headers)

    assert summary.status_code == 200
    assert breakdown.status_code == 200
    assert trends.status_code == 200
    assert heatmap.status_code == 200
