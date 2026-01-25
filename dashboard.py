import streamlit as st
import pandas as pd
import plotly.express as px
import time

from constants import SAMPLING_INTERVAL_SECONDS, HUMIDITY, DATA_FILE, TIMESTAMP, TEMPERATURE, CO2_PPM

st.title("CO₂ Sensor Dashboard")

# Optional: show live numeric values
st.subheader("Live Readings")
co2_text = st.empty()
temp_text = st.empty()
hum_text = st.empty()

# Chart placeholder
st.subheader("Historical CO₂")
chart_placeholder = st.empty()

while True:
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        st.warning("Data file not found yet...")
        time.sleep(SAMPLING_INTERVAL_SECONDS)
        continue

    if not df.empty:
        # Show latest values
        latest = df.iloc[-1]
        co2_text.text(f"CO₂: {latest[CO2_PPM]:.1f} ppm")
        temp_text.text(f"Temperature: {latest[TEMPERATURE]:.1f} °C")
        hum_text.text(f"Humidity: {latest[HUMIDITY]:.1f} %")

        # Plot history
        fig = px.line(df, x=TIMESTAMP, y=[CO2_PPM, TEMPERATURE, HUMIDITY], title="CO₂ History")
        chart_placeholder.plotly_chart(fig)

    time.sleep(SAMPLING_INTERVAL_SECONDS)