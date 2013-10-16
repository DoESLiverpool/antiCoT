import uuid
import re
from flask.ext.restful import fields, marshal
from sqlalchemy.exc import ArgumentError

from AMON import db

uuid_pattern = re.compile('[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\Z', re.I)


class Entity(db.Model):
    __tablename__ = 'entities'

    uuid = db.Column(db.String(36), unique=True, primary_key=True)
    description = db.Column(db.Text, nullable=True)
    meteringPointIds = db.relationship('MeteringPoint', cascade='all', backref=db.backref('entity'))

    summary_fields = {'entityId': fields.String(attribute='uuid'),
                      'description': fields.String}

    response_fields = {'entityId': fields.String(attribute='uuid'),
                       'description': fields.String,
                       'meteringPointIds': fields.List(fields.String)}

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
    description = db.Column(db.Text, nullable=True)
    entity_id = db.Column(db.String(36), db.ForeignKey('entities.uuid'), index=True)
    devices = db.relationship('Device', cascade='all', backref=db.backref('metering_point'))

    # If not NULL, represents the location of the device in some 3D coordinate space.
    # NOTE: Not part of the AMON standard, but can be represented in the "metadata" structure.
    x = db.Column(db.Float, nullable=True)
    y = db.Column(db.Float, nullable=True)
    z = db.Column(db.Float, nullable=True)

    metadata_fields = {'x': fields.Float,
                       'y': fields.Float,
                       'z': fields.Float}

    response_fields = {'meteringPointId': fields.String(attribute='uuid'),
                       'entityId': fields.String(attribute='entity_id'),
                       'description': fields.String,
                       'metadata': fields.Nested(metadata_fields)}

    def __init__(self, UUID, entity_id, description=None):
        if uuid_pattern.match(UUID) is None:
            raise ArgumentError
        else:
            self.uuid = UUID.lower()

        if uuid_pattern.match(entity_id) is None:
            raise ArgumentError
        else:
            self.entity_id = entity_id.lower()

        self.description = description

    def __repr__(self):
        return self.uuid


class Reading(db.Model):
    __tablename__ = 'readings'

    _id = db.Column(db.Integer(), unique=True, autoincrement=True, primary_key=True)
    reading_type = db.Column(db.Text(), nullable=False)
    unit = db.Column(db.Text(), nullable=True)
    resolution = db.Column(db.Float(), nullable=True)
    accuracy = db.Column(db.Float(), nullable=True)
    period = db.Column(db.Enum('instant', 'cumulative', 'pulse'), nullable=False)
    value_min = db.Column(db.Float(), nullable=True)
    value_max = db.Column(db.Float(), nullable=True)
    correction = db.Column(db.Boolean(), nullable=True)
    corrected_unit = db.Column(db.Text(), nullable=True)
    correction_factor = db.Column(db.Float(), nullable=True)
    correction_factor_breakdown = db.Column(db.Text(), nullable=True)
    device_id = db.Column(db.String(36), db.ForeignKey('devices.uuid'), index=True)

    response_fields = {'type': fields.String(attribute='reading_type'),
                       'unit': fields.String,
                       'resolution': fields.Float,
                       'accuracy': fields.Float,
                       'period': fields.String,
                       'min': fields.Float(attribute='value_min'),
                       'max': fields.Float(attribute='value_max'),
                       'correction': fields.Boolean,
                       'correctedUnit': fields.String(attribute='corrected_unit'),
                       'correctionFactor': fields.Float(attribute='correction_factor'),
                       'correctionFactorBreakdown': fields.String(attribute='correction_factor_breakdown')}

    def __init__(self, reading_type, period):
        self.reading_type = reading_type
        self.period = period.lower()

    def __repr__(self):
        return '{0} ({1})'.format(self.reading_type, self.unit)


class Measurement(db.Model):
    __tablename__ = 'measurements'

    _id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True)
    reading_type = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, nullable=False)
    value = db.Column(db.Float, nullable=False)
    error = db.Column(db.Text, nullable=True)
    aggregated = db.Column(db.Boolean, nullable=True)
    device_id = db.Column(db.String(36), db.ForeignKey('devices.uuid'), index=True)

    response_fields = {'type': fields.String(attribute='reading_type'),
                       'timestamp': fields.DateTime,
                       'value': fields.Float,
                       'error': fields.String,
                       'aggregated': fields.Boolean}

    def __init__(self, reading_type, timestamp, value, aggregated=False):
        self.reading_type = reading_type
        self.timestamp = timestamp
        self.value = value
        self.aggregated = aggregated

    def __repr__(self):
        return '{0} [{1}] {2}'.format(self.timestamp, self.reading_type, self.value)


class Device(db.Model):
    __tablename__ = 'devices'

    uuid = db.Column(db.String(36), unique=True, primary_key=True)
    entity_id = db.Column(db.String(36), index=True)
    metering_point_id = db.Column(db.String(36), db.ForeignKey('metering_points.uuid'), index=True)
    description = db.Column(db.Text, nullable=True)
    privacy = db.Column(db.Enum('private', 'public'), nullable=False)
    measurements = db.relationship('Measurement', backref=db.backref('device'))
    readings = db.relationship('Reading', backref=db.backref('device'))


    # If not NULL, represents the location of the device in some 3D coordinate space.
    # NOTE: Not part of the AMON standard, but can be represented in the "metadata" structure. This is different from
    # the "location" attribute because that represents a location in a well-known geographic coordinate system.
    x = db.Column(db.Float, nullable=True)
    y = db.Column(db.Float, nullable=True)
    z = db.Column(db.Float, nullable=True)

    metadata_fields = {'x': fields.Float,
                       'y': fields.Float,
                       'z': fields.Float}

    response_fields = {'deviceId': fields.String(attribute='uuid'),
                       'entityId': fields.String(attribute='entity_id'),
                       'meteringPointId': fields.String(attribute='metering_point_id'),
                       'description': fields.String,
                       'privacy': fields.String,
                       'metadata': fields.Nested(metadata_fields)}

    def __init__(self, UUID, entity_id, metering_point_id, privacy, description=None):
        if uuid_pattern.match(UUID) is None:
            raise ArgumentError
        else:
            self.uuid = UUID.lower()

        if uuid_pattern.match(entity_id) is None:
            raise ArgumentError
        else:
            self.entity_id = entity_id.lower()

        if uuid_pattern.match(metering_point_id) is None:
            raise ArgumentError
        else:
            self.metering_point_id = metering_point_id.lower()

        self.privacy = privacy.lower()

        self.description = description

    def __repr__(self):
        return 'Device(UUID={0}, metering_point_id={1}, entity_id={2})'.format(self.uuid, self.metering_point_id,
                                                                               self.entity_id)

    def marshal(self):
        # metadata = marshal(self, Device.metadata_fields)
        return marshal(self, Device.response_fields)
