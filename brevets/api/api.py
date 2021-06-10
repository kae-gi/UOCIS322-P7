from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from pymongo import MongoClient
from bson import json_util
import json,os
import logging
#import config

from passlib.hash import sha256_crypt as pwd_context
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                          as Serializer, BadSignature, \
                          SignatureExpired)

app = Flask(__name__)
app.secret_key = 'testing1234@#$'

api = Api(app)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db_b = client.brevetsdb
db_u = client.usersdb
usertable = client.usersdb.usertable

#===============================================================================
# From DockerLogin
SECRET_KEY = 'testing1234@#$'

def hash_password(password):
    #return pwd_context.using(salt="somestring").encrypt(password)
    return pwd_context.encrypt(password)

def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

def generate_auth_token(id, expiration=600):
   s = Serializer(SECRET_KEY, expires_in=expiration)
   return s.dumps({'id': id})

def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return "Success"
#===============================================================================
def pullAll(limit=0):
    """pulls all open and close times from the database"""
    all_times = dict()
    if limit > 0:
        all_list = list(db_b.timestable.find().limit(limit))
    else:
        all_list = list(db_b.timestable.find())
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
        token = request.args.get('token', type=str)
        if not verify_auth_token():
            return abort(401, description="Could not authorize.")
        else:
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
        token = request.args.get('token', type=str)
        if not verify_auth_token():
            return abort(401, description="Could not authorize.")
        else:
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
        token = request.args.get('token', type=str)
        if not verify_auth_token():
            return abort(401, description="Could not authorize.")
        else:
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
#===============================================================================
class Register(Resource):
    def post(self):
        username = request.form.get('username', type=str)
        password = request.form.get('password', type=str)

        # if user does not exist already
        user = db_u.usertable.find_one({'username':username})
        if user == None:
            db_u.usertable.insert({'id':db_u.usertable.find().count()+1, 'username':username, 'password':password})
            return password, 201
        else:
            return abort(400, description="User exists already")

class Token(Resource):
    def get(self):
        username = request.form.get('username', type=str)
        password = request.form.get('password', type=str)

        hash_p = hash_password(password)
        user = db_u.usertable.find_one({'username':username})
        # user does not exist
        if user == None:
            return abort(401, "Unauthorized: user does not exist")
        # password & hash do not match
        #if not verify_password(user['password'], hash_p):
        if not verify_password(password, user['password']):
            return abort(401, "Unauthorized: Password is incorrect")

        id = int(user['id'])
        expiration = 600
        auth_token = generate_auth_token(id, expiration)
        user_token = {'id': user['id'], 'token':str(auth_token)[2:-1], 'duration': expiration}
        return jsonify(user_token)



# Create routes
# Another way, without decorators
api.add_resource(listAll, '/listAll/', '/listAll/<string:dtype>')
api.add_resource(listOpenOnly, '/listOpenOnly/', '/listOpenOnly/<string:dtype>')
api.add_resource(listCloseOnly, '/listCloseOnly/', '/listCloseOnly/<string:dtype>')
api.add_resource(Register, '/register')
api.add_resource(Token, '/token')


# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
