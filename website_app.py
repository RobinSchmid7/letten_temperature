import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import requests

st.title('[Obere Letten Status](https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/flussbad_oberer_letten.html)')

# Function to load temperature data
def load_data():
    file_path = 'https://raw.githubusercontent.com/RobinSchmid7/letten_temperature/master/data/data.csv'
    try:
        data = pd.read_csv(file_path, dayfirst=True)
        
        # Manual mapping of German month names to English
        german_to_english_months = {
            'Januar': 'January', 'Februar': 'February', 'März': 'March', 'April': 'April',
            'Mai': 'May', 'Juni': 'June', 'Juli': 'July', 'August': 'August',
            'September': 'September', 'Oktober': 'October', 'November': 'November', 'Dezember': 'December'
        }
        for german, english in german_to_english_months.items():
            data['Date'] = data['Date'].str.replace(german, english)
        
        # Adjust the format to match the date and time in the CSV
        data['Date'] = pd.to_datetime(data['Date'], format='%d. %B %Y %H.%M Uhr')
        # Ensure each date has only one data point, for safety
        data = data.drop_duplicates(subset='Date', keep='first')
        
        # Filter data to ensure points are at least 3 hours apart
        data = data.sort_values(by='Date')
        data = data[data['Date'].diff().dt.total_seconds() > 3 * 3600]
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Function to get current weather data
def get_weather():
    api_key = '352949661d130d8cf168b7edba44b8d3'  # Replace with your OpenWeatherMap API key
    url = f'http://api.openweathermap.org/data/2.5/weather?q=Zurich&appid={api_key}&units=metric'
    try:
        response = requests.get(url)
        weather_data = response.json()
        
        # Check if the expected keys are in the response
        if 'main' in weather_data and 'weather' in weather_data:
            temp = weather_data['main']['temp']
            sunshine = weather_data['weather'][0]['description']
            return temp, sunshine
        else:
            st.error("Unexpected response format from weather API.")
            return None, None
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None, None

# Load the temperature data
data = load_data()

# Get current weather data
current_temp, current_sunshine = get_weather()

# Display current weather data
if current_temp is not None and current_sunshine is not None:
    st.markdown(f"### Current Weather in Zurich")
    st.markdown(f"**Temperature:** {current_temp} °C")
    st.markdown(f"**Sunshine:** {current_sunshine}")

st.markdown(f"### Current Status of Swimming Place Obere Letten")
# Filter to the most recent 14 days
if not data.empty:
    last_date = data['Date'].max()
    start_date = last_date - timedelta(days=14)
    data = data[data['Date'] > start_date]

# Visualize the data if it's not empty
if not data.empty:
    sns.set_theme(style="whitegrid")
    
    # Plot temperature data
    fig_temp, ax1 = plt.subplots(figsize=(10, 6))
        
    # Compute and plot the monthly average water temperature
    last_month_date = last_date - timedelta(days=30)
    monthly_avg_temp = data[data['Date'] > last_month_date]['WaterTemp'].mean()
    ax1.axhline(monthly_avg_temp, color='lightblue', lw=2, ls='--', label=f"Monthly Average Water Temp: {monthly_avg_temp:.2f} °C", zorder=1)
    
    sns.lineplot(x='Date', y='WaterTemp', data=data, marker='o', color='dodgerblue', label='Current Water Temperature', ax=ax1, linewidth=2.5, zorder=2)
    
    # Filter data to only include times between 12:00 and 18:00 for outside temperature
    outside_temp_data = data[(data['Date'].dt.hour >= 12) & (data['Date'].dt.hour <= 18)]
    
    sns.lineplot(x='Date', y='OutsideTemp', data=outside_temp_data, marker='o', color='red', label='Current Outside Temperature', ax=ax1, linewidth=2.5, zorder=2)
    
    # Compute and plot the monthly average outside temperature
    monthly_avg_outside_temp = outside_temp_data['OutsideTemp'].mean()
    ax1.axhline(monthly_avg_outside_temp, color='orange', lw=2, ls='--', label=f"Monthly Average Outside Temp: {monthly_avg_outside_temp:.2f} °C", zorder=1)
    
    ax1.set_title('Water and Outside Temperature', fontsize=16)
    ax1.set_xlabel('Date', fontsize=14)
    ax1.set_ylabel('Temperature (°C)', fontsize=14)
    ax1.set_xticks(data['Date'])
    ax1.set_xticklabels(data['Date'].dt.strftime('%d %b %H:%M'), rotation=90)
    ax1.set_ylim(min(data['WaterTemp'].min(), data['OutsideTemp'].min()) - 5, max(data['WaterTemp'].max(), data['OutsideTemp'].max()) + 5)
    ax1.legend(loc='upper left')
    ax1_right = ax1.twinx()
    ax1_right.set_yticks(ax1.get_yticks())
    ax1_right.set_ylim(ax1.get_ylim())
    plt.tight_layout()
    st.pyplot(fig_temp)
    
    # Plot water flow data
    fig_flow, ax3 = plt.subplots(figsize=(10, 6))
        
    # Compute and plot the monthly average water flow
    monthly_avg_flow = data[data['Date'] > last_month_date]['Flow'].mean()
    ax3.axhline(monthly_avg_flow, color='orange', lw=2, ls='--', label=f"Monthly Average Flow: {monthly_avg_flow:.2f} m³/s", zorder=1)
    
    sns.lineplot(x='Date', y='Flow', data=data, marker='o', color='dodgerblue', label='Current Water Flow', ax=ax3, linewidth=2.5, zorder=2)
    
    ax3.set_title('Water Flow', fontsize=16)
    ax3.set_xlabel('Date', fontsize=14)
    ax3.set_ylabel('Water Flow (m³/s)', fontsize=14)
    ax3.set_xticks(data['Date'])
    ax3.set_xticklabels(data['Date'].dt.strftime('%d %b %H:%M'), rotation=90)
    ax3.set_ylim(data['Flow'].min() - 50, data['Flow'].max() + 50)  # Adjust limits based on your data range
    ax3.legend(loc='upper left')
    ax3_right = ax1.twinx()
    ax3_right.set_yticks(ax1.get_yticks())
    ax3_right.set_ylim(ax1.get_ylim())
    plt.tight_layout()
    st.pyplot(fig_flow)
    
    # Plot open/close status as a 1D line with green and red dots
    fig_open, ax2 = plt.subplots(figsize=(10, 3))
    colors = ['green' if status == 1 else 'red' for status in data['Open']]
    ax2.scatter(data['Date'], [1] * len(data), color=colors, s=100)
    ax2.set_title('Open/Close Status', fontsize=16)
    ax2.set_xlabel('Date', fontsize=14)
    ax2.set_yticks([])
    ax2.set_xticks(data['Date'])
    ax2.set_xticklabels(data['Date'].dt.strftime('%d %b %H:%M'), rotation=90)
    plt.tight_layout()
    st.pyplot(fig_open)
else:
    st.markdown("No data available to display.")

# Author credentials
st.markdown("© 2024 [Robin Schmid](https://github.com/RobinSchmid7)")
