import os
import time
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.graph_objects as go

from constants import SAMPLING_INTERVAL_SECONDS, HUMIDITY, DATA_FILE, TIMESTAMP, TEMPERATURE, CO2_PPM

DASHBOARD_USERNAME = "piwheeze"

authenticator = stauth.Authenticate(
    {
        "usernames": {
            DASHBOARD_USERNAME: {
                "name": "PiWheeze",
                "password": os.environ["DASHBOARD_PASSWORD_HASH"],
            }
        }
    },
    "piwheeze_auth",
    os.environ["DASHBOARD_COOKIE_KEY"],
    365,
    auto_hash=False,
)

authenticator.login()

if st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password")
    st.stop()

authenticator.logout("Log out", "sidebar")

st.title("CO₂ Sensor Dashboard")

# Optional: show live numeric values
st.subheader("Live Readings")
co2_text = st.empty()
temp_text = st.empty()
hum_text = st.empty()

# Chart placeholder
st.subheader("Historical CO₂")
# Streamlit has no way to preserve a Plotly chart's zoom/pan across a redraw in
# this app's architecture (a plain script loop, not a rerun per data point) -
# every redraw is a fresh chart as far as the browser is concerned. So instead
# of fighting that, a freeze toggle stops redraws altogether on request, which
# is the only way to guarantee a zoom you set actually stays put. Check it
# *before* zooming in, then zoom/pan freely - it won't be touched again until
# you uncheck it.
freeze = st.checkbox("⏸️ Freeze view (pause updates so zoom/pan stays put)")
chart_placeholder = st.empty()


def render() -> None:
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        st.warning("Data file not found yet...")
        return

    if df.empty:
        return

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


# Always draw once immediately: on first load, and also whenever toggling the
# freeze checkbox restarts this script (a fresh run starts with an empty page,
# so skipping this on a frozen run would leave the chart blank instead of
# showing the last known values).
render()

while True:
    time.sleep(SAMPLING_INTERVAL_SECONDS)
    if not freeze:
        render()
