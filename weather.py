import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

from flask import Flask

from geopy.geocoders import Nominatim


def get_lat_long(city_name):
    geolocator = Nominatim(user_agent="geocoding_app")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None



#Ideally this will not be run in the server script
#These should be generated seperately and put into
#the database as seeds
#Then the server can pull the coords and city names
#from the DB and send them to the client
city = "Queensbury, New York"
latitude, longitude = get_lat_long(city)




app = Flask(__name__)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

@app.route("/")
def ShowMainPage():
    return "<p>Hello World!</p>"


@app.route("/weather", methods=['GET'])
def fetchWeather():
    #can set a random lat and long here
    #then get the name of the city

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
    t = f"<p>Current Temp {current_temperature_2m}</p>"
    return t

app.run(debug=True)