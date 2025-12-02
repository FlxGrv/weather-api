import yaml
from pathlib import Path
import pandas as pd

#check the configuration file before running this script

#import the configuration file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

def weatherTransfo(df):
    """
    Transforms the data obtained by the getWeatherData function, for better analysis possibilities and readability.
    Specifically tailored for the current load of fetched variables.

    The input is the resulting df of getWeatherData.
    The outputs are:
    - a clean table for plotting
    - a csv version of that table for saving/archiving the timeseries

    """
    #indicate the path where you'd like to save your csv file
    csv_path = Path(config["paths"]["data_csv"])

    #rename columns for readability (personal choices)
    df.rename(columns = {"time":"date","temperature_2m_min": "t_min","temperature_2m_mean":"t_avg","temperature_2m_max":"t_max",
                           "precipitation_sum": "prec_total","snowfall_sum": "snow","daylight_duration":"day_time"
                           ,"sunshine_duration":"sun_time"}, inplace=True)

    #format date column
    df["date"] = pd.to_datetime(df["date"])

    #format sunrise and sunset columns
    df[["sunrise", "sunset"]] = df[["sunrise", "sunset"]].apply(pd.to_datetime)
    #translate sunrise and sunset time in hours to turn them numeric
    df["sunrise"] = df["sunrise"].dt.hour + df["sunrise"].dt.minute /60 + df["sunrise"].dt.second /3600
    df["sunset"]  = df["sunset"].dt.hour + df["sunset"].dt.minute /60 + df["sunset"].dt.second /3600
    #format day_time and sun_time in hours
    df["day_time"] = df["day_time"]/3600
    df["sun_time"] = df["sun_time"]/3600

    #format numeric columns to 2 decimals
    df = df.round(2)

    #MEAN OF LAST WEEK
    #set limits of time interval
    #here we basically set the value to our forecast value. In the current code, forecast = 0
    #so the uper limit is the last day of past_days, yesterday.
    uperLimit = pd.Timestamp(df["date"].max())
    #transform with pd.Timestamp to regularize the comparison later on when printing to csv 
    #not 100% sure why, but it works

    #select appropriated data
    #we set the interval of days we want to calculate the mean for.
    #how it is set, is that it is going to select all days before the uper limit, defined by past_days and forecast
    day_interval = config["API"]["forecast"]+config["API"]["past_days"]-1
    first_day = uperLimit - pd.Timedelta(days=day_interval)
    df_7 = df[(df["date"] >= first_day) & (df["date"] < uperLimit)].copy()
    #copy to avoid the warning

    #calculate means
    df_7_means = df_7.groupby("location").mean().round(2)
    #round again because of memory shenanigans

    #format for readability
    #get sunrise, sunset, daylight and suntime in readable format (for info, not for plotting)
    df_7_means["sunrise_str"] = pd.to_datetime(df_7_means["sunrise"], unit="h").dt.strftime("%H:%M")
    df_7_means["sunset_str"]  = pd.to_datetime(df_7_means["sunset"], unit="h").dt.strftime("%H:%M")
    df_7_means["day_time_str"] = pd.to_datetime(df_7_means["day_time"], unit="h").dt.strftime("%H:%M")
    df_7_means["sun_time_str"]  = pd.to_datetime(df_7_means["sun_time"], unit="h").dt.strftime("%H:%M")

    #add info for identification
    #replace the day for which we calculated the mean of the 7 past days (original is average date)
    df_7_means["date"] = uperLimit
    #add column that indicate it's the mean
    df_7_means["type"] = "7-day-mean"

    #location is index due to groupby, needs to be changed
    df_7_means = df_7_means.reset_index().rename(columns={'index': 'location'})

    #TODAYS VALUES
    today_data = df[df["date"] == uperLimit].copy()
    #creating a copy to avoid warning again

    #format data as above
    today_data["sunrise_str"] = pd.to_datetime(today_data["sunrise"], unit="h").dt.strftime("%H:%M")
    today_data["sunset_str"]  = pd.to_datetime(today_data["sunset"], unit="h").dt.strftime("%H:%M")
    today_data["day_time_str"] = pd.to_datetime(today_data["day_time"], unit="h").dt.strftime("%H:%M")
    today_data["sun_time_str"]  = pd.to_datetime(today_data["sun_time"], unit="h").dt.strftime("%H:%M")

    #add type to indicate it's non-mean data
    today_data["type"] = "Today"

    #TOTAL VALUES GENERATED FOR TODAY
    daily_data = pd.concat([df_7_means,today_data], axis = 0, ignore_index= True)

    #APPEND THE DATA TO THE MAIN CSV IN ORDER TO BUILD HISTORICAL DATA
    #avoid saving 2 times the info for the same day

    if csv_path.exists():
        csv_data = pd.read_csv(csv_path, parse_dates=["date"])

        if uperLimit not in csv_data["date"].values:
            csv_data = pd.concat([csv_data, daily_data], ignore_index= True)
            csv_data.to_csv(csv_path, index=False)

    else:
    #useful for first iteration of the code, when the csv doesn't exist
            csv_data = daily_data
    #make sure updated data always exists as we want to plot it later on
            csv_data.to_csv(csv_path, index=False)
    
    return csv_data