import os
import requests
from bs4 import BeautifulSoup
import re
import csv

def fetch_temperature_info(url):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract temperature
        temp_element = soup.find('td', id="baederinfos_temperature_value")
        if not temp_element:
            return "Temperature element not found"
        temp_text = temp_element.text.strip()
        temp_match = re.search(r'(\d+)\s*°', temp_text)
        if not temp_match:
            return "Temperature not found in the expected format"
        temperature = temp_match.group(1)

        # Extract open status
        status_element = soup.find('td', id="baederinfos_status_value")
        if not status_element:
            return "Status element not found"
        is_open = 1 if "offen" in status_element.text.lower() else 0

        # Extract date
        date_element = soup.find('td', id="baederinfos_status_updated")
        if not date_element:
            return "Date element not found"
        date_text = date_element.text.strip()
        date_match = re.search(r'\d{1,2}\.\s*\w+\s*\d{4}\s*\d{1,2}\.\d{2}\s*Uhr', date_text)
        if not date_match:
            return "Date not found in the expected format"
        date = date_match.group(0)

        print(f"Date: {date}, Temperature: {temperature}°C, Open: {is_open}")

        # Use absolute path for the data directory
        data_dir = os.path.abspath('../data')
        os.makedirs(data_dir, exist_ok=True)
        data_file = os.path.join(data_dir, 'data.csv')

        write_header = not os.path.exists(data_file)

        with open(data_file, 'a', newline='') as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(['Date', 'Temp', 'Open'])
            writer.writerow([date, temperature, is_open])

        return f"Data saved: Date - {date}, Temperature - {temperature}°C, Open - {is_open}"

    except requests.RequestException as e:
        return f"An error occurred: {e}"

url = "https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/flussbad_oberer_letten.html"
result = fetch_temperature_info(url)
print(result)