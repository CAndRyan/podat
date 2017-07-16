"""run.py - Start the web app, using Flask - http://flask.pocoo.org/"""

# pylint: disable=C0301
# pylint: disable=W0703

# Import flask and the necessary components
import os
from flask import Flask, request, render_template, jsonify, send_from_directory  #redirect, url_for
import requests     # pip install requests

# Import the Psycopg2 and db helper modules
#add symlink to the scripts 'module': sudo ln -s /<initialDirectory>/scripts/ /usr/local/lib/python2.7/dist-packages/pg_prov
#on Windows -> mklink /D C:\Python27\Lib\site-packages\pg_prov "<initialDirectory>\scripts"
from pg_prov import pg_connect as pgc
#import prov_classes as prov
from pg_prov import prov_db as pdb

# Establish the Flask app with config
APP = Flask(__name__)
APP.config.from_object("config")

# Establish a database connection
DB = pgc.PgConnect.with_user("candryan")
MAPBOX_KEY = pdb.ProvDB.get_api_key(DB, "mapbox")

# Define favicon.ico view
@APP.route('/favicon.ico')
def favicon():
    """Define favicon.ico view"""
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Define app routing
@APP.route('/')
def index():
    """Define app routing"""
    return render_template("index.html")

# Define the API request
@APP.route('/api', methods=["GET"])
def api():
    """Define the API request"""
    #obj = request.get_json(force=True)
    limit = 10
    try:
        limit = int(request.args.get("limit"))
    except Exception as ex:
        return (str(ex), 400)

    rows = pdb.ProvDB.get_crimes(DB, limit)
    return jsonify(rows)     #**rows if using map instead of list

# Define proxy endpoint for retrieving the map tileset for Leaflet (using MapBox)
@APP.route('/get-tiles-proxy', methods=["GET"])
def get_tiles():
    """Define proxy endpoint for retrieving the map tileset for Leaflet (using MapBox)"""
    zxy = [0]*3
    url = "https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{0}/{1}/{2}?access_token={3}"

    try:
        zxy[0] = request.args.get("z")
        zxy[1] = request.args.get("x")
        zxy[2] = request.args.get("y")
    except Exception as ex:
        return (str(ex), 400)

    if MAPBOX_KEY is not None:
        try:
            m_url = url.format(zxy[0], zxy[1], zxy[2], MAPBOX_KEY)
        except Exception as ex:
            return (str(ex), 500)

        return requests.get(m_url).content
    else:
        return ('', 204)
