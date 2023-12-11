from tests.conftest import client


def add_record(client):
    return client.post('api/v1/task', data={
        'title': 'Unit Test Title',
        'description': 'Unit Test Description'
    })


# test that the test provides a clean db
def test_db_empty(client):
    response = client.get('api/v1/tasks')

    assert response.status_code == 200
    assert len(response.json) == 0


def test_get(client):
    response = add_record(client)

    assert response.status_code == 200

    response = client.get('api/v1/task/1')

    assert response.status_code == 200
    assert response.json['id'] == 1
    assert response.json['title'] == 'Unit Test Title'
    assert response.json['description'] == 'Unit Test Description'
    assert response.json['completed'] is False


def test_get_multiple(client):
    for i in range(10):
        response = add_record(client)

        assert response.status_code == 200

    response = client.get('api/v1/tasks')

    assert response.status_code == 200
    assert len(response.json) == 10


def test_get_multiple_pagination(client):
    for i in range(10):
        response = add_record(client)

        assert response.status_code == 200

    response = client.get('api/v1/tasks', data={
        'per_page': 4})

    assert response.status_code == 200
    assert len(response.json) == 4

    response = client.get('api/v1/tasks', data={
        'per_page': 4,
        'page': 2})

    assert response.status_code == 200
    assert len(response.json) == 4

    response = client.get('api/v1/tasks', data={
        'per_page': 4,
        'page': 3})

    assert response.status_code == 200
    assert len(response.json) == 2


def test_update(client):
    response = add_record(client)

    assert response.status_code == 200

    response = client.put('api/v1/task/1', data={
        'title': 'Updated Unit Test Title',
        'description': 'Updated Unit Test Description',
        'completed': True
    })

    assert response.status_code == 200

    response = client.get('api/v1/task/1')

    assert response.status_code == 200

    assert response.json['id'] == 1
    assert response.json['title'] == 'Updated Unit Test Title'
    assert response.json['description'] == 'Updated Unit Test Description'
    assert response.json['completed']


def test_delete(client):
    response = add_record(client)

    assert response.status_code == 200

    response = client.delete('api/v1/task/1')

    assert response.status_code == 200

    response = client.get('api/v1/task/1')

    assert response.status_code == 404
