import pandas as pd

from constants import (CO2_PPM, CO2_WARNING_PPM,
                       HUMIDITY, HUMIDITY_WARNING_PERCENT,
                       PM1_0, PM2_5, PM10,
                       PM2_5_CAUTION_UG_M3, PM2_5_WARNING_UG_M3,
                       PM10_CAUTION_UG_M3, PM10_WARNING_UG_M3,
                       TEMPERATURE, TEMPERATURE_WARNING_C,
                       TIMESTAMP)

# Live readings table for the dashboard. Kept free of Streamlit so it can be
# tested from plain pandas rows; see tests/test_readings.py.

OK = "🟢 OK"
CAUTION = "🟡 Elevated"
WARNING = "🔴 High"
NO_DATA = "⚪ No data"

# (column, label, unit, decimals, tiers); tiers are (value above which it applies, status)
# lowest first, using the same thresholds as the chart warning bands. A reading with no
# tiers (PM1.0 has no guideline) shows a blank status.
ENVIRONMENT_READINGS = (
    (CO2_PPM, "CO₂", "ppm", 0, ((CO2_WARNING_PPM, WARNING),)),
    (TEMPERATURE, "Temperature", "°C", 1, ((TEMPERATURE_WARNING_C, WARNING),)),
    (HUMIDITY, "Humidity", "%", 0, ((HUMIDITY_WARNING_PERCENT, WARNING),)),
)
PARTICULATE_READINGS = (
    (PM1_0, "PM1.0", "µg/m³", 0, ()),
    (PM2_5, "PM2.5", "µg/m³", 0, ((PM2_5_CAUTION_UG_M3, CAUTION), (PM2_5_WARNING_UG_M3, WARNING))),
    (PM10, "PM10", "µg/m³", 0, ((PM10_CAUTION_UG_M3, CAUTION), (PM10_WARNING_UG_M3, WARNING))),
)


def fmt_time(timestamp) -> str:
    """ISO timestamp from the CSV -> 'YYYY-MM-DD HH:MM:SS' (the Pi's local time)."""
    return str(timestamp).replace("T", " ")[:19]


def _status(value: float, tiers) -> str:
    if not tiers:
        return ""
    status = OK
    for above, tier_status in tiers:
        if value > above:
            status = tier_status
    return status


def _rows(latest: pd.Series | None, readings) -> list[dict]:
    rows = []
    for column, label, unit, decimals, tiers in readings:
        value = None if latest is None else latest.get(column)
        if value is None or pd.isna(value):
            rows.append({"Reading": label, "Value": "—", "Status": NO_DATA, "Measured": "—"})
            continue
        rows.append({
            "Reading": label,
            "Value": f"{value:.{decimals}f} {unit}",
            "Status": _status(value, tiers),
            "Measured": fmt_time(latest[TIMESTAMP]),
        })
    return rows


def live_readings(environment: pd.Series | None, particulates: pd.Series | None) -> pd.DataFrame:
    """
    One row per reading from the latest CSV row of each sensor (None if that
    sensor has no data yet), indexed by reading name for display as a table.
    """
    rows = _rows(environment, ENVIRONMENT_READINGS) + _rows(particulates, PARTICULATE_READINGS)
    return pd.DataFrame(rows).set_index("Reading")
