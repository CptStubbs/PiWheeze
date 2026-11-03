import csv
import logging
from typing import Optional

from constants import (CO2_PPM, DATA_FILE, HUMIDITY, PM1_0, PM2_5, PM10, PM_DATA_FILE,
                       TEMPERATURE, TIMESTAMP)

logger = logging.getLogger(__name__)


def _read_last_row(data_file: str) -> Optional[dict]:
    """Return the last CSV row of data_file as raw strings, or None."""
    try:
        with open(data_file, newline="") as f:
            reader = csv.DictReader(f)
            last = None
            for row in reader:
                last = row
    except FileNotFoundError:
        return None
    except OSError as e:
        logger.warning("Could not read %s: %s", data_file, e)
        return None

    return last


def read_latest_row() -> Optional[dict]:
    """
    Return the most recent sensor row from DATA_FILE, or None if the file
    is missing, empty, or unreadable. Values for CO2_PPM, TEMPERATURE,
    HUMIDITY are coerced to float; non-numeric values become None.
    """
    last = _read_last_row(DATA_FILE)
    if last is None:
        return None

    return {
        TIMESTAMP: last.get(TIMESTAMP),
        CO2_PPM: _to_float(last.get(CO2_PPM)),
        TEMPERATURE: _to_float(last.get(TEMPERATURE)),
        HUMIDITY: _to_float(last.get(HUMIDITY)),
    }


def read_latest_pm_row() -> Optional[dict]:
    """
    Same as read_latest_row() but for the particulate sensor's PM_DATA_FILE;
    PM1_0, PM2_5, PM10 are coerced to float.
    """
    last = _read_last_row(PM_DATA_FILE)
    if last is None:
        return None

    return {
        TIMESTAMP: last.get(TIMESTAMP),
        PM1_0: _to_float(last.get(PM1_0)),
        PM2_5: _to_float(last.get(PM2_5)),
        PM10: _to_float(last.get(PM10)),
    }


def _to_float(value) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
