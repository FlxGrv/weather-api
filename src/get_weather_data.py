import yaml
import requests
import pandas as pd

#check the configuration file before running this script

#import the configuration file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

def getWeatherData(config):
    """
    Fetch daily weather data for two given locations using the Open-Meteo API.

    The input is a configuration yaml file (change your selected parameters there!).
    The output is a pandas dataframe that needs some work done on.

    """
    #set coordinates of the 2 places to be compared
    coord1 = (config["Locations"]["coord1"])
    coord2 = (config["Locations"]["coord2"])
    names = (config["Locations"]["name1"],config["Locations"]["name2"])
    #set timezone
    tz = config["Locations"]["timezone"]
    #set variables to be fetched from the API
    var = config["API"]["variables"]
    #set number of days of interest
    forecast = config["API"]["forecast"]
    past = config["API"]["past_days"]

    #prepare the fetch
    #(you can find the parameters in the API documentation: https://open-meteo.com/en/docs) 
    parameters = {
        "latitude": f"{coord1[0]},{coord2[0]}",
        "longitude": f"{coord1[1]},{coord2[1]}",
        "daily": var,
        "forecast_days": forecast,
        "past_days": past,
        "timezone": tz
    }
    url = config["API"]["api_url"]
    
    #the fetch:
    responses = requests.get(url, params=parameters)

    #get the data
    #first as a raw json
    rawData = responses.json()
    #merge the data in a readable dataframe & add location name
    df_final = []
    for place,name in zip(rawData, names):
        df = pd.DataFrame(place["daily"])
        df["location"] = name
        #print(f"test: {df}")

        df_final.append(df)

    df_final = pd.concat(df_final, ignore_index=True)

    return df_final