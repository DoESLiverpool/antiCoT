from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import restful

app = Flask(__name__)
app.config.from_object('default_settings')
db = SQLAlchemy(app)
api = restful.Api(app)


import views