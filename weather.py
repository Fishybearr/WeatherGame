import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

from flask import Flask, render_template, request

from geopy.geocoders import Nominatim

import sqlite3

#Fetches data from sqlite
#conn = sqlite3.connect('weatherDB.db')
#cursor = conn.cursor()
#cursor.execute("SELECT city1 FROM seeds WHERE id=1")
#row = cursor.fetchone()
#conn.close()
#print(row)


def get_lat_long(city_name):
    geolocator = Nominatim(user_agent="geocoding_app")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return 0, 0 #default vals for when city cannot be found



#Ideally this will not be run in the server script
#These should be generated seperately and put into
#the database as seeds
#Then the server can pull the coords and city names
#from the DB and send them to the client
city = "Buffalo, New York"
latitude, longitude = get_lat_long(city)




app = Flask(__name__)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

@app.route("/")
def ShowMainPage():
    return render_template('index.html')


@app.route("/weather", methods=['GET'])
def fetchWeather():
    #Get the value for the selected seed and use as weather source


    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
	    "latitude": latitude,
	    "longitude": longitude,
	    "current": ["temperature_2m", "precipitation"],
	    "wind_speed_unit": "mph",
	    "temperature_unit": "fahrenheit",
	    "precipitation_unit": "inch"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_precipitation = current.Variables(1).Value()

    print(f"Current time {current.Time()}")
    print(f"Current temperature_2m {current_temperature_2m}")
    print(f"Current precipitation {current_precipitation}")
    #t = f"<p>Current Temp {current_temperature_2m}</p>"

    #round number to whole
    current_temperature_2m = round(current_temperature_2m,1)
    return str(current_temperature_2m)

@app.route("/validate", methods = ['POST'])
def validateAnswer():
    #fetch answer from correct seed
    playerChoice = str(request.data)
    playerChoice = playerChoice[2:-1]
    print(playerChoice)
    
    #TODO: Move this ID to global as it is the
    # only identifier for what seed we should be on
    id = 1;
    
    #connect to DB and pull the correctAnswer for current seed
    conn = sqlite3.connect('weatherDB.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT correctCity FROM seeds where id={id}")
    correctAnswer = cursor.fetchone();
    conn.close()

    #Force correctAnswer to be a string
    correctAnswer = str(correctAnswer);

    #remove front and end chars from answer
    correctAnswer = correctAnswer[2:-3]

    #replace | with SPACE
    correctAnswer = correctAnswer.replace("|"," ")


    if playerChoice.__eq__(correctAnswer):
        return "yes"
    else:
        return "no"
    

    # TODO: Update this to pull from the database and put the names
    # in a random order before sending the string
    # Returns the names of the cities as a string
    #
@app.route("/cityNames", methods = ['GET'])
def GetCityNames():
    #add names in a random order
    # TODO fetch names from the db and put them in a random order
    return "Queensbury New York\nFort Edward New York\nBuffalo New York"

app.run(debug=True)