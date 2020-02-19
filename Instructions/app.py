
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite", echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurements
Station = Base.classes.stations

session = Session(engine)

app = Flask(__name__)



@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Avalable Routes:<br/><br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- precipitation by dates from prior year<br/>"
        f"<br/>"

        f"/api/v1.0/stations<br/>"
        f"- Return a json list of stations from the dataset.<br/>"
        f"<br/>"
        
        f"/api/v1.0/tobs<br/>"
        f"- Invoice Total for a given country (defaults to 'USA')<br/>"
        f"<br/>"
        
        f"/api/v1.0/startdate/enddate<br/>"
        f"- the minimum average, and the max temperature for a given start or start-end range.<br/>"
        f"- examples of giving start date: /api/v1.0/2017-01-01<br/>"
        f"- examples of giving start-end date: /api/v1.0/2017-01-01/2017-01-15<br/>"
    )



YearBeg = dt.datetime(2016,5,20) #set one less date before the year beg date 
YearEnd = dt.datetime(2017,8,23) #set one more date after the year end date 


@app.route("/api/v1.0/precipitation")
def Precipitation():
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > YearBeg).filter(Measurement.date < YearEnd).all()
    OneYearDates = [r[0] for r in results]
    OneYearPrcp = [r[1] for r in results]

    PrcpbyD = pd.DataFrame({'date':OneYearDates,'precipitation':OneYearPrcp})
    PrcpbyD.set_index('date',inplace=True)
    

    df_as_json = PrcpbyD.to_dict(orient='split')
    
    
    return jsonify({'status': 'ok', 'json_data': df_as_json})


@app.route("/api/v1.0/stations")
def Stations():
    result2 = session.query(Station.station, Station.name, Station.latitude,Station.longitude,Station.elevation).statement
    Sls = pd.read_sql_query(result2, session.bind)
    Sls.set_index('station',inplace=True)
    df2_as_json = Sls.to_dict(orient='split')
    return jsonify({'status': 'ok', 'json_data': df2_as_json})


@app.route("/api/v1.0/tobs")
def Tobs():
    result3 = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > YearBeg).filter(Measurement.date < YearEnd).statement
    Templs = pd.read_sql_query(result3, session.bind)
    df3_as_json = Templs.to_dict(orient='split')
    return jsonify({'status': 'ok', 'json_data': df3_as_json})

@app.route("/api/v1.0/<start>")
def Vacation(start):
    VacaBeg = start 
    calc_temp = session.query(func.avg(Measurement.tobs),func.max(Measurement.tobs),func.min(Measurement.tobs)).\
        filter(Measurement.date > VacaBeg).statement
    TempStat = pd.read_sql_query(calc_temp, session.bind)
    TAve = int(TempStat['avg_1'])
    TMax = int(TempStat['max_1'])
    TMin = int(TempStat['min_1'])
    Templist = pd.DataFrame({'Stats': ["Ave_Temp","Max_Temp","Min_Temp"], 'value': [TAve, TMax, TMin]})
    df4_as_json = Templist.to_dict(orient='split')
    return jsonify({'status': 'ok', 'json_data': df4_as_json})


@app.route("/api/v1.0/<start>/<end>")
def Vacation1(start,end):
    VacaBeg1 = start 
    VacaEnd1 = end

    calc_temp1 = session.query(func.avg(Measurement.tobs),func.max(Measurement.tobs),func.min(Measurement.tobs)).\
        filter(Measurement.date > VacaBeg1).filter(Measurement.date < VacaEnd1).statement
    TempStat1 = pd.read_sql_query(calc_temp1, session.bind)
    TAve1 = int(TempStat1['avg_1'])
    TMax1 = int(TempStat1['max_1'])
    TMin1 = int(TempStat1['min_1'])
    
    Templist1 = pd.DataFrame({'Stats': ["Ave_Temp","Max_Temp","Min_Temp"], 'value': [TAve1, TMax1, TMin1]})
    df5_as_json = Templist1.to_dict(orient='split')
    return jsonify({'status': 'ok', 'json_data': df5_as_json})









################################################################

if __name__ == "__main__":
    app.run(debug=True)