"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import os
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
from pymongo import MongoClient
import logging
import json

###
# Globals
###
app = flask.Flask(__name__)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetsdb


###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')

@app.route("/display")
def display():
    km_list=list(db.timestable.find())
    brevet_distance_km=list(db.brevet_distance.find().limit(1))
    # checking: was data entered?
    if (len(km_list) > 0):
        # response: yes, data was entered. display
        return flask.render_template('display.html',
			     km_list=km_list,
                 brevet_distance_km=brevet_distance_km)
    else:
        # response: no, data was ever entered
        return flask.render_template('nope.html')

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))

    # FIXED
    begin_time = request.args.get('begin_time', type=str)
    brevet_dist = request.args.get('brevet_dist', type=float)
    arrow_begin_time = arrow.get(begin_time, "YYYY-MM-DDTHH:mm") # make arrow object

    # changed fixed distance of 200 to brevet distance
    # current time is no longer start time, but the begin_time arrow
    open_time = acp_times.open_time(km, brevet_dist, arrow_begin_time).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet_dist, arrow_begin_time).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/kmsubmit/", methods=["POST"])
def submit():
    # clear out dbs
    db.timestable.drop()
    db.brevet_distance.drop()
    # get km_list for fields
    km_list = request.form.to_dict()
    km_dict = json.loads(km_list['km_list'])
    km_dict_length = len(km_dict)
    # get the brevet distance field
    brevet_distance_km = json.loads(km_list['brevet_distance_km'])
    # checking: is km_dict NOT empty?
    if (km_dict_length > 0):
        # response: not empty, insert into db for brevet_distance and timestable
        brevet_document = {
            'distance': brevet_distance_km
        }
        db.brevet_distance.insert_one(brevet_document)
        for row in km_dict:
            km_document = {
                'miles': row['miles'],
                'km': row['km'],
                'location': row['location'],
                'open': row['open'],
                'close': row['close']
            }
            db.timestable.insert_one(km_document)
    return flask.jsonify(output=str(request.form))

#############

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
