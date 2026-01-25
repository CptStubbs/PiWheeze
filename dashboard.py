import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        fig = go.Figure()

        # CO2 on primary y-axis
        fig.add_trace(go.Scatter(
            x=df[TIMESTAMP],
            y=df[CO2_PPM],
            mode='lines',
            name='CO2 ppm',
            yaxis='y1'
        ))
        # Temperature on secondary y-axis
        fig.add_trace(go.Scatter(
            x=df[TIMESTAMP],
            y=df[TEMPERATURE],
            mode='lines',
            name='Temperature °C',
            yaxis='y2'
        ))

        # Humidity on secondary y-axis
        fig.add_trace(go.Scatter(
            x=df[TIMESTAMP],
            y=df[HUMIDITY],
            mode='lines',
            name='Humidity %',
            yaxis='y2'
        ))

        # Layout with two y-axes
        fig.update_layout(
            title="CO2 / Temperature / Humidity History",
            xaxis=dict(title="Time"),
            yaxis=dict(
                title="CO2 ppm",
                side='left'
            ),
            yaxis2=dict(
                title="Temp / Humidity",
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0, y=1)
        )

        chart_placeholder.plotly_chart(fig)

    time.sleep(SAMPLING_INTERVAL_SECONDS)