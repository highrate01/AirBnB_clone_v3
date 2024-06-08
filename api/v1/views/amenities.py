#!/usr/bin/python3
"""Create a new view for Amenity objects
that handles all default RESTFul API actions"""
from models.amenity import Amenity
from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage


@app_views.route('/amenities', methods=['GET'], strict_slashes=False)
def get_amenities():
    """retrieve all amenity objects"""
    amenities = storage.all(Amenity).values()  # Corrected to use values()
    list_amenity = [amenity.to_dict() for amenity in amenities]
    return jsonify(list_amenity)


@app_views.route('/amenities/<amenity_id>', methods=['GET'],
                 strict_slashes=False)
def get_amenity_obj(amenity_id):
    """retrieve each amenity object"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        return jsonify(amenity.to_dict())
    else:
        return abort(404)


@app_views.route('/amenities/<amenity_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_amenity(amenity_id):
    """delete each amenity object"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        storage.delete(amenity)
        storage.save()
        return jsonify({}), 200
    else:
        return abort(404)


@app_views.route('/amenities', methods=['POST'], strict_slashes=False)
def create_amenity():
    """creates amenity objects"""
    if request.content_type != 'application/json':
        return abort(400, "Not a JSON")
    data = request.get_json()
    if not data:
        return abort(400, "Not a JSON")
    if "name" not in data:
        return abort(400, "Missing name")
    amenity = Amenity(**data)
    amenity.save()
    return jsonify(amenity.to_dict()), 201


@app_views.route('/amenities/<amenity_id>', methods=['PUT'],
                 strict_slashes=False)
def updates_amenity(amenity_id):
    """updates amenity object"""
    if request.content_type != 'application/json':
        return abort(400, "Not a JSON")
    data = request.get_json()
    if not data:
        return abort(400, "Not a JSON")
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        ignore_keys = ['id', 'created_at', 'updated_at']
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(amenity, key, value)
        amenity.save()
        return jsonify(amenity.to_dict()), 200
    else:
        return abort(404)
