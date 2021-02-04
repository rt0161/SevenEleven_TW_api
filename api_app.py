from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json
from bson.json_util import dumps

import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# ensure non-ascii char representation
app.config['JSON_AS_ASCII'] = False


PASSWORD = '1234'
DBNAME = 'taipei_seven'
app.config['DBNAME'] = DBNAME
MONGO_URI = "mongodb+srv://Admin:"+PASSWORD+"@cluster0.owy49.mongodb.net/"+DBNAME+"?retryWrites=true&w=majority"
app.config['MONGO_URI'] = MONGO_URI

mongo = PyMongo(app, MONGO_URI)

def convert_2radian(n):
    """Converts distance in km to radian"""
    EARTH_RADIUS = 6378.1
    return n/EARTH_RADIUS

def within_dist_query(long, lat, dist, isDining= None):
    if isDining==None:
        query = {'location.coordinates': 
                    {'$nearSphere':[long, lat],
                    '$maxDistance':convert_2radian(dist)}}
    else:
        query = {'location.coordinates': 
                    {'$nearSphere':[long, lat],
                    '$maxDistance':convert_2radian(dist)},
                   'isDining': isDining}
       
    return query


@app.route('/search_within/', methods=['POST'])
def search_within():
    if request.json:
        # validate post content
        query_content_check =list(request.json.keys())
        if len(query_content_check) < 3: 
            return jsonify(status="failure", desc="Missing post content.")
        for key in query_content_check:
            if key not in ['longitude','latitude','dist']:
                return jsonify(status="failure", desc="Ill post content.")

        lon = request.json['longitude']
        lat = request.json['latitude']
        dist = request.json['dist']
        if 'isDining' in query_content_check:
            payload = within_dist_query(lon, lat, dist, request.json['isDining'])
        else:    
            payload = within_dist_query(lon, lat, dist)
    else: return jsonify(status="failure", desc="No valid post content.")
    app.logger.info(payload)
        
    seven = mongo.db.taipei_seven
    # query from mongo
    try:
        result = seven.find(payload)
        response = json.loads(dumps(result,ensure_ascii=False))

    except Exception as err:
        app.logger.info(err)
        return jsonify(status="failure", desc="query database not sucess.")
    return jsonify({'result' : response})

if __name__ == '__main__':
    app.run(debug=True)