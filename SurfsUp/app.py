# Import the dependencies.
import datetime as dt
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station



#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Create first route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation measurementsf for hte last 12 months: /api/v1.0/precipitation<br/>"
        f"A list of stations from the database: /api/v1.0/stations<br/>"
        f"A list of dates and temperature observations for the previous year: /api/v1.0/tobs<br/>"
        f"Enter a Start date to view the min, max and average temperatures(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Enter a start and end date to view the min, max and average temperatures(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# Create second route precipitation data for the last 12 months.
@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate query date
    
    most_recent = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    query_date = datetime.strptime(most_recent,'%Y-%m-%d') - dt.timedelta(days=365)

    #  Query for results using query date
    weather_data = session.query(Measurements.date, Measurements.prcp).\
    filter(Measurements.date >= query_date).order_by(Measurements.date).all()

    # Close out session (link) from Python to the DB
    session.close()

    # Create dictionary for results
    precipitation = []
    for date, prcp in weather_data:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precipitation.append(precip_dict)
    # return jason list of dictionary
    return jsonify(precipitation)

#  Create third route for station data.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #  Query database for the stations
    station_query = session.query(Stations.station, Stations.name, Stations.latitude, Stations.longitude, Stations.elevation).all()

    # Close out session (link) from Python to the DB
    session.close()  

     # Create dictionary for results
    summary= []
    for station,name,latitude,longitude,elevation in station_query:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = latitude
        station_dict['Lon'] = longitude
        station_dict["Elevation"] = elevation
        summary.append(station_dict)
      
    # return jason list of dictionary
    return jsonify(summary)   
    
#  Create forth route for most active station yearly data
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most active station
    active_stations = session.query(Measurements.station, func.count(Measurements.id)).\
    group_by(Measurements.station).\
    order_by(func.count(Measurements.id).desc()).all()

    # Calculate query date
    most_recent = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    query_date = datetime.strptime(most_recent,'%Y-%m-%d') - dt.timedelta(days=365)
   

    #  Query database from the total observations for the last year
    tobs_query = session.query( Measurements.date, Measurements.tobs).\
        filter(Measurements.date >= query_date).filter(Measurements.station == active_stations[0][0]).all()

    # Close out session (link) from Python to the DB
    session.close()

    # Create dictionary for results
    tobs_summary = []
    for date, tobs in tobs_query:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        tobs_summary.append(tobs_dict)

    # return jason list of dictionary
    return jsonify(tobs_summary)

# Crete fifth route to summary measurements active stations based on entered start date
@app.route("/api/v1.0/<start>")
def get_t_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_result = session.query(func.min(Measurements.tobs), func.round(func.avg(Measurements.tobs),2),\
     func.round(func.max(Measurements.tobs),2)).filter(Measurements.date >= start).all()
    
    # Close out session (link) from Python to the DB
    session.close()

# Create dictionary and jsonif

    tobs_sum = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["max"] = max
        tobs_sum.append(tobs_dict)

    return jsonify(tobs_sum)

# Create sixth route for summary data for active stations based on entering a start and end date
@app.route('/api/v1.0/<start>/<end>')
def get_t_start_end(start,end):
   
    # Close out session (link) from Python to the DB
    session = Session(engine)
   
    query_result = session.query(func.min(Measurements.tobs), func.round(func.avg(Measurements.tobs),2), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
   
    # Close out session (link) from Python to the DB
    session.close()
    # Create dictionary and jsonify 
    tobs_sum = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_sum.append(tobs_dict)

    return jsonify(tobs_sum)


if __name__ == "__main__":
    app.run(debug=True)