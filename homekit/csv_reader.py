import csv
import logging
from typing import Optional

from constants import CO2_PPM, DATA_FILE, HUMIDITY, TEMPERATURE, TIMESTAMP

logger = logging.getLogger(__name__)


def read_latest_row() -> Optional[dict]:
    """
    Return the most recent sensor row from DATA_FILE, or None if the file
    is missing, empty, or unreadable. Values for CO2_PPM, TEMPERATURE,
    HUMIDITY are coerced to float; non-numeric values become None.
    """
    try:
        with open(DATA_FILE, newline="") as f:
            reader = csv.DictReader(f)
            last = None
            for row in reader:
                last = row
    except FileNotFoundError:
        return None
    except OSError as e:
        logger.warning("Could not read %s: %s", DATA_FILE, e)
        return None

    if last is None:
        return None

    return {
        TIMESTAMP: last.get(TIMESTAMP),
        CO2_PPM: _to_float(last.get(CO2_PPM)),
        TEMPERATURE: _to_float(last.get(TEMPERATURE)),
        HUMIDITY: _to_float(last.get(HUMIDITY)),
    }


def _to_float(value) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
