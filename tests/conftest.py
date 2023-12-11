import os

import pytest
import pathlib
from api import create_app


@pytest.fixture
def app():
    db_path = pathlib.Path(os.path.dirname(__file__)) / 'test.db'

    app = create_app(dict(TESTING=True,
                          SQLALCHEMY_DATABASE_URI='sqlite:///' + str(db_path),
                          CLEAR_DATABASE=True))

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
