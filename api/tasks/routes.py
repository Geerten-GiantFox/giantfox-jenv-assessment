from api import db
from api.tasks.models import Task, TaskSchema
from flask import Response, request
from api.tasks import tasks


# CRUD
@tasks.route('/tasks', methods=['GET'])
def get_tasks():
    tasks_schema = TaskSchema(many=True)
    all_tasks = Task.query.all()

    return tasks_schema.jsonify(all_tasks)

@tasks.route('/tasks/page/<int:page>', methods=['GET'])
def get_tasks_page(page):
    tasks_schema = TaskSchema(many=True)
    all_tasks = Task.query.paginate(page=page, per_page=5, error_out=False)

    return tasks_schema.jsonify(all_tasks)


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


