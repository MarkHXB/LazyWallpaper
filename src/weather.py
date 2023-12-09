import datetime
from enum import Enum, auto

import requests
import json


class WeatherType(Enum):
    CLEAR_SKY = auto()
    CLEAR = auto()
    MAINLY_CLEAR = auto()
    PARTLY_CLOUDY = auto()
    OVERCAST = auto()
    FOG = auto()
    DRIZZLE = auto()
    FREEZING_DRIZZLE = auto()
    RAIN = auto()
    FREEZING_RAIN = auto()
    SNOW_FALL = auto()
    SNOW_GRAINS = auto()
    RAIN_SHOWERS = auto()
    SNOW_SHOWERS = auto()
    THUNDERSTORM_SLIGHT_MODERATE = auto()
    THUNDERSTORM_WITH_HAIL = auto()


class Season(Enum):
    SPRING = (3, 4, 5)
    SUMMER = (6, 7, 8)
    AUTUMN = (9, 10, 11)
    WINTER = (12, 1, 2)


def get_location_by_ip():
    url = 'http://ipinfo.io/json'
    res = requests.get(url)
    res.raise_for_status()
    data = json.loads(res.text)
    loc = data['loc']
    lat = loc.split(',')[0]
    lon = loc.split(',')[1]
    return lat, lon


def get_open_meteo_api_url(lat, lon):
    return f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code&timezone=auto&forecast_days=1'


def get_wmo(lat, lon):
    url = get_open_meteo_api_url(lat, lon)
    res = requests.get(url)
    res.raise_for_status()
    data = json.loads(res.text)
    weather_code = data.get("daily", {}).get("weather_code", [])[0]
    return weather_code


def get_current_weather():
    # get latitude and longitude by ip
    lat, lon = get_location_by_ip()

    # get weather code by lat, lon
    wmo = get_wmo(lat, lon)

    # return weather type in humanreadable format
    weather_codes = {
        WeatherType.CLEAR_SKY: [0],
        WeatherType.CLEAR: [],
        WeatherType.MAINLY_CLEAR: [1, 2],
        WeatherType.PARTLY_CLOUDY: [3],
        WeatherType.OVERCAST: [],
        WeatherType.FOG: [45, 48],
        WeatherType.DRIZZLE: [51, 53, 55],
        WeatherType.FREEZING_DRIZZLE: [56, 57],
        WeatherType.RAIN: [61, 63, 65],
        WeatherType.FREEZING_RAIN: [66, 67],
        WeatherType.SNOW_FALL: [71, 73, 75],
        WeatherType.SNOW_GRAINS: [77],
        WeatherType.RAIN_SHOWERS: [80, 81, 82],
        WeatherType.SNOW_SHOWERS: [85, 86],
        WeatherType.THUNDERSTORM_SLIGHT_MODERATE: [95],
        WeatherType.THUNDERSTORM_WITH_HAIL: [96, 99],
    }

    # find weather type value by wmo
    for weather_type, codes in weather_codes.items():
        if wmo in codes:
            return weather_type

    # return default weather type if wmo not in codes
    return WeatherType.CLEAR_SKY


def get_current_season():
    current_month = datetime.datetime.now().month

    if 3 <= current_month <= 5:
        return 'Spring'
    elif 6 <= current_month <= 8:
        return 'Summer'
    elif 9 <= current_month <= 11:
        return 'Autumn'
    else:
        return 'Winter'


def get_weather_params():
    return f'background {get_current_season()} {get_current_weather().name.title().replace("_"," ")} Nature'
