import requests
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#SET VARIABLES

#set path to csv where data will be stored
csv_path = Path(r"C:\Users\felix\Documents\Python Projects\Weather API\LJ-LAU_weather_comparison_2.csv")
#not used for now

#set coordinates of the 2 places to be compared
#coord 1 is Ljubljana, coord 2 is Lausanne
coord1 = (46.05, 14.51)
coord2 = (46.51, 6.63)
names = ("Ljubljana", "Lausanne")

#set timezone (as found here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
tz = "Europe/Berlin"

#set weather variables you are interested in (as found here: https://open-meteo.com/en/docs#daily_parameter_definition)
#for now: daily variables
var = ["temperature_2m_min","temperature_2m_mean","temperature_2m_max","precipitation_sum","snowfall_sum","sunrise","sunset","daylight_duration","sunshine_duration"]

#set number of days of interest
#for now: today and 7 days in the past
forecast = 1
past = 7

#PREPARE FETCH

parameters = {
    "latitude": f"{coord1[0]},{coord2[0]}",
    "longitude": f"{coord1[1]},{coord2[1]}",
    "daily": var,
    "forecast_days": forecast,
    "past_days": past,
    "timezone": tz
}

url = "https://api.open-meteo.com/v1/forecast"

responses = requests.get(url, params=parameters)

#GET DATA

#get the raw Json
rawData = responses.json()

#merge the data in a readable table
#add location name
df_final = []

for place,name in zip(rawData, names):
    df = pd.DataFrame(place["daily"])
    df["location"] = name
    #print(df)

    df_final.append(df)

df_final = pd.concat(df_final, ignore_index=True)

#FORMAT DATA

#print(df_final.dtypes)

#rename columns that need it (sunset and sunrise stay the same)
df_final.rename(columns = {"time":"date","temperature_2m_min": "t_min","temperature_2m_mean":"t_avg","temperature_2m_max":"t_max",
                           "precipitation_sum": "prec_total","snowfall_sum": "snow","daylight_duration":"day_time"
                           ,"sunshine_duration":"sun_time"}, inplace=True)

#format "time" column
df_final["date"] = pd.to_datetime(df_final["date"])

#format sunrise and sunset columns
df_final[["sunrise", "sunset"]] = df_final[["sunrise", "sunset"]].apply(pd.to_datetime)
#translate sunrise and sunset time in hours to turn them numeric
df_final["sunrise"] = df_final["sunrise"].dt.hour + df_final["sunrise"].dt.minute /60 + df_final["sunrise"].dt.second /3600
df_final["sunset"]  = df_final["sunset"].dt.hour + df_final["sunset"].dt.minute /60 + df_final["sunset"].dt.second /36000
#format day_time and sun_time in hours
df_final["day_time"] = df_final["day_time"]/3600
df_final["sun_time"] = df_final["sun_time"]/3600

#format numeric columns to 2 decimals
df_final = df_final.round(2)

#MEAN OF LAST WEEK

#set limits of time interval
today = pd.Timestamp(df_final["date"].max())
#transform with pd.Timestamp to regularize the comparison later on when printing to csv 
#not 100% sure why, but it works

first_day = today - pd.Timedelta(days=7)
#select appropriated data
df_7 = df_final[(df_final["date"] >= first_day) & (df_final["date"] < today)].copy()
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
df_7_means["date"] = today
#add column that indicate it's the mean
df_7_means["type"] = "7-day-mean"

#location is index due to groupby, needs to be changed
df_7_means = df_7_means.reset_index().rename(columns={'index': 'location'})

#TODAYS VALUES

today_data = df_final[df_final["date"] == today].copy()
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

    if today not in csv_data["date"].values:
        csv_data = pd.concat([csv_data, daily_data], ignore_index= True)
        csv_data.to_csv(csv_path, index=False)

else:
    #useful for first iteration of the code, when the csv doesn't exist
    csv_data = daily_data
    #make sure updated data always exists as we want to plot it later on
    csv_data.to_csv(csv_path, index=False)

#PLOT THE DATA
#lines for 7-day averages, dots for today's data
#1 plot for min/mean/max temp (2x 3 lines + 2x 3 dots)
#1 plot for precipitation and snow (2x 2 lines + 2x 2 dots) find way to draw nothing if 0 snow
#1 plot for sunrise and sunset 
#1 plot for daytime and suntime

#set variables used in all the subplots

#set colors for the locations
colors = {"Lausanne": "blue", "Ljubljana": "green"}
#set dictionnary that we will then unpack when setting labels for each subplot
x_tick_var = {"axis":"x", "labelrotation":45, "labelsize":7, "pad" : 1}
#set variable to set format of x-labels
myFmt = mdates.DateFormatter("%d %b %y")
#set marker size for all plots
marks = 4

#set number of plots (here 4)
fig, axs = plt.subplots(2, 2, figsize=(10, 8))
fig.subplots_adjust(hspace=0.5)

#get the first subplot (top-left)
#plot is about temperature
ax = axs[0, 0]

for (loc, ty), group in csv_data.groupby(["location","type"]):
    col = colors[loc]

    if ty == "Today":
        # no lines but just markers for today's data
        ax.plot(group["date"], group["t_avg"],marker= "o", markersize = marks, linestyle= "none", color = col) #, label=f'{loc} - {ty}')
        ax.plot(group["date"], group["t_max"],marker= "x", markersize = marks, linestyle= "none", color = col)
        ax.plot(group["date"], group["t_min"],marker= "d", markersize = marks, linestyle= "none", color = col)
    else:
        #lines for the 7-day mean
        ax.plot(group["date"], group["t_avg"], color = col)
        ax.plot(group["date"], group["t_max"], color = col, linestyle= "--")
        ax.plot(group["date"], group["t_min"], color = col, linestyle= ":")

ax.set_xlabel("Date")
ax.set_ylabel("temp")
ax.set_title("Temp evolution over days (Min, Avg, Max) [°C]")
ax.tick_params(**x_tick_var)
ax.xaxis.set_major_formatter(myFmt)
#ax.legend(title="Location")

#get second plot (top-right)
#plot is about total precipitation and snow
ax = axs[0, 1]

#replace 0 by nan so it doesn't get plotted
for (loc, ty), group in csv_data.replace(0, np.nan).groupby(["location","type"]):
    col = colors[loc]

    if ty == "Today":
        # no lines but just markers for today's data
        ax.plot(group["date"], group["prec_total"],marker= "o", markersize = marks, linestyle= "none", color= col)
        ax.plot(group["date"], group["snow"],marker= "x", markersize = marks, linestyle= "none", color = col)
        
    else:
        #lines for the 7-day mean
        ax.plot(group["date"], group["prec_total"], color = col)
        ax.plot(group["date"], group["snow"], color = col, linestyle= "--")

ax.set_xlabel("Date")
ax.set_ylabel("Precipitaion")
ax.set_title("Precipitation and snow [mm]")
ax.tick_params(**x_tick_var)
ax.xaxis.set_major_formatter(myFmt)

#get third plot (botom-left)
#plot is about sunrise and sunset times (in hours since midnight)
ax = axs[1, 0]

for (loc, ty), group in csv_data.groupby(["location","type"]):
    col = colors[loc]

    if ty == "Today":
        # no lines but just markers for today's data
        ax.plot(group["date"], group["sunrise"],marker= "o", markersize = marks, linestyle= "none", color= col)
        ax.plot(group["date"], group["sunset"],marker= "x", markersize = marks, linestyle= "none", color = col)
        
    else:
        #lines for the 7-day mean
        ax.plot(group["date"], group["sunrise"], color = col)
        ax.plot(group["date"], group["sunset"], color = col, linestyle= "--")

ax.set_xlabel("Date")
ax.set_ylabel("Hours since midnight")
ax.set_title("Sunrise and sunset times [h]")
ax.tick_params(**x_tick_var)
ax.xaxis.set_major_formatter(myFmt)

#get fourth plot (botom-right)
#plot is about daytime and suntime in hours
ax = axs[1, 1]

for (loc, ty), group in csv_data.groupby(["location","type"]):
    col = colors[loc]

    if ty == "Today":
        # no lines but just markers for today's data
        ax.plot(group["date"], group["day_time"],marker= "o", markersize = marks, linestyle= "none", color= col)
        ax.plot(group["date"], group["sun_time"],marker= "x", markersize = marks, linestyle= "none", color = col)
        
    else:
        #lines for the 7-day mean
        ax.plot(group["date"], group["day_time"], color = col)
        ax.plot(group["date"], group["sun_time"], color = col, linestyle= "--")

ax.set_xlabel("Date")
ax.set_ylabel("Hours")
ax.set_title("Day time and sun time [h]")
ax.tick_params(**x_tick_var)
ax.xaxis.set_major_formatter(myFmt)

plt.show()



print(csv_data.replace(0, np.nan))






