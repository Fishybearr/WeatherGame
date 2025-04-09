import sqlite3
from geopy.geocoders import Nominatim
#connect to DB
# INSERT into seeds VALUES(id,'name1','name2','correctName')

def get_lat_long(city_name):
    geolocator = Nominatim(user_agent="geocoding_app")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return 0, 0 #default vals for when city cannot be found


city1 = "Kyoto, Japan";
city2 = "Prague, Czech Republic";
city3 = "Buenos Aires, Argentina";

latitude, longitude = get_lat_long(city1)
print (f"{latitude},{longitude}")

latitude, longitude = get_lat_long(city2)
print (f"{latitude},{longitude}")

latitude, longitude = get_lat_long(city3)
print (f"{latitude},{longitude}")