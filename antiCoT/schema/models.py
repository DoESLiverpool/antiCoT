import uuid
import re
from flask.ext.restful import fields
from sqlalchemy.exc import ArgumentError

from antiCoT import db

uuid_pattern = re.compile('[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\Z', re.I)


class Entity(db.Model):
    __tablename__ = 'entities'

    entity_summary_fields = {'entityId': fields.String(attribute='uuid'),
                             'description': fields.String}

    entity_fields = {'entityId': fields.String(attribute='uuid'),
                     'description': fields.String}

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), unique=True)
    description = db.Column(db.Text(), nullable=True)

    def __init__(self, UUID=None, description=None):
        if UUID is None:
            self.uuid = str(uuid.uuid4())
        else:
            if uuid_pattern.match(UUID) is None:
                raise ArgumentError
            else:
                self.uuid = UUID

        self.description = description

    def __repr__(self):
        return '<Entity {0}>'.format(self.uuid)
