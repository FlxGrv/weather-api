import yaml
from weather_data.get_weather_data import getWeatherData
from weather_data.weather_data_transformation import weatherTransfo
from weather_data.weather_data_plot import weatherPlot

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    
primer = getWeatherData(config)
transformed = weatherTransfo(primer)
weatherPlot(transformed)

