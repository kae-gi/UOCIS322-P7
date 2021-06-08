from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson import json_util
import json,os


app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetsdb

def pullAll(limit=0):
    """pulls all open and close times from the database"""
    all_times = dict()
    if limit > 0:
        all_list = list(db.timestable.find().limit(limit))
    else:
        all_list = list(db.timestable.find())
    all_list_loaded = json.loads(json_util.dumps(all_list))
    for i in range(len(all_list_loaded)):
        open_time = all_list_loaded[i]["open"]
        close_time = all_list_loaded[i]["close"]
        all_times[i] = {"open_time":open_time, "close_time":close_time}
    return all_times

def formCSV(data):
    """converts data to csv format"""
    rows = ""
    headers = list(data[0].keys())
    rows = ",".join(headers) + "\n"
    for key in data:
        if "open_time" in headers and "close_time" in headers:
            row = [data[key]["open_time"], data[key]["close_time"]]
        elif "open_time" in headers:
            row = [data[key]["open_time"]]
        else:
            row = [data[key]["close_time"]]
        rows +=  ",".join(row) + "\n"
    return rows

class listAll(Resource):
    def get(self, dtype=""):
        top = int(request.args.get('top',default=-1)) # default is show all
        if isinstance(top,int): # top k many to pull
            data = pullAll(top)
        else: # if not specified, pull all
            data = pullAll()
        # choose data type to return
        if dtype == "csv":
            return formCSV(data)
        else:
            return data

class listOpenOnly(Resource):
    def get(self, dtype=""):
        times = dict()
        top = int(request.args.get('top',default=-1)) # default is show all
        if isinstance(top,int):
            data = pullAll(top)
        else:
            data = pullAll()
        for key in data:
            row = {"open_time":data[key]["open_time"]}
            times[key] = row
        if dtype == "csv":
            return formCSV(times)
        else:
            return times

class listCloseOnly(Resource):
    def get(self, dtype=""):
        times = dict()
        top = int(request.args.get('top',default=-1)) # default is show all
        if isinstance(top,int):
            data = pullAll(top)
        else:
            data = pullAll()
        for key in data:
            row = {"close_time":data[key]["close_time"]}
            times[key] = row
        if dtype == "csv":
            return formCSV(times)
        else:
            return times

# Create routes
# Another way, without decorators
api.add_resource(listAll, '/listAll/', '/listAll/<string:dtype>')
api.add_resource(listOpenOnly, '/listOpenOnly/', '/listOpenOnly/<string:dtype>')
api.add_resource(listCloseOnly, '/listCloseOnly/', '/listCloseOnly/<string:dtype>')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
