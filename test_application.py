import pytest
from main import app, items, history

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_add_task(client):
    items.clear()
    response = client.post('/', data={
        'newItem': 'Test Task',
        'duedate': '2030-12-31',
        'category': 'Work'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert len(items) == 1
    assert items[0]['content'] == 'Test Task'
    assert items[0]['category'] == 'Work'


def test_add_task_missing_fields(client):
    response = client.post('/', data={
        'newItem': '',
        'duedate': '2030-12-31',
        'category': 'Work'
    })
    assert response.status_code in (200, 302)


def test_add_task_missing_all_fields(client):
    # Cover possible validation branch for empty form submission
    response = client.post('/', data={
        'newItem': '',
        'duedate': '',
        'category': ''
    })
    assert response.status_code in (200, 302)


def test_edit_task(client):
    items.clear()
    client.post('/', data={
        'newItem': 'Original Task',
        'duedate': '2030-12-01',
        'category': 'House'
    })

    task_id = items[0]['id']
    response = client.post('/edit-item', data={
        'edit_id': task_id,
        'new_content': 'Updated Task'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert items[0]['content'] == 'Updated Task'


def test_edit_task_invalid_id(client):
    # Cover editing with invalid ID (non-existent)
    response = client.post('/edit-item', data={
        'edit_id': 999,
        'new_content': 'Won’t Work'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_edit_task_missing_id(client):
    # Cover editing with missing ID
    response = client.post('/edit-item', data={
        'edit_id': '',
        'new_content': 'Should Fail Gracefully'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_delete_task(client):
    items.clear()
    history.clear()

    client.post('/', data={
        'newItem': 'Task to Delete',
        'duedate': '2030-12-15',
        'category': 'School'
    })

    task_id = items[0]['id']
    response = client.post('/delete-item', data={
        'checkbox': task_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert len(items) == 0
    assert len(history) == 1
    assert history[0]['status'] == 'Deleted'


def test_delete_task_invalid_id(client):
    # Cover deleting a task with invalid ID
    response = client.post('/delete-item', data={
        'checkbox': 99999
    }, follow_redirects=True)
    assert response.status_code == 200


def test_complete_task(client):
    items.clear()
    history.clear()

    client.post('/', data={
        'newItem': 'Task to Complete',
        'duedate': '2030-10-01',
        'category': 'Shopping'
    })

    task_id = items[0]['id']
    response = client.post('/complete-item', data={
        'complete_id': task_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert len(items) == 0
    assert len(history) == 1
    assert history[0]['status'] == 'Completed'


def test_complete_task_invalid_id(client):
    # Cover completing task with invalid ID
    response = client.post('/complete-item', data={
        'complete_id': 99999
    }, follow_redirects=True)
    assert response.status_code == 200


def test_task_priority_ordering(client):
    items.clear()

    client.post('/', data={
        'newItem': 'Later Task',
        'duedate': '2031-12-31',
        'category': 'Other'
    })

    client.post('/', data={
        'newItem': 'Sooner Task',
        'duedate': '2030-01-01',
        'category': 'Other'
    })

    assert items[0]['content'] == 'Sooner Task'
    assert items[1]['content'] == 'Later Task'


def test_history_view(client):
    history.clear()
    items.clear()

    client.post('/', data={
        'newItem': 'History Test Task',
        'duedate': '2035-01-01',
        'category': 'Test'
    })
    task_id = items[0]['id']

    client.post('/complete-item', data={
        'complete_id': task_id
    })

    response = client.get('/')
    assert response.status_code == 200
    assert b'History' in response.data
    assert b'Completed' in response.data


def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Todo' in response.data or b'Tasks' in response.data
