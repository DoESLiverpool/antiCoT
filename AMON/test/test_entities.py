import logging
from fixture import SQLAlchemyFixture
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.testing import TestCase
from flask.ext import restful

import AMON


class TestEntities(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    JSON_AS_ASCII = False

    def create_app(self):
        logging.basicConfig(format='%(asctime)s.%(msecs).03dZ | %(levelname)s | %(message)s',
                            level='DEBUG',
                            datefmt='%Y-%m-%dT%H:%M:%S')

        app = Flask(__name__)
        app.config.from_object(self)
        self.api = restful.Api(app)
        self.db = SQLAlchemy(app)
        AMON.init(app, self.db, self.api)

        return app

    def setUp(self):
        self.db.create_all()
        # self.dbfixture = SQLAlchemyFixture(env={'EntityData': AMON.Entity}, engine=self.db)

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_get_all(self):
        rv = self.client.get('/amon/entities')
        self.assert200(rv)

    def test_get_unknown(self):
        rv = self.client.get('/amon/entities/some_unknown_entity_uuid')
        self.assert404(rv)
