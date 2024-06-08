import requests
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

# Function to get current weather data
def get_current_weather(city):
    api_key = "b3c62ae7f7ad5fc3cb0a7b56cb7cbda6"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for any HTTP errors
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error occurred: {err}")
        return None
    except Exception as err:
        st.error(f"An error occurred: {err}")
        return None

    try:
        data = response.json()
        if data['cod'] != 200:
            st.error(f"Error: {data['message']}")
            return None
        return data
    except json.JSONDecodeError as err:
        st.error(f"Failed to parse response JSON: {err}")
        return None

# Function to get weather forecast data
def get_weather_forecast(city):
    api_key = "b3c62ae7f7ad5fc3cb0a7b56cb7cbda6"
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for any HTTP errors
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error occurred: {err}")
        return None
    except Exception as err:
        st.error(f"An error occurred: {err}")
        return None

    try:
        data = response.json()
        if data['cod'] != "200":
            st.error(f"Error: {data['message']}")
            return None
        return data
    except json.JSONDecodeError as err:
        st.error(f"Failed to parse response JSON: {err}")
        return None

# Function to plot weather forecast data
def plot_weather_forecast(data):
    forecast_list = data['list']
    dates = [item['dt_txt'] for item in forecast_list]
    temperatures = [item['main']['temp'] for item in forecast_list]
    temperatures_celsius = [round(temp - 273.15, 2) for temp in temperatures]
    humidity = [item['main']['humidity'] for item in forecast_list]
    pressure = [item['main']['pressure'] for item in forecast_list]

    df = pd.DataFrame({
        'Date': dates,
        'Temperature (°C)': temperatures_celsius,
        'Humidity (%)': humidity,
        'Pressure (hPa)': pressure
    })

    fig = px.line(df, x='Date', y=['Temperature (°C)', 'Humidity (%)', 'Pressure (hPa)'],
                  title=f"5-Day Weather Forecast for {data['city']['name']}",
                  labels={'value': 'Value', 'variable': 'Metric'})
    st.plotly_chart(fig)

# Streamlit app layout
st.header("Advanced Weather Data Visualization")
st.image("https://images.theconversation.com/files/442675/original/file-20220126-17-1i0g402.jpg?ixlib=rb-1.1.0&q=45&auto=format&w=1356&h=668&fit=crop")

city = st.text_input("Enter city name")
if st.button("Get Weather"):
    if city:
        current_weather = get_current_weather(city)
        weather_data = get_weather_forecast(city)
        
        if current_weather:
            st.subheader(f"Current Weather in {city}")
            weather_description = current_weather['weather'][0]['description']
            temperature = round(current_weather['main']['temp'] - 273.15, 2)
            humidity = current_weather['main']['humidity']
            pressure = current_weather['main']['pressure']
            lat = current_weather['coord']['lat']
            lon = current_weather['coord']['lon']

            st.metric(label="Temperature (°C)", value=temperature)
            st.metric(label="Humidity (%)", value=humidity)
            st.metric(label="Pressure (hPa)", value=pressure)
            st.write(f"**Weather Description:** {weather_description.capitalize()}")

            st.subheader("City Location")
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=lat,
                    longitude=lon,
                    zoom=10,
                    pitch=50,
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=pd.DataFrame({'lat': [lat], 'lon': [lon]}),
                        get_position='[lon, lat]',
                        get_color='[200, 30, 0, 160]',
                        get_radius=10000,
                    ),
                ],
            ))

        if weather_data:
            st.subheader("5-Day Weather Forecast")
            plot_weather_forecast(weather_data)
    else:
        st.error("Please enter a city name.")
