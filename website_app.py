import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import locale

st.title('Obere Letten Status')

COMFORT_TEMP = 18

# # Set the locale to German to interpret 'Mai' as May
# try:
#     locale.setlocale(locale.LC_TIME, 'de_DE.utf8')
# except locale.Error:
#     try:
#         locale.setlocale(locale.LC_TIME, 'en_US.utf8')
#         st.warning("Locale 'de_DE.utf8' not found. Using 'en_US.utf8' instead.")
#     except locale.Error:
#         st.warning("Locale 'en_US.utf8' not found. Using default locale.")

# Function to load temperature data
def load_data():
    file_path = 'https://raw.githubusercontent.com/RobinSchmid7/river_temp_scraper/master/data/data.csv'
    # file_path = '/home/rschmid/git/river_temp_scraper/data/data.csv'  # Adjust the path as needed
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
        return data.sort_values(by='Date')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the temperature data
data = load_data()

# Filter to the most recent 7 days if there are more than 7 days of data
if len(data) > 7:
    data = data.tail(7)

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
    ax1.set_xticklabels(data['Date'].dt.strftime('%d %b %Y'), rotation=45)
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
    ax3.set_xticklabels(data['Date'].dt.strftime('%d %b %Y'), rotation=45)
    ax3.set_ylim(data['Flow'].min() - 50, data['Flow'].max() + 50)  # Adjust limits based on your data range
    ax3.legend(loc='upper left')
    plt.tight_layout()
    st.pyplot(fig_flow)
    
    # Plot open/close status
    fig_open, ax2 = plt.subplots(figsize=(10, 2))
    colors = ['green' if status == 1 else 'red' for status in data['Open']]
    ax2.bar(data['Date'], [1] * len(data), color=colors, width=0.1)  # Adjusted width to 0.1 for narrow bars
    ax2.set_title('Open/Close Status at Obere Letten', fontsize=16)
    ax2.set_xlabel('Date', fontsize=14)
    ax2.set_yticks([])
    ax2.set_xticks(data['Date'])
    ax2.set_xticklabels(data['Date'].dt.strftime('%d %b %Y'), rotation=45)
    plt.tight_layout()
    st.pyplot(fig_open)
else:
    st.markdown("No data available to display.")