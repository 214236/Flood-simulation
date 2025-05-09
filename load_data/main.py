# Windows
# pip install openmeteo-requests
# pip install requests-cache retry-requests numpy pandas
#
# Linux Ubuntu
# pip3 install --break-system-packages openmeteo-requests requests-cache retry-requests numpy pandas


import openmeteo_requests

import math
import numpy as np
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Define the bounding coordinates of the grid
a, b = 50.70, 15.90   # starting point [latitude, longitude]
c, d = 51.00, 16.20   # ending point [latitude, longitude]
step = 0.1            # resolution of the grid (in degrees)



# Calculate the number of points based on the step
num_latitudes = int((c - a) / step) + 1
num_longitudes = int((d - b) / step) + 1

# Generate arrays of latitude and longitude values using linspace
latitudes = np.linspace(a, c, num_latitudes)
longitudes = np.linspace(b, d, num_longitudes)

# Create a meshgrid of all combinations of latitudes and longitudes
grid_lat, grid_lon = np.meshgrid(latitudes, longitudes, indexing='ij')

# Flatten the 2D arrays into 1D lists
lat_list = grid_lat.flatten().tolist()
lon_list = grid_lon.flatten().tolist()

# Round the latitudes and longitudes
r = -math.floor(math.log10(step))
lat_list = [round(lat, r) for lat in lat_list]
lon_list = [round(lon, r) for lon in lon_list]



# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": lat_list,
	"longitude": lon_list,
	"start_date": "2024-01-01",
	"end_date": "2024-12-31",
	"daily": ["rain_sum", "snowfall_sum", "wind_direction_10m_dominant", "wind_speed_10m_max", "temperature_2m_mean", "surface_pressure_mean", "soil_moisture_0_to_100cm_mean"]
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_rain_sum = daily.Variables(0).ValuesAsNumpy()
daily_snowfall_sum = daily.Variables(1).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(2).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()
daily_temperature_2m_mean = daily.Variables(4).ValuesAsNumpy()
daily_surface_pressure_mean = daily.Variables(5).ValuesAsNumpy()
daily_soil_moisture_0_to_100cm_mean = daily.Variables(6).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["rain_sum"] = daily_rain_sum
daily_data["snowfall_sum"] = daily_snowfall_sum
daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
daily_data["surface_pressure_mean"] = daily_surface_pressure_mean
daily_data["soil_moisture_0_to_100cm_mean"] = daily_soil_moisture_0_to_100cm_mean

daily_dataframe = pd.DataFrame(data = daily_data)

daily_dataframe.to_csv("daily_weather_data.csv", index=False)

print("Data saved to 'daily_weather_data.csv'")

