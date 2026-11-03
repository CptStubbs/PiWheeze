import os
import time
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd

import charts
from constants import (SAMPLING_INTERVAL_SECONDS, HUMIDITY, DATA_FILE, TIMESTAMP, TEMPERATURE, CO2_PPM,
                       PM1_0, PM2_5, PM10, PM_DATA_FILE)

DASHBOARD_USERNAME = "piwheeze"

st.set_page_config(page_title="Sensor Dashboard")

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

st.title("Sensor Dashboard")

# Live numeric values, each with the time it was measured
st.subheader("Live Readings")
co2_text = st.empty()
temp_text = st.empty()
hum_text = st.empty()
pm_text = st.empty()

# Streamlit has no way to preserve a Plotly chart's zoom/pan across a redraw in
# this app's architecture (a plain script loop, not a rerun per data point) -
# every redraw is a fresh chart as far as the browser is concerned. So instead
# of fighting that, a freeze toggle stops redraws altogether on request, which
# is the only way to guarantee a zoom you set actually stays put. Check it
# *before* zooming in, then zoom/pan freely - it won't be touched again until
# you uncheck it.
freeze = st.checkbox("⏸️ Freeze view (pause updates so zoom/pan stays put)")

# One chart per quantity: they have unrelated scales, so sharing axes looked messy
st.subheader("Historical Readings")
co2_slot = st.empty()
temp_slot = st.empty()
hum_slot = st.empty()
pm25_slot = st.empty()
pm10_slot = st.empty()


def fmt_time(timestamp: str) -> str:
    """ISO timestamp from the CSV -> 'YYYY-MM-DD HH:MM:SS' (the Pi's local time)."""
    return str(timestamp).replace("T", " ")[:19]


def render_pm() -> None:
    try:
        df = pd.read_csv(PM_DATA_FILE)
    except FileNotFoundError:
        pm_text.text("Particulates: no data file yet (is the PMSA003I connected?)")
        return

    # Rows logged while the sensor was down are blank; drop them
    df = df.dropna(subset=[TIMESTAMP, PM2_5])
    if df.empty:
        return

    latest = df.iloc[-1]
    pm_text.text(
        f"PM1.0: {latest[PM1_0]:.0f} µg/m³   "
        f"PM2.5: {latest[PM2_5]:.0f} µg/m³   "
        f"PM10: {latest[PM10]:.0f} µg/m³   "
        f"(measured {fmt_time(latest[TIMESTAMP])})"
    )
    pm25_slot.plotly_chart(charts.pm2_5_chart(df))
    pm10_slot.plotly_chart(charts.pm10_chart(df))


def render() -> None:
    render_pm()
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        st.warning("Data file not found yet...")
        return

    if df.empty:
        return

    # Show latest values
    latest = df.iloc[-1]
    measured = f"(measured {fmt_time(latest[TIMESTAMP])})"
    co2_text.text(f"CO₂: {latest[CO2_PPM]:.1f} ppm   {measured}")
    temp_text.text(f"Temperature: {latest[TEMPERATURE]:.1f} °C   {measured}")
    hum_text.text(f"Humidity: {latest[HUMIDITY]:.1f} %   {measured}")

    co2_slot.plotly_chart(charts.co2_chart(df))
    temp_slot.plotly_chart(charts.temperature_chart(df))
    hum_slot.plotly_chart(charts.humidity_chart(df))


# Always draw once immediately: on first load, and also whenever toggling the
# freeze checkbox restarts this script (a fresh run starts with an empty page,
# so skipping this on a frozen run would leave the chart blank instead of
# showing the last known values).
render()

while True:
    time.sleep(SAMPLING_INTERVAL_SECONDS)
    if not freeze:
        render()
