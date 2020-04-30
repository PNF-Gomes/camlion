import numpy as np
import matplotlib.pyplot as plt
from utils import interpolation
import requests, json 

PEOPLE_COUNTER = 5
PHYSICAL_DISTANCE = 2
PEOPLE_PER_SQUARE_METER = 1
EXT_TEMPERATURE = 20
EXT_HUMIDITY = 35
WIND_SPEED = 7
GEO_RISK = 5

class ContagionRiskEvaluator:

    def __init__(self):
        #camera API variables
        self.physical_distance = PHYSICAL_DISTANCE   
        self.people_counter = PEOPLE_COUNTER
        self.people_per_square_meter = PEOPLE_PER_SQUARE_METER

        #external variables regarding exterior
        self.weather_info_acquirer = WeatherInfo()
        self.exterior_temperature =  EXT_TEMPERATURE
        self.exterior_humidity = EXT_HUMIDITY
        self.wind_speed = WIND_SPEED
        self.geo_risk = GEO_RISK
        self.air_pollution = 0.0 #idle for now

        #exernal variable regarding the interior
        self.ventilation = False
        self.indoor_temperature = 0.0

        #decay information
        self.decay_rate = 1/43.28
        self.initial_value = 1 #temp

    def update(self, physical_distance, people_counter, people_per_square_meter):
        self.physical_distance = physical_distance
        self.people_counter = people_counter
        self.people_per_square_meter = people_per_square_meter

    def physical_distance_norm(self):
        return self.normalize(self.physical_distance, 0, 2*self.people_counter/3)

    def people_per_square_meter_norm(self):
        return self.normalize(self.people_per_square_meter, 1/3, 1)

    def temperature_norm(self):
        return self.normalize(self.exterior_temperature, 35, 20)
    
    def humidity_norm(self):
        return self.normalize(self.exterior_humidity, 70, 35)
    
    def wind_speed_norm(self):
        return self.normalize(self.wind_speed, 2.8, 7)
    
    def normalize(self, value, low_risk_value, high_risk_value):
        return interpolation(low_risk_value, 0, high_risk_value, 1, value)

    def compute_risk(self):
        risk =  2.5*self.physical_distance_norm() + \
                2*self.people_per_square_meter_norm() + \
                1*self.wind_speed_norm() + \
                1*self.geo_risk + \
                0.6 * self.temperature_norm() + \
                0.4 * self.humidity_norm()
            
        if risk < 0:
            risk = 0
        elif risk > 10:
            risk = 10
    
        return risk

    def compute_environmental_risk(self):
        return self.temperature_norm() + self.humidity_norm()
    
    def compute_geo_risk(self):
        return self.geo_risk

class WeatherInfo():
    
    def __init__(self):
        self.api_key = "6d4be0a06273fcc9d1448610ab45f8d1"
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.city_name = "new york"
        self.complete_url = self.base_url + "appid=" + self.api_key + "&q=" + self.city_name

    def get_weather_info(self):
        response = requests.get(self.complete_url)
        x = response.json()
        if["cod"] !='404' or '401':
            weather_info = x["main"]
            current_temperature = (weather_info["temp"] - 273.15)//1 
            current_humidity = weather_info["humidity"]
            z = x["weather"]
        else:
            print("No weather info was found! 20oC and 70 humidity will be used")