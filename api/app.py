import os

from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///' + os.path.join(basedir, 'tasks.db')

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String())


with app.app_context():
    db.create_all()

ma = Marshmallow(app)


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True


# sanity check
@app.route('/api/v1/status', methods=['GET'])
def get_status():
    return Response('OK', status=200)


# CRUD
@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    tasks_schema = TaskSchema(many=True)
    all_tasks = Task.query.all()

    return tasks_schema.jsonify(all_tasks)


@app.route('/api/v1/task/<int:id>', methods=['GET'])
def get_task(id):
    task_schema = TaskSchema(many=False)
    task = Task.query.get(id)

    if task is None:
        return Response(response="Task not found", status=404)

    return task_schema.jsonify(task)


@app.route('/api/v1/task', methods=['POST'])
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


@app.route('/api/v1/task/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)

    if task is None:
        return Response(response="Task not found", status=404)

    request_data = request.form.to_dict()
    if 'title' in request_data:
        task.title = request_data['title']

    if 'description' in request_data:
        task.description = request_data['description']

    db.session.commit()

    return Response(response="Task updated successfully", status=200)


@app.route('/api/v1/task/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)

    if task is None:
        return Response(response="Task not found", status=404)

    db.session.delete(task)
    db.session.commit()
    return Response(response="Task deleted successfully", status=200)


if __name__ == '__main__':
    app.run(debug=True)
