# Import the dependencies.
import datetime as dt
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
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation measurementsf for hte last 12 months: /api/v1.0/precipitation<br/>"
        f"A list of stations from the database: /api/v1.0/stations<br/>"
        f"A list of dates and temperature observations for the previous year: /api/v1.0/tobs<br/>"
        f"Enter a Start date to view the min, max and average temperatures: api/v1.0/<start><br/>"
        f"Enter a start and end date to view the min, max and average temperatures: /api/v1.0/<start><end><br/>"
    )
