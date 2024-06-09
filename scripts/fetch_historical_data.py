import os
import csv
import requests
from datetime import datetime, timedelta

def fetch_historical_weather(api_key, date):
    url = f'http://api.openweathermap.org/data/2.5/onecall/timemachine'
    params = {
        'lat': 47.3769,  # Latitude for Zurich
        'lon': 8.5417,   # Longitude for Zurich
        'dt': int(date.timestamp()),
        'appid': api_key,
        'units': 'metric'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        if 'current' in weather_data:
            return weather_data['current']['temp'], None
        else:
            return None, "Unexpected response format from weather API."
    except Exception as e:
        return None, f"Error fetching weather data: {e}"

def update_csv_with_historical_weather(data_file, api_key):
    if not os.path.exists(data_file):
        print(f"File {data_file} does not exist.")
        return

    with open(data_file, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = list(reader)

    # Manual mapping of German month names to English
    german_to_english_months = {
        'Januar': 'January', 'Februar': 'February', 'März': 'March', 'April': 'April',
        'Mai': 'May', 'Juni': 'June', 'Juli': 'July', 'August': 'August',
        'September': 'September', 'Oktober': 'October', 'November': 'November', 'Dezember': 'December'
    }

    updated_rows = []
    for row in rows:
        if row[4] == 'NaN':
            date_str = row[0]
            for german, english in german_to_english_months.items():
                date_str = date_str.replace(german, english)
            date = datetime.strptime(date_str, '%d. %B %Y %H.%M Uhr')
            temp, error = fetch_historical_weather(api_key, date)
            if error:
                print(f"Error fetching weather for {date_str}: {error}")
                updated_rows.append(row)
            else:
                row[4] = temp
                updated_rows.append(row)
        else:
            updated_rows.append(row)

    with open(data_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(updated_rows)

api_key = '352949661d130d8cf168b7edba44b8d3'
data_file = '../data/data2.csv'
update_csv_with_historical_weather(data_file, api_key)