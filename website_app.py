import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

st.title('Obere Letten Status')

COMFORT_TEMP = 18

# Function to load temperature data
def load_data():
    file_path = 'https://raw.githubusercontent.com/RobinSchmid7/river_temp_scraper/master/data/data.csv'
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

# Load the temperature data
data = load_data()

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
    sns.lineplot(x='Date', y='Temp', data=data, marker='o', color='dodgerblue', label='Daily Temperature', ax=ax1)
    ax1.fill_between(data['Date'], data['Temp'] - 1, data['Temp'] + 1, color='dodgerblue', alpha=0.3)
    ax1.axhline(COMFORT_TEMP, color='green', lw=2, ls='--', label="Robin's comfortable temperature")
    ax1.set_title('Water Temperature at Obere Letten', fontsize=16)
    ax1.set_xlabel('Date', fontsize=14)
    ax1.set_ylabel('Temperature (°C)', fontsize=14)
    ax1.set_xticks(data['Date'])
    ax1.set_xticklabels(data['Date'].dt.strftime('%d %b %Y %H:%M'), rotation=45)
    ax1.set_ylim(0, 30)
    ax1.legend(loc='upper left')
    plt.tight_layout()
    st.pyplot(fig_temp)
    
    # Plot water flow data
    fig_flow, ax3 = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='Date', y='Flow', data=data, marker='o', color='mediumseagreen', label='Daily Water Flow', ax=ax3)
    ax3.fill_between(data['Date'], data['Flow'] - 10, data['Flow'] + 10, color='mediumseagreen', alpha=0.3)
    ax3.set_title('Water Flow at Obere Letten', fontsize=16)
    ax3.set_xlabel('Date', fontsize=14)
    ax3.set_ylabel('Water Flow (m³/l)', fontsize=14)
    ax3.set_xticks(data['Date'])
    ax3.set_xticklabels(data['Date'].dt.strftime('%d %b %Y %H:%M'), rotation=45)
    ax3.set_ylim(data['Flow'].min() - 50, data['Flow'].max() + 50)  # Adjust limits based on your data range
    ax3.legend(loc='upper left')
    plt.tight_layout()
    st.pyplot(fig_flow)
    
    # Plot open/close status as a 1D line with green and red dots
    fig_open, ax2 = plt.subplots(figsize=(10, 3))
    colors = ['green' if status == 1 else 'red' for status in data['Open']]
    ax2.scatter(data['Date'], [1] * len(data), color=colors, s=100)
    ax2.set_title('Open/Close Status at Obere Letten', fontsize=16)
    ax2.set_xlabel('Date', fontsize=14)
    ax2.set_yticks([])
    ax2.set_xticks(data['Date'])
    ax2.set_xticklabels(data['Date'].dt.strftime('%d %b %Y %H:%M'), rotation=45)
    plt.tight_layout()
    st.pyplot(fig_open)
else:
    st.markdown("No data available to display.")
