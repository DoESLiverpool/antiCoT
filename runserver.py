import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import restful

from default_settings import LOG_LEVEL

import AMON

logging.basicConfig(format='%(asctime)s.%(msecs).03dZ | %(levelname)s | %(message)s',
                        level=getattr(logging, LOG_LEVEL, logging.INFO),
                        datefmt='%Y-%m-%dT%H:%M:%S')

logging.info('AntiCoT v0.1 starting')

app = Flask(__name__)
app.config.from_object('default_settings')
db = SQLAlchemy(app)
api = restful.Api(app)

AMON.init(app, db, api)

db.create_all()
app.run()