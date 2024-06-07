#!/usr/bin/python3
"""defines api status"""
from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status')
def api_status():
    """return route"""
    response = {"status": "OK"}
    return jsonify(response)
