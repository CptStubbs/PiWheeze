import os
import time
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd

import charts
from readings import live_readings
from constants import (SAMPLING_INTERVAL_SECONDS, DATA_FILE, TIMESTAMP, CO2_PPM, TEMPERATURE, HUMIDITY,
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

# Latest value of each reading, its status against the warning thresholds, and when it was measured
st.subheader("Live Readings")
readings_slot = st.empty()

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


def read_history(path: str, value_columns: list[str]) -> pd.DataFrame | None:
    """The CSV at path without sensor-down rows (no timestamp or no values), or None if it doesn't exist yet."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        return None
    return df.dropna(subset=[TIMESTAMP]).dropna(subset=value_columns, how="all")


def render() -> None:
    environment = read_history(DATA_FILE, [CO2_PPM, TEMPERATURE, HUMIDITY])
    particulates = read_history(PM_DATA_FILE, [PM1_0, PM2_5, PM10])

    def latest(df):
        return None if df is None or df.empty else df.iloc[-1]

    readings_slot.table(live_readings(latest(environment), latest(particulates)))

    if environment is None:
        st.warning("Data file not found yet...")
    elif not environment.empty:
        co2_slot.plotly_chart(charts.co2_chart(environment))
        temp_slot.plotly_chart(charts.temperature_chart(environment))
        hum_slot.plotly_chart(charts.humidity_chart(environment))

    if particulates is not None and not particulates.empty:
        pm25_slot.plotly_chart(charts.pm2_5_chart(particulates))
        pm10_slot.plotly_chart(charts.pm10_chart(particulates))


# Always draw once immediately: on first load, and also whenever toggling the
# freeze checkbox restarts this script (a fresh run starts with an empty page,
# so skipping this on a frozen run would leave the chart blank instead of
# showing the last known values).
render()

while True:
    time.sleep(SAMPLING_INTERVAL_SECONDS)
    if not freeze:
        render()
