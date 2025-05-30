import testing
from main import app, items, history

@testing.fixture
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
    assert response.status_code == 302 or response.status_code == 200


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
    assert items[0]['content'] == 'Updated Task'


def test_edit_task_invalid_id(client):
    response = client.post('/edit-item', data={
        'edit_id': 999,
        'new_content': 'Won’t Work'
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

    assert len(items) == 0
    assert len(history) == 1
    assert history[0]['status'] == 'Deleted'


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

    assert len(items) == 0
    assert len(history) == 1
    assert history[0]['status'] == 'Completed'


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
    assert b'History' in response.data
    assert b'Completed' in response.data
