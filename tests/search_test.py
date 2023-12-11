from flask import json

from tests.conftest import client


# Add tasks to our database from the provided sample tasks. These tasks were generated using chatGPT so that they are
# complex and similar enough that ranking them does something.
def add_records(client):
    json_sample = json.load(open('sample_tasks.json'))

    for record in json_sample:
        response = client.post('api/v1/task', data={
            'title': record['Task Title'],
            'description': record['Description']
        })

        assert response.status_code == 200

    return


def test_find(client):
    add_records(client)

    response = client.get('api/v1/tasks/find', data={
        'query': 'Effects of mindfulness and gratitude on mental well-being'
    })

    assert response.status_code == 200
    assert len(response.json) == 2

    assert response.json[0]['id'] == 8
    assert response.json[1]['id'] == 3
