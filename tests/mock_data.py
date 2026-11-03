"""Synthetic sensor history for previewing and testing the dashboard charts."""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from constants import CO2_PPM, HUMIDITY, PM1_0, PM2_5, PM10, TEMPERATURE, TIMESTAMP

POINTS = 864  # 72h at one point every 5 minutes; the real CSV is denser but looks the same
STEP = timedelta(minutes=5)


def _timestamps() -> list[str]:
    start = datetime(2026, 11, 2, 0, 0).astimezone() - STEP * POINTS
    return [(start + STEP * i).isoformat(timespec="seconds") for i in range(POINTS)]


def _frame(co2, temperature, humidity, pm1_0, pm2_5, pm10) -> pd.DataFrame:
    return pd.DataFrame({
        TIMESTAMP: _timestamps(),
        CO2_PPM: co2,
        TEMPERATURE: temperature,
        HUMIDITY: humidity,
        PM1_0: pm1_0,
        PM2_5: pm2_5,
        PM10: pm10,
    })


def _daily(low: float, high: float, noise: float, rng) -> np.ndarray:
    """A day/night wave between low and high with some noise on top."""
    t = np.arange(POINTS)
    wave = (np.sin(2 * np.pi * t / (24 * 12) - np.pi / 2) + 1) / 2
    return low + (high - low) * wave + rng.normal(0, noise, POINTS)


def good_air() -> pd.DataFrame:
    """Everything comfortably inside its good range."""
    rng = np.random.default_rng(1)
    pm2_5 = np.clip(_daily(3, 8, 0.6, rng), 0, None)
    return _frame(
        co2=_daily(450, 750, 15, rng),
        temperature=_daily(19, 23, 0.1, rng),
        humidity=_daily(40, 55, 0.5, rng),
        pm1_0=pm2_5 * 0.6,
        pm2_5=pm2_5,
        pm10=pm2_5 * 1.4,
    )


def warnings() -> pd.DataFrame:
    """Every quantity climbs through its warning bands by the end."""
    rng = np.random.default_rng(2)
    ramp = np.linspace(0, 1, POINTS)
    pm2_5 = 4 + ramp ** 2 * 60 + rng.normal(0, 1, POINTS)
    return _frame(
        co2=450 + ramp * 1000 + rng.normal(0, 20, POINTS),     # ends ~1450, past the 1200 axis top
        temperature=19 + ramp * 9 + rng.normal(0, 0.1, POINTS),
        humidity=45 + ramp * 50 + rng.normal(0, 0.5, POINTS),
        pm1_0=pm2_5 * 0.6,
        pm2_5=pm2_5,
        pm10=pm2_5 * 2.5,
    )


def spikes_and_gaps() -> pd.DataFrame:
    """Good air with short PM spikes (cooking) and stretches of missing data."""
    df = good_air()
    for centre in (200, 520, 700):
        bump = 40 * np.exp(-((np.arange(POINTS) - centre) / 6.0) ** 2)
        df[PM2_5] += bump
        df[PM1_0] += bump * 0.8
        df[PM10] += bump * 1.3
    # Sensor-down rows are written as blank cells, which read back as NaN
    for start, end in ((300, 330), (610, 625)):
        df.loc[start:end, [CO2_PPM, TEMPERATURE, HUMIDITY, PM1_0, PM2_5, PM10]] = np.nan
    return df


SCENARIOS = {
    "good_air": good_air,
    "warnings": warnings,
    "spikes_and_gaps": spikes_and_gaps,
}
