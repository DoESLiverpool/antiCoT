from flask import request, url_for, make_response, jsonify
from flask.ext.restful import Resource, marshal, abort
from sqlalchemy.exc import ArgumentError, IntegrityError
from AMON import db, api
from AMON.schema.models import Entity, MeteringPoint


class Entities(Resource):
    def get(self, entity_id=None):
        """
        Queries the database for the entity who's id matches the given UUID. If no UUID is given, return a summary of
        all the entities.

        :param entity_id: The UUID of the entity being requested
        :return: 200 - A JSON representation of an entity/entities
                 404 - The entity cannot be found
        """
        if entity_id is None:
            entities = Entity.query.all()
            response = jsonify({'entities': marshal(entities, Entity.summary_fields)})
        else:
            entities = Entity.query.filter(Entity.uuid == entity_id).all()
            response = jsonify({'entities': marshal(entities, Entity.response_fields)})

            if len(entities) == 0:
                abort(404, message='Entity not found')

        return response

    def post(self):
        """
        Adds a new entity to the database. Doesn't support the "?append=true" parameter. Also doesn't support updating
        an entity's list of metering points as the documentation implies, this can be achieved by re-parenting the
        metering points.

        :return: 201 - The entity was successfully created
                 400 - The parameters were malformed
                 403 - The entity already exists
        """
        entity_id = None
        description = None

        try:
            if request.headers['Content-Type'] == 'application/json':
                content = request.get_json()
                if 'entityId' in content:
                    entity_id = content['entityId'].lower()

                if 'description' in content:
                    description = content['description']
            else:
                raise ArgumentError

            entity = Entity(entity_id, description)
            db.session.add(entity)
            db.session.commit()

            return make_response(('', 201, {'Location': url_for('entities', entity_id=entity.uuid, _external=True)}))
        except ArgumentError:
            abort(400, message='Invalid entity parameters')
        except IntegrityError:
            abort(403, message='The entity already exists')

    def put(self, entity_id):
        """
        Updates an entity in the database.

        :param entity_id: The UUID of the entity being updated
        :return: 200 - The entity was updated
                 201 - A new entity was created
                 400 - The UUID was malformed
        """
        description = None

        if request.headers['Content-Type'] == 'application/json':
            content = request.get_json()

            if 'description' in content:
                description = content['description']
        else:
            abort(400, message='Invalid entity parameters')

        entity = Entity.query.filter(Entity.uuid == entity_id).first()

        if entity is None:
            try:
                entity = Entity(entity_id, description)
                db.session.add(entity)
                return make_response(('', 201, {'Location': url_for('entity', entity_id=entity.uuid, _external=True)}))
            except ArgumentError:
                abort(400, message='Invalid entity parameters')

        else:
            entity.description = description
            db.session.commit()
            return make_response('', 204)


class MeteringPoints(Resource):
    def get(self, metering_point_id=None):
        if metering_point_id is None:
            abort(400, message='Metering point id missing')

        metering_points = MeteringPoint.query.filter(MeteringPoint.uuid == metering_point_id).all()
        response = jsonify({'meteringPoints': marshal(metering_points, MeteringPoint.response_fields)})

        if len(metering_points) == 0:
            abort(404, message='Metering Point not found')

        return response

    def post(self):
        """
        Adds a new metering point to the database.

        :return: 201 - The metering point was successfully created
                 400 - The parameters were malformed
                 403 - The metering point already exists
        """
        metering_point_id = None
        description = None
        entity_id = None

        try:
            if request.headers['Content-Type'] == 'application/json':
                content = request.get_json()
                if 'meteringPointId' in content:
                    metering_point_id = content['meteringPointId'].lower()

                if 'description' in content:
                    description = content['description']

                if 'entityId' in content:
                    entity_id = content['entityId'].lower()
            else:
                raise ArgumentError

            metering_point = MeteringPoint(metering_point_id, entity_id, description)
            db.session.add(metering_point)
            db.session.commit()

            return make_response(('', 201, {'Location': url_for('meteringpoints',
                                                                metering_point_id=metering_point.uuid,
                                                                _external=True)}))
        except ArgumentError:
            abort(400, message='Invalid metering point parameters')
        except IntegrityError:
            abort(403, message='The metering point already exists')

    def put(self, metering_point_id):
        """
        Updates a metering point in the database.

        :param metering_point_id: The UUID of the metering point being updated
        :return: 200 - The metering point was updated
                 201 - A new metering point was created
                 400 - The input was malformed
        """
        description = None
        entity_id = None

        if request.headers['Content-Type'] == 'application/json':
            content = request.get_json()

            if 'description' in content:
                description = content['description']

            if 'entityId' in content:
                entity_id = content['entityId'].lower()
        else:
            abort(400, message='Invalid entity parameters')

        metering_point = MeteringPoint.query.filter(MeteringPoint.uuid == metering_point_id).first()

        if metering_point is None:
            try:
                metering_point = MeteringPoint(metering_point_id, entity_id, description)
                db.session.add(metering_point)
                return make_response(('', 201, {'Location': url_for('meteringpoints',
                                                                    metering_point_id=metering_point.uuid,
                                                                    _external=True)}))
            except ArgumentError:
                abort(400, message='Invalid entity parameters')

        else:
            metering_point.description = description

            if entity_id is not None and entity_id != metering_point.entity_id:
                # We may need to do something clever here with re-parenting this record.
                metering_point.entity_id = entity_id

            db.session.commit()
            return make_response('', 200)


api.add_resource(Entities, '/entities/<entity_id>', '/entities', endpoint='entities')
api.add_resource(MeteringPoints, '/metering-points/<metering_point_id>', '/metering-points', endpoint='meteringpoints')