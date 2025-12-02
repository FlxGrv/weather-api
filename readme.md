# Daily weather timeries builder for 2 defined places

This project contains python code that fetches data from the Open Meteo API for 2 defined locations.
It then transforms the data in order to plot both the daily forecast and the average of the 7 last days for a selected number of indicators.
The outputs are a locally saved csv file and a plot.
The script should be run daily to allow the building of a comparative timeseries.

## Description

In order to practice my python a bit, to learn the useful task of getting data from an API, *and also now* to have a subject to try out git and Github for the first time, I have started this little project.
As I recently moved countries, it is a fun way to keep in touch with the city I previously lived in, in my home country, and see how it compares with the city I moved to.

It gets daily data from the Open Meteo API (https://open-meteo.com/) for 2 places (you need to know their geographical coordinates) and stores it in a csv file.
For each selected indicator (list below), and each location, it generates 2 measures per day: yesterday's value and the average value for the 7 previous days. These values get saved in a csv file stored locally.
It then plots the values on 4 graphs and allows for a quick comparion between the selected locations.
If ran every day, it will create a timeseries.

Currently selected indicators (you can select others, but it will probably break the code):

- temperature_2m_min
- temperature_2m_mean -
- temperature_2m_max
- precipitation_sum
- snowfall_sum 
- sunrise
- sunset
- daylight_duration
- sunshine_duration

You can find the definitions here: https://open-meteo.com/en/docs#daily_parameter_definition

Locations, choice of dates for interval, weather parameters, some plotting variables can be changed in the configuration file.

Ideas for improvement (not in any order):
- Automatize the daily run of the script (not necessarily relevant here, idk)
- ~~structure the code better, using different functions in different files.~~
- make nicer plots
- add more customable points in the config file

## Getting Started

### Dependencies

You should have python installed on your computer and a working internet connexion.
Check requirements.txt for the list of needed packages.

### Installing

* You can download or clone this project from its GitHub repository.
* If you want to use it as is, check the config file to set the locations you are interested in, and other parameters. Normally, the code can be run as it is. Just don't forget to change the path to location in your machine where you want to save the csv file. However, if you decide to change the fetched parameters from the API, that might cause problems.

### Executing program

Just run weather-main.py.
It will generate (if first time) or update the csv in the location you selected.
A plot should appear to. Up to you to save it if you want.

## Help

It's a small program, it should work fine.

## Authors

Me, FlxGrv on GitHub.

## Version History

* 0.2
    * Introduction of a config file, use of functions in separated scripts, fetching of yesterday's data instead of today's (due to the nature of Open Meteo daily variables being final only at 23h59)
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

NA.

## Acknowledgments

Thanks to lenny-ourke for the helpful comments.