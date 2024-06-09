#!/usr/bin/python3
"""Create a new view for User object that
handles all default RESTFul API actions"""
from models.user import User
from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage


@app_views.route('/users', methods=['GET'], strict_slashes=False)
def get_users():
    """Retrieve all users"""
    users = [user.to_dict() for user in storage.all(User).values()]
    return jsonify(users)


@app_views.route('/users/<user_id>', methods=['GET'],
                 strict_slashes=False)
def get_user_object(user_id):
    """Retrieve a user object"""
    user = storage.get(User, user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        abort(404)


@app_views.route('/users/<user_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_user(user_id):
    """Delete a user object"""
    user = storage.get(User, user_id)
    if user:
        storage.delete(user)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


@app_views.route('/users', methods=['POST'],
                 strict_slashes=False)
def create_user():
    """Create a user object"""
    if not request.get_json():
        abort(400, "Not a JSON")
    data = request.get_json()
    if 'email' not in data:
        abort(400, "Missing email")
    if 'password' not in data:
        abort(400, "Missing password")
    user = User(**data)
    user.save()
    return jsonify(user.to_dict()), 201


@app_views.route('/users/<user_id>', methods=['PUT'],
                 strict_slashes=False)
def update_user(user_id):
    """Update a user object"""
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    if not request.get_json():
        abort(400, "Not a JSON")
    data = request.get_json()
    ignore_keys = ['id', 'email', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(user, key, value)
    user.save()
    return jsonify(user.to_dict()), 200
