osmPath = "map.osm"
dbPath = "map.db"

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from routing.route import searchRoute
from sql.handle_sql import SqlHandler
from utils.search import search



app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type: application/json'

# First init of database
sql = SqlHandler(dbPath, osmPath)
del sql

# http://127.0.0.1:5555/getRoute/36891304/17021250/
@app.route("/getRoute/<fromWay>/<toWay>/")
@cross_origin()
def getRouteReq(fromWay, toWay):
    return jsonify(nodes=searchRoute(fromWay, toWay))

@app.route("/search/<wayName>/<limit>")
def searchReq(wayName, limit):
    return jsonify(ways=search(wayName, limit))