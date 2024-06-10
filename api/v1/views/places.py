#!/usr/bin/python3
"""Create a new view for Place objects that
handles all default RESTFul API actions"""
from models.place import Place
from models.city import City
from models.state import State
from models.amenity import Amenity
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
    if request.content_type != 'application/json':
        abort(400, "Not a JSON")
    if not request.get_json():
        abort(400, "Not a JSON")
    data = request.get_json()
    if data:
        states = data.get('states')
        cities = data.get('cities')
        amenities = data.get('amenities')

    if not states and not cities and not amenities:
        places = storage.all(Place).values()
        places_list = [place.to_dict() for place in places]
        return jsonify(place_list)
    places_list = []

    if states:
        state_objs = [storage.get(State, state_id) for state_id in states]
        for state in state_objs:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            places_list.append(place)

    if cities:
        city_objs = [storage.get(City, city_id) for city_id in cities]
        for city in city_objs:
            if city:
                for place in city.places:
                    if place not in places_list:
                        places_list.append(place)

    if amenities:
        if not places_list:
            all_places = storage.all(Place).values()
            amen_objs = [storage.get(Amenity, amen_id) for amen_id in amenities]
            for place in all_places:
                if all(amen in place.amenities for amen in amen_objs)]:
                    places_list.append(place)
    places = []
    for plc_obj in places_list:
        plc_dict = plc_obj.to_dict()
        plc_dict.pop('amenities', None)
        places.append(plc_dict)
    return jsonify(places)
