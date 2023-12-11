from flask import Flask, Blueprint

tasks = Blueprint("tasks", __name__)

from api.tasks import routes
from api.tasks import models
