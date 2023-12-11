import os

from flask import Flask, json
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()
db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'tasks.db'),
        TOKEN_FILE_URI=os.path.join(os.path.dirname(__file__), 'tokens.json')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # The tokens should of course not be included in the code base in real life
    app.api_tokens = json.load(open(app.config['TOKEN_FILE_URI']))

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # lets use marshmallow for serialization and SQLAlchemy for database access
    ma.init_app(app)
    db.init_app(app)

    # this enables the tasks api which is nicely seperated in its own directory
    from api.tasks import tasks
    app.register_blueprint(tasks, url_prefix='/api/v1')

    # Clear database functionality to start tests fresh
    with app.app_context():
        if app.config.get('CLEAR_DATABASE', False):
            db.drop_all()

        db.create_all()

    return app
