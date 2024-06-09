import os
import requests
from bs4 import BeautifulSoup
import re
import csv

def get_soup(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

def extract_temperature(soup):
    temp_element = soup.find('td', id="baederinfos_temperature_value")
    if not temp_element:
        return None, "Temperature element not found"
    temp_text = temp_element.text.strip()
    temp_match = re.search(r'(\d+)\s*°', temp_text)
    if not temp_match:
        return None, "Temperature not found in the expected format"
    return int(temp_match.group(1)), None

def extract_open_status(soup):
    status_element = soup.find('td', id="baederinfos_status_value")
    if not status_element:
        return None, "Status element not found"
    return 1 if "offen" in status_element.text.lower() else 0, None

def extract_date(soup):
    date_element = soup.find('td', id="baederinfos_status_updated")
    if not date_element:
        return None, "Date element not found"
    date_text = date_element.text.strip()
    date_match = re.search(r'\d{1,2}\.\s*\w+\s*\d{4}\s*\d{1,2}\.\d{2}\s*Uhr', date_text)
    if not date_match:
        return None, "Date not found in the expected format"
    return date_match.group(0), None

def extract_river_data(soup):
    rows = soup.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 4 and 'Limmat-Unterhard' in cells[0].text:
            return cells[3].text.strip(), None
    return "Not Found", None

def get_current_weather(api_key):
    url = f'http://api.openweathermap.org/data/2.5/weather?q=Zurich&appid={api_key}&units=metric'
    try:
        response = requests.get(url)
        weather_data = response.json()
        if 'main' in weather_data:
            return weather_data['main']['temp'], None
        else:
            return None, "Unexpected response format from weather API."
    except Exception as e:
        return None, f"Error fetching weather data: {e}"

def save_to_csv(data, data_file):
    write_header = not os.path.exists(data_file)
    with open(data_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(['Date', 'Temp', 'Open', 'River Data', 'Outside Temp'])
        writer.writerow(data)

def remove_duplicates_from_csv(data_file):
    if not os.path.exists(data_file):
        return

    with open(data_file, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = list(reader)

    unique_rows = []
    seen = set()
    for row in rows:
        row_tuple = tuple(row)
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_rows.append(row)

    with open(data_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(unique_rows)

def fetch_temperature_info(url1, url2, api_key):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'
    }
    try:
        main_soup = get_soup(url1, headers)
        temperature, temp_error = extract_temperature(main_soup)
        if temp_error:
            return temp_error
        is_open, open_error = extract_open_status(main_soup)
        if open_error:
            return open_error
        date, date_error = extract_date(main_soup)
        if date_error:
            return date_error

        river_soup = get_soup(url2, headers)
        river_data, river_error = extract_river_data(river_soup)
        if river_error:
            return river_error

        outside_temp, weather_error = get_current_weather(api_key)
        if weather_error:
            return weather_error

        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, '../data')
        os.makedirs(data_dir, exist_ok=True)
        data_file = os.path.join(data_dir, 'data.csv')
        save_to_csv([date, temperature, is_open, river_data, outside_temp], data_file)
        remove_duplicates_from_csv(data_file)

        return f"Data saved: Date - {date}, Temperature - {temperature}°C, Open - {is_open}, River Data - {river_data}, Outside Temp - {outside_temp}°C"
    except requests.RequestException as e:
        return f"An error occurred: {e}"

url1 = "https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/flussbad_oberer_letten.html"
url2 = "https://hydroproweb.zh.ch/Listen/AktuelleWerte/aktuelle_werte.html"
api_key = '352949661d130d8cf168b7edba44b8d3'
result = fetch_temperature_info(url1, url2, api_key)
print(result)
