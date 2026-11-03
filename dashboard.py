import os
import time
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.graph_objects as go

from constants import (SAMPLING_INTERVAL_SECONDS, HUMIDITY, DATA_FILE, TIMESTAMP, TEMPERATURE, CO2_PPM,
                       PM1_0, PM2_5, PM10, PM_DATA_FILE)

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
co2_chart = st.empty()
temp_chart = st.empty()
hum_chart = st.empty()
pm_chart = st.empty()


def fmt_time(timestamp: str) -> str:
    """ISO timestamp from the CSV -> 'YYYY-MM-DD HH:MM:SS' (the Pi's local time)."""
    return str(timestamp).replace("T", " ")[:19]


def line_chart(placeholder, df: pd.DataFrame, series: list[tuple[str, str]], title: str, unit: str) -> None:
    """Draw one chart; series is a list of (column, legend name) sharing one y-axis."""
    fig = go.Figure()
    for column, name in series:
        fig.add_trace(go.Scatter(x=df[TIMESTAMP], y=df[column], mode='lines', name=name))
    fig.update_layout(
        title=title,
        xaxis=dict(title="Time"),
        yaxis=dict(title=unit),
        legend=dict(x=0, y=1)
    )
    placeholder.plotly_chart(fig)


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
    line_chart(pm_chart, df,
               [(PM1_0, "PM1.0"), (PM2_5, "PM2.5"), (PM10, "PM10")],
               "Particulate History", "µg/m³")


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

    line_chart(co2_chart, df, [(CO2_PPM, "CO2 ppm")], "CO₂ History", "ppm")
    line_chart(temp_chart, df, [(TEMPERATURE, "Temperature °C")], "Temperature History", "°C")
    line_chart(hum_chart, df, [(HUMIDITY, "Humidity %")], "Humidity History", "%")


# Always draw once immediately: on first load, and also whenever toggling the
# freeze checkbox restarts this script (a fresh run starts with an empty page,
# so skipping this on a frozen run would leave the chart blank instead of
# showing the last known values).
render()

while True:
    time.sleep(SAMPLING_INTERVAL_SECONDS)
    if not freeze:
        render()
