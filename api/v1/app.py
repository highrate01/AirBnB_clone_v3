#!/usr/bin/python3
"""
create a api
"""
from models import storage
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/api/v1/*": {"origins": "0.0.0.0"}})


@app.teardown_appcontext
def teardown(exception):
    """close engine"""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """customized error handler"""
    response = {"error": "Not found"}
    return jsonify(response), 404


if __name__ == "__main__":
    HOST = getenv("HBNB_API_HOST", '0.0.0.0')
    PORT = int(getenv("HBNB_API_PORT", 5000))
    app.run(debug=True, host=HOST, port=PORT, threaded=True)
