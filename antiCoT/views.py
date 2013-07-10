from flask import request, url_for, make_response, jsonify
from flask.ext.restful import Resource, reqparse, marshal, abort
from sqlalchemy.exc import ArgumentError, IntegrityError
from antiCoT import db, api
from antiCoT.schema.models import Entity


# Initialise the Flask-RESTful argument parser.
parser = reqparse.RequestParser()
parser.add_argument('entityId', type=str)
parser.add_argument('description', type=str)


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
            # entities = db.session.query(Entity.uuid).all()
            entities = Entity.query.all()
            response = jsonify({'entities': marshal(entities, Entity.entity_summary_fields)})
        else:
            entities = Entity.query.filter(Entity.uuid == entity_id).all()
            response = jsonify({'entities': marshal(entities, Entity.entity_fields)})

        if len(entities) == 0:
            abort(404, message='Entity not found')

        return response

    def post(self):
        """
        Adds a new entity to the database.

        :return: 201 - The entity was successfully created
                 400 - The parameters were malformed
                 403 - The entity already exists
        """
        entity_id = None
        description = None

        if request.headers['Content-Type'] == 'application/json':
            content = request.get_json()
            if 'entityId' in content:
                entity_id = content['entityId']

            if 'description' in content:
                description = content['description']
        else:
            args = parser.parse_args()
            entity_id = args['entityId']
            description = args['description']

        try:
            entity = Entity(entity_id, description)
            db.session.add(entity)
            db.session.commit()

            return make_response(('', 201, {'Location': url_for('entity', entity_id=entity.uuid, _external=True)}))
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
        elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            if 'description' in request.form:
                description = request.form['description']

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

    def delete(self, entity_id):
        """
        Removes an entity from the database.

        :param entity_id: The UUID of the entity being deleted
        :return: 200 - The
        """
        the_entity = Entity.query.filter(Entity.uuid == entity_id).first()

        if the_entity is None:
            abort(404, message='Unknown entityId')

        db.session.delete(the_entity)
        db.session.commit()
        return make_response('', 204)

api.add_resource(Entities, '/entity/<entity_id>', '/entity', endpoint='entity')
