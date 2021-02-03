import requests
import pymongo
from pprint import pprint
import logging

import pandas as pd
import requests
import json


source_url = 'https://raw.githubusercontent.com/ctiml/convenience-store-data/master/7-11/台北市.json'
PASSWORD = '1234'
DBNAME = 'taipei_seven'
mongo_server_url = "mongodb+srv://Admin:"+PASSWORD+"@cluster0.owy49.mongodb.net/"+DBNAME+"?retryWrites=true&w=majority"

# logging configuration
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def data_fetch(self, source_url):
    try:
        r= requests.get(source_url)
        if r.status_code == 200:
            logger.info("Successful fetch data from source.")
            return r.json()
        else: 
            logger.error("Endpoint returned failed status.\n")
            logger.info("Status for fetching source data: {}".format(r.text))

def data_screen(self, data):
    IDs =[]
    for item in data:
        IDs+=[item['POIID']]
    
    logger.info("total IDs:", len(data), "unique IDs:", len(set(IDs)))

def parse_source_json(self, data):

    """ This function parses the JSON content and leave only the features needed,
        Set the location coordinates right for mongo ingestion.
    """
    data_dict=[]
    for item in data:
        tmp_dict ={}
        tmp_dict["_id"]=item["POIID"]
        tmp_dict["POIName"]=item["POIName"]
        tmp_dict["Address"]=item["Address"]
        try:
            if item["isDining"]=='Y':
                tmp_dict["isDining"] = True
            else:
                tmp_dict["isDining"] = False
        except:
            tmp_dict["isDining"] = None
        tmp_dict["location"] = {"type": "Point", "coordinates": [item["X"],item["Y"]]}
        
        data_dict.append(tmp_dict)
    return data_dict

def mongo_connect(self,mongo_server_url, DBNAME, COLLECTION_NAME):
    try:
        cluster = pymongo.MongoClient(client_url)
        cluster.server_info()
        db=cluster[DBNAME]
        collection = db[COLLECTION_NAME]
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logger.error(err)
        except pymongo.errors.ConnectionFailure as err:
            logger.error(err)
        except pymongo.errors.InvalidURI as err:
            logger.error(err)
        except pymongo.errors.OperationFailure as err:
            logger.error(err)
    except:
        logger.error("connection error. Unknown issue.")

    return collection

if __name__ == "__main__":
    # based on the data structure, only need to parse the Taipei city sevens' locations
    data=data_fetch(source_url)['stores']
    data_screen(data)

    # parse data
    data = parse_source_json(data)

    # initiate connection to mongo
    collection = mongo_connect(mongo_server_url, DBNAME, DBNAME)

    # ingest data
    for doc in data:
        try:
            result = collection.insert_one(doc)
            if result.inserted_id:
                logger.info("successful insert, document: {}".format(result.inserted_id))
        except Excpetion as err:
            logger.error("An exception occurred: {}".format(err))
            
    logger.info("Finished. Check database creation at Mongo Atlas.")

