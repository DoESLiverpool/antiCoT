import uuid
import re
from flask.ext.restful import fields
from sqlalchemy.exc import ArgumentError

from antiCoT import db

uuid_pattern = re.compile('[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\Z', re.I)


class Entity(db.Model):
    __tablename__ = 'entities'

    uuid = db.Column(db.String(36), unique=True, primary_key=True)
    description = db.Column(db.Text(), nullable=True)
    meteringPointIds = db.relationship('MeteringPoint', cascade='all,delete', backref=db.backref('entity'))

    summary_fields = {'entityId': fields.String(attribute='uuid'),
                      'description': fields.String}

    fields = {'entityId': fields.String(attribute='uuid'),
              'description': fields.String,
              'meteringPointIds': fields.List(fields.String),
    }

    def __init__(self, UUID=None, description=None):
        if UUID is None:
            self.uuid = str(uuid.uuid4()).lower()
        else:
            if uuid_pattern.match(UUID) is None:
                raise ArgumentError
            else:
                self.uuid = UUID.lower()

        self.description = description

    def __repr__(self):
        return self.uuid


class MeteringPoint(db.Model):
    __tablename__ = 'metering_points'

    uuid = db.Column(db.String(36), unique=True, primary_key=True)
    description = db.Column(db.Text(), nullable=True)
    entity_id = db.Column(db.String, db.ForeignKey('entities.uuid'))

    fields = {'meteringPointId': fields.String(attribute='uuid'),
              'entityId': fields.String(attribute='entity'),
              'description': fields.String}

    def __init__(self, UUID, entity_id, description=None):
        self.uuid = UUID.lower()
        self.entity_id = entity_id.lower()
        self.description = description

    def __repr__(self):
        return self.uuid