# run.py
#
# Start the web app, using Flask - http://flask.pocoo.org/
#

# Import flask and the necessary components
from flask import Flask, request, redirect, url_for, render_template, jsonify, send_from_directory
import os
import requests     # pip install requests

# Import the Psycopg2 and db helper modules
#add symlink to the scripts 'module': sudo ln -s /<initialDirectory>/scripts/ /usr/local/lib/python2.7/dist-packages/pg_prov
from pg_prov import pg_connect as pgc
#import prov_classes as prov
from pg_prov import prov_db as pdb

# Establish the Flask app with config
app = Flask(__name__)
app.config.from_object("config")

# Establish a database connection
db = pgc.PgConnect.with_user("candryan")
mapboxKey = pdb.ProvDB.get_api_key(db, "mapbox")

# Define favicon.ico view
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Define app routing
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api', methods=["POST"])
def api():
    #rows = db.select("prov_statute", ["*"], """id > 0 LIMIT 5""")
    #return "\n".join(db.stringify_rows(rows))
    #return jsonify(request.get_json(force=True))
    #obj = request.get_json(force=True)
    #rows = db.select(obj["table"], ["*"], """id > {0} LIMIT {1}""".format(obj["idCondition"], obj["limit"]))
    #return "\n".join(db.stringify_rows(rows))
    obj = request.get_json(force=True)
    rows = pdb.ProvDB.get_crimes(db)
    return jsonify(rows)     #**rows if using map instead of list

# Define proxy endpoint for retrieving the map tileset for Leaflet (using MapBox)
@app.route('/get-tiles-proxy', methods=["GET"])
def get_tiles():
    zxy = [0]*3
    url = "https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{0}/{1}/{2}?access_token={3}"

    try:
        zxy[0] = request.args.get("z")
        zxy[1] = request.args.get("x")
        zxy[2] = request.args.get("y")
    except Exception as ex:
        return (str(ex), 400)

    if not mapboxKey == None:
        try:
            mUrl = url.format(zxy[0], zxy[1], zxy[2], mapboxKey)
        except Exception as ex:
            return (str(ex), 500)

        return requests.get(mUrl).content
    else:
        return ('', 204)
