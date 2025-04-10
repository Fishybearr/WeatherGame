import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

from flask import Flask, render_template, request, make_response

from geopy.geocoders import Nominatim

import sqlite3

import random;


#TODO: Implement session cookies to save a user's progress for the day so they
#can't just refresh the tab and retry

id = 2;


#---TODO---TODO---TODO: Implement blueprints to clean up this file---


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

#TODO: Move this to it's own function
#id =1;
conn = sqlite3.connect('weatherDB.db')
cursor = conn.cursor()
cursor.execute(f"SELECT correctCity FROM seeds where id={id}")
correctCity = cursor.fetchone();
conn.close();

correctCity = str(correctCity).replace("|"," ")

latitude, longitude = get_lat_long(correctCity)




app = Flask(__name__)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

@app.route("/")
def ShowMainPage():
    hasCompleted = request.cookies.get('completed')
    hasCompleted = str(hasCompleted)

    currentID = request.cookies.get('gameId')
    currentID = str(currentID)

    if(hasCompleted.__eq__("true")):
        if currentID.__eq__(str(id)):
            return render_template('alreadyPlayed.html')
        else:
            return render_template('index.html')
        
    else:    
        return render_template('index.html')
#TODO: Need to set some sort of system for the alreadyPlayed page to check if a new game is up

@app.route("/weather", methods=['GET'])
def fetchWeather():
    #Get the value for the selected seed and use as weather source


   

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
	"latitude": latitude,
	"longitude": longitude,
	"current": ["temperature_2m", "precipitation", "weather_code"],
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
    current_weather_code = current.Variables(2).Value()

    print(f"Current time {current.Time()}")
    print(f"Current temperature_2m {current_temperature_2m}")
    print(f"Current precipitation {current_precipitation}")
    print(f"Current weather_code {current_weather_code}")


    weather = "NONE"
    #check weather codes
    if current_weather_code == 1: #clear day
        weather = "clear"
    elif current_weather_code == 101: #clear night
        weather = "clear"
    
    #cloudy
    elif current_weather_code == 2:
        weather = "partCloudy"
    
    elif current_weather_code == 102:
        weather = "partCloudy"

    elif current_weather_code == 3:
        weather = "partCloudy"
    
    elif current_weather_code == 103:
        weather = "partCloudy"
    
    elif current_weather_code == 4:
        weather = "cloudy"
    
    elif current_weather_code == 104:
        weather = "cloudy"

        #rainy



    #round number to 1 decimal place
    current_temperature_2m = round(current_temperature_2m,1)
    returnString = f"{current_temperature_2m} °F\n{weather}"
    #return str(current_temperature_2m)
    return returnString;

    #TODO: Add weather icons and logic for other weather codes on sever-side and client-side


@app.route("/validate", methods = ['POST'])
def validateAnswer():
    #fetch answer from correct seed
    playerChoice = str(request.data)
    playerChoice = playerChoice[2:-1]
    print(playerChoice)
    
    #TODO: Move this ID to global as it is the
    # only identifier for what seed we should be on
    #id = 1;

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
@app.route("/cityNames", methods = ['GET'])
def GetCityNames():
    #id = 1;
    conn = sqlite3.connect('weatherDB.db');
    cursor = conn.cursor();
    cursor.execute(f"SELECT city1, city2, correctCity FROM seeds where id={id}");
    row = cursor.fetchone();
    conn.close();

    rand50 = random.randint(0,1);

    if rand50 == 0:
        c1 = row[0]
        c2 = row[1]
    else:
        c1 = row[1]
        c2 = row[0]

    c3 = row[2]
    
    c1 = str(c1).replace("|"," ")
    c2 = str(c2).replace("|"," ")
    c3 = str(c3).replace("|"," ")


    cities = ["","",""]
    
    rand = random.randint(0,2)
    cities[rand] = c3;

    if rand == 2: #rand last
        cities[0] = c1
        cities[1] = c2
    elif rand == 1: #rand second
        cities[0] = c1;
        cities[2] = c2;
    else: #rand first
        cities[1] = c1;
        cities[2] = c2;
  

    #add names in a random order
    # TODO fetch names from the db and put them in a random order
    return f"{cities[0]}\n{cities[1]}\n{cities[2]}"

@app.route("/validate", methods = ['GET'])
def SetCookies():
    resp = make_response()
    resp.set_cookie('completed','true')
    resp.set_cookie('gameId',str(id))
    return resp


app.run(debug=True)