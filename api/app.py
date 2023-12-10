import os

from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

@app.route('/api/v1/status', methods=['GET'])
def get_status():
    return Response('OK', status=200)



if __name__ == '__main__':
    app.run(debug=True)
