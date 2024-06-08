#!/usr/bin/python3
"""defines state method that all default restful api actions"""
from models.state import State
from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage


@app_views.route('/states', strict_slashes=False)
def get_states():
    """retrieves all states"""
    states = storage.all(State).values()
    list_state = [state.to_dict() for state in states]
    return jsonify(list_state)


@app_views.route('/states/<state_id>', strict_slashes=False)
def get_state_obj(state_id):
    """retrieves a state objects"""
    state = storage.get(State, state_id)

    if state:
        return jsonify(state.to_dict())
    else:
        abort(404)


@app_views.route('/states/<state_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_state_obj(state_id):
    """deletes a state objects"""
    state = storage.get(State, state_id)
    if state:
        storage.delete(state)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """creates state objects"""
    if request.content_type != 'application/json':
        return abort(400, "Not a JSON")
    if not request.get_json():
        return abort(400, "Not a JSON")
    kwargs = request.get_json()

    if "name" not in kwargs:
        return abort(400, "Missing name")
    state = State(**kwargs)
    state.save()
    return jsonify(state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    """updates state objects"""
    if request.content_type != 'application/json':
        return abort(400, "Not a JSON")
    state = storage.get(State, state_id)
    if state:
        if not request.get_json():
            return abort(400, "Not a JSON")
        data = request.get_json()
        ignore_keys = ['id', 'created_at', 'updated_at']
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(state, key, value)
        state.save()
        return jsonify(state.to_dict()), 200
    else:
        return abort(400)
