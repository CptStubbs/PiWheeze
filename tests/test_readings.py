import numpy as np
import pandas as pd

from constants import CO2_PPM, HUMIDITY, PM1_0, PM2_5, PM10, TEMPERATURE, TIMESTAMP
from readings import CAUTION, NO_DATA, OK, WARNING, fmt_time, live_readings

TIME = "2026-11-02T17:15:56-08:00"


def row(**values) -> pd.Series:
    base = {TIMESTAMP: TIME, CO2_PPM: 600, TEMPERATURE: 21.0, HUMIDITY: 50,
            PM1_0: 2, PM2_5: 4, PM10: 6}
    return pd.Series({**base, **values})


def table(**values) -> pd.DataFrame:
    latest = row(**values)
    return live_readings(latest, latest)


def test_one_row_per_reading_in_order():
    assert list(table().index) == ["CO₂", "Temperature", "Humidity", "PM1.0", "PM2.5", "PM10"]


def test_values_carry_units_and_measured_time():
    t = table(**{CO2_PPM: 812.4, TEMPERATURE: 21.26})
    assert t.loc["CO₂", "Value"] == "812 ppm"
    assert t.loc["Temperature", "Value"] == "21.3 °C"
    assert t.loc["PM2.5", "Value"] == "4 µg/m³"
    assert (t["Measured"] == "2026-11-02 17:15:56").all()


def test_good_air_is_all_ok():
    t = table()
    assert t.loc[["CO₂", "Temperature", "Humidity", "PM2.5", "PM10"], "Status"].eq(OK).all()


def test_pm1_0_has_no_status():
    assert table(**{PM1_0: 500}).loc["PM1.0", "Status"] == ""


def test_status_flips_only_above_the_threshold():
    assert table(**{CO2_PPM: 1000}).loc["CO₂", "Status"] == OK
    assert table(**{CO2_PPM: 1001}).loc["CO₂", "Status"] == WARNING
    assert table(**{TEMPERATURE: 25.1}).loc["Temperature", "Status"] == WARNING
    assert table(**{HUMIDITY: 86}).loc["Humidity", "Status"] == WARNING


def test_pm_has_a_caution_tier_before_the_warning_tier():
    assert table(**{PM2_5: 16}).loc["PM2.5", "Status"] == CAUTION
    assert table(**{PM2_5: 36}).loc["PM2.5", "Status"] == WARNING
    assert table(**{PM10: 46}).loc["PM10", "Status"] == CAUTION
    assert table(**{PM10: 155}).loc["PM10", "Status"] == WARNING


def test_missing_sensor_shows_no_data():
    t = live_readings(row(), None)
    assert t.loc[["PM1.0", "PM2.5", "PM10"], "Status"].eq(NO_DATA).all()
    assert t.loc["PM2.5", "Value"] == "—"
    assert t.loc["CO₂", "Status"] == OK


def test_blank_value_shows_no_data():
    assert table(**{CO2_PPM: np.nan}).loc["CO₂", "Status"] == NO_DATA


def test_fmt_time():
    assert fmt_time(TIME) == "2026-11-02 17:15:56"
