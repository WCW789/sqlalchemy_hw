import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.station, Measurement.prcp).all()

    precipitation = []
    for station, prec in results:
        precipitation_dict = {}
        precipitation_dict["station"] = station
        precipitation_dict["prcp"] = prec
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()
    ld_list = [str(ld) for ld in last_date]
    ld_string = ''.join(ld_list)

    last_date_dt = datetime.strptime(ld_string, "%Y-%m-%d")
    last_date_dt = last_date_dt.date()
    one_year_prior = last_date_dt - dt.timedelta(days=365)

    sel = [Measurement.date, Measurement.tobs]
    measures = session.query(*sel).filter(Measurement.date >= one_year_prior).group_by(
        Measurement.date).order_by(Measurement.date).all()
    temp = list(np.ravel(measures))
    return jsonify(temp)


@app.route("/api/v1.0/<start>")
def metrics(start):

    sel = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]

    results = session.query(*sel).\
        filter(Measurement.date >= start).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    sel = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]

    if end:
        results_overall = session.query(
            *sel).filter(Measurement.date <= end).filter(Measurement.date >= start).all()
        temps_overall = list(np.ravel(results_overall))
        return jsonify(temps_overall)

    if not end:
        results_start = session.query(
            *sel).filter(Measurement.date >= start).all()
        temps_start = list(np.ravel(results_start))

        return jsonify(temps_start)


if __name__ == "__main__":
    app.run(debug=True)
