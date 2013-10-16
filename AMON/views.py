from flask import request, url_for, make_response, jsonify
from flask.ext.restful import Resource, marshal, abort
from sqlalchemy.exc import ArgumentError, IntegrityError
from werkzeug.exceptions import BadRequest
from AMON import db, api
from models import Entity, MeteringPoint


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
                abort(404, message='Entity not found', status='ERROR')

        return response

    def post(self):
        """
        Adds a new entity to the database. Doesn't support the "?append=true" parameter. Also doesn't support updating
        an entity's list of metering points as the documentation implies, this can be achieved by re-parenting the
        metering points.

        :return: 201 - The entity was successfully created
                 400 - The parameters were malformed, or the message body was empty
                 403 - The entity already exists
                 415 - The content type is unsupported
        """

        try:
            if request.json is None:
                abort(415, message='Unsupported Content-Type. Got \'{0}\', '
                                   'expected \'application/json\''.format(request.headers['Content-Type']),
                      status='ERROR')

            entity = Entity(request.json.get('entityId'), request.json.get('description'))
            db.session.add(entity)
            db.session.commit()

            return make_response((jsonify({'status': 'OK'}), 201,
                                  {'Location': url_for('entities', entity_id=entity.uuid, _external=True)}))

        except ArgumentError:
            abort(400, message='Invalid entity parameters', status='INVALID')
        except IntegrityError:
            abort(403, message='The entity already exists', status='ERROR')
        except BadRequest:
            abort(400, message='The message body was empty', status='INVALID')

    def put(self, entity_id=None):
        """
        Updates an entity in the database.

        :param entity_id: The UUID of the entity being updated
        :return: 200 - The entity was updated
                 400 - The message body was empty
                 404 - The UUID doesn't exist in the database
                 415 - The content type is unsupported
        """

        try:
            if request.json is None:
                    abort(415, message='Unsupported Content-Type. Got \'{0}\', '
                                       'expected \'application/json\''.format(request.headers['Content-Type']),
                          status='ERROR')

            entity = Entity.query.filter(Entity.uuid == entity_id).first()

            if entity is None:
                abort(404, message='Unknown UUID \'{0}\''.format(entity_id), status='ERROR')
            else:
                entity.description = request.json.get('description')
                db.session.commit()
                return jsonify({'status': 'OK'})
        except BadRequest:
            abort(400, message='The message body was empty', status='INVALID')


class MeteringPoints(Resource):
    def get(self, metering_point_id=None):
        """
        Queries the database for the metering point who's id matches the given UUID.

        :param metering_point_id: The UUID of the metering point being requested
        :return: 200 - A JSON representation of an metering point
                 400 - The parameters were malformed
                 404 - The metering point cannot be found
        """
        if metering_point_id is None:
            abort(400, message='Metering point id missing', status='ERROR')

        metering_points = MeteringPoint.query.filter(MeteringPoint.uuid == metering_point_id).all()

        if len(metering_points) == 0:
            abort(404, message='Metering Point not found', status='ERROR')

        return jsonify({'meteringPoints': marshal(metering_points, MeteringPoint.response_fields)})

    def post(self):
        """
        Adds a new metering point to the database.

        :return: 201 - The metering point was successfully created
                 400 - The parameters were malformed, or the message body was empty
                 403 - The metering point already exists
                 415 - The content type is unsupported
        """

        try:
            if request.json is None:
                abort(415, message='Unsupported Content-Type. Got \'{0}\', '
                                   'expected \'application/json\''.format(request.headers['Content-Type']),
                      status='ERROR')

            metering_point = MeteringPoint(request.json.get('meteringPointId'),
                                           request.json.get('entityId'), request.json.get('description'))
            db.session.add(metering_point)
            db.session.commit()

            response_headers = {'Location': url_for('meteringpoints', metering_point_id=metering_point.uuid,
                                                    _external=True)}
            return make_response((jsonify({'status': 'OK'}), 201, response_headers))
        except ArgumentError:
            abort(400, message='Invalid metering point parameters', status='INVALID')
        except IntegrityError:
            abort(403, message='The metering point already exists', status='ERROR')
        except BadRequest:
            abort(400, message='The message body was empty', status='INVALID')

    # Default metering_point_id to None otherwise a 500 error is raised before we get here. This way we can handle the
    # error more gracefully.
    def put(self, metering_point_id=None):
        """
        Updates a metering point in the database.

        :param metering_point_id: The UUID of the metering point being updated
        :return: 200 - The metering point was updated
                 400 - The message body was empty
                 404 - The UUID doesn't exist in the database
                 415 - The content type is unsupported
        """

        try:
            if request.json is None:
                    abort(415, message='Unsupported Content-Type. Got \'{0}\', '
                                       'expected \'application/json\''.format(request.headers['Content-Type']),
                          status='ERROR')

            metering_point = MeteringPoint.query.filter(MeteringPoint.uuid == metering_point_id).first()

            if metering_point is None:
                abort(404, message='Unknown UUID \'{0}\''.format(metering_point_id), status='ERROR')
            else:
                metering_point.description = request.json.get('description')

                entity_id = request.json.get('entityId')

                if entity_id is not None and entity_id != metering_point.entity_id:
                    # We may need to do something clever here with re-parenting this record.
                    metering_point.entity_id = entity_id

                db.session.commit()
                return jsonify({'status': 'OK'})
        except BadRequest:
            abort(400, message='The message body was empty', status='INVALID')


api.add_resource(Entities, '/amon/entities/<entity_id>', '/amon/entities', endpoint='entities')
api.add_resource(MeteringPoints, '/amon/metering-points/<metering_point_id>', '/amon/metering-points',
                 endpoint='meteringpoints')