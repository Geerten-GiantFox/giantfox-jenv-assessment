from datetime import datetime

from sklearn.metrics.pairwise import cosine_similarity

from api import db
from api.tasks.models import Task, TaskSchema
from flask import Response, request
from api.tasks import tasks
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer


# CRUD
@tasks.route('/tasks', methods=['GET'])
def get_tasks():
    request_data = request.form.to_dict()

    # The filtering is optional but if there is a value for a date filter it must be in the correct format. Making an
    # assumption about what was meant would be confusing for the user.
    start_date = datetime(1900, 1, 1)
    if 'start_date' in request_data:
        try:
            start_date = datetime.strptime(request_data['start_date'], '%Y-%m-%d')
        except ValueError:
            return Response(response='Invalid date format. Please enter date in YYYY-MM-DD format', status=400)

    end_date = datetime.now()
    if 'end_date' in request_data:
        try:
            end_date = datetime.strptime(request_data['end_date'], '%Y-%m-%d')
        except ValueError:
            return Response(response='Invalid date format. Please enter date in YYYY-MM-DD format', status=400)

    # Here we should also check for e.g. <1 but I dont have a lot of time
    per_page = request.form.get('per_page', default=Task.query.count(), type=int)
    page = request.form.get('page', default=1, type=int)

    relevant_tasks = Task.query.filter(Task.date_created.between(start_date, end_date)).paginate(page=page,
                                                                                                 per_page=per_page,
                                                                                                 error_out=False)

    tasks_schema = TaskSchema(many=True)
    return tasks_schema.jsonify(relevant_tasks)


@tasks.route('/task/<int:id>', methods=['GET'])
def get_task(id):
    task_schema = TaskSchema(many=False)
    task = db.session.get(Task, id)

    if task is None:
        return Response(response="Task not found", status=404)

    return task_schema.jsonify(task)


@tasks.route('/task', methods=['POST'])
def create_task():
    # check if required data is included
    request_data = request.form.to_dict()
    if 'title' not in request_data or 'description' not in request_data:
        return Response(response="title and description are required.", status=400)

    task = Task(title=request_data['title'], description=request_data['description'])

    db.session.add(task)
    db.session.commit()

    task_schema = TaskSchema(many=False)

    return task_schema.jsonify(task)


@tasks.route('/task/<int:id>', methods=['PUT'])
def update_task(id):
    task = db.session.get(Task, id)

    if task is None:
        return Response(response="Task not found", status=404)

    request_data = request.form.to_dict()
    if 'title' in request_data:
        task.title = request_data['title']

    if 'description' in request_data:
        task.description = request_data['description']

    if 'completed' in request_data:
        # TODO: add type checking
        task.completed = request_data['completed'].lower() == 'true'

    db.session.commit()

    return Response(response="Task updated successfully", status=200)


@tasks.route('/task/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = db.session.get(Task, id)

    if task is None:
        return Response(response="Task not found", status=404)

    db.session.delete(task)
    db.session.commit()
    return Response(response="Task deleted successfully", status=200)


# Lets do something slightly less basic for finding tasks.
@tasks.route('tasks/find', methods=['GET'])
def find_tasks():
    request_data = request.form.to_dict()

    # First check if all necessary data is available
    if "query" not in request_data:
        return Response(response="description required.", status=400)

    # Get all tasks and convert them to the right format
    all_tasks = Task.query.all()
    all_tasks_text = [t.title + " " + t.description for t in all_tasks]

    # Only use the search term words as vocab (presumably not a lot so this is faster)
    vocab = request_data['query'].lower().split()
    vectorizer = TfidfVectorizer(vocabulary=vocab, stop_words='english')
    transformed_tasks = vectorizer.fit_transform(all_tasks_text)

    # Transform the query using the same weights
    query = vectorizer.transform([request_data['query']])

    # Calculate the similarities and threshold them
    cosine_similarities = cosine_similarity(query, transformed_tasks).flatten()
    mask = cosine_similarities > 0.5

    # Sort the tasks based on how well they fit the query, only return the good matches
    sorted_indices = np.argsort(-cosine_similarities[mask])
    sorted_tasks = [all_tasks[i] for i in np.where(mask)[0][sorted_indices]]

    task_schema = TaskSchema(many=True)
    return task_schema.jsonify(sorted_tasks)
