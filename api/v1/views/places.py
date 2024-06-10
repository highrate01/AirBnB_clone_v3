#!/usr/bin/python3
"""Create a new view for Place objects that
handles all default RESTFul API actions"""
from models.place import Place
from models.city import City
from models.user import User
from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_city(city_id):
    """Retrieve all Place objects of a City"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    """Retrieve a Place object"""
    place = storage.get(Place, place_id)
    if place:
        return jsonify(place.to_dict())
    else:
        abort(404)


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Delete a Place object"""
    place = storage.get(Place, place_id)
    if place:
        storage.delete(place)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Create a Place object"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not request.get_json():
        abort(400, "Not a JSON")
    data = request.get_json()
    if 'user_id' not in data:
        abort(400, "Missing user_id")
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)
    if 'name' not in data:
        abort(400, "Missing name")
    data['city_id'] = city_id
    place = Place(**data)
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """Update a Place object"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.get_json():
        abort(400, "Not a JSON")
    data = request.get_json()
    ignore_keys = ['id', 'user_id', 'city_id', 'created_at',
                   'updated_at']
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
def places_search():
    """Retrieves all Place objects based on the JSON
    data in the request body"""
    data = request.get_json(silent=True)
    if not data:
        places = [place.to_dict() for place in storage.all(Place).values()]
        return jsonify(places)

    if not isinstance(data, dict):
        abort(400, "Not a JSON")

    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])

    if not states and not cities and not amenities:
        places = [place.to_dict() for place in storage.all(Place).values()]
        return jsonify(places)

    places_list = []

    if states:
        state_objs = [storage.get(State, state_id) for state_id in states]
        for state in state_objs:
            if state:
                for city in state.cities:
                    places_list.extend(city.places)

    if cities:
        city_objs = [storage.get(City, city_id) for city_id in cities]
        for city in city_objs:
            if city:
                places_list.extend(city.places)

    if amenities:
        amenity_objs = [
                storage.get(Amenity, amenity_id) for amenity_id in amenities]
        places_list = [
                place for place in places_list
                if all(amenity in place.amenities for amenity in amenity_objs)]

    places_list = [place.to_dict() for place in set(places_list)]
    return jsonify(places_list)
