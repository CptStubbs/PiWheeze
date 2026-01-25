import csv
import os
import time
from co2_sensor.co2_module import Co2Sensor
from constants import CO2_PPM, DATA_FILE, FIELDNAMES, HUMIDITY, LOG_INTERVAL_SECONDS, MAX_LINES, TEMPERATURE, TIMESTAMP
from collections import deque
from io import StringIO

history = deque()
config = {
    "refresh_interval_seconds": 1
}
sensor = None
latest_row = None

def get_sensor() -> Co2Sensor:
    """
    Set up the CO2 sensor to be global for the app
    """
    global sensor
    if sensor is None:
        sensor = Co2Sensor()
    return sensor


def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def append_row_rolling(row: dict):
    """
    Append a row to CSV and ensure the file never exceeds MAX_LINES.
    Pops the oldest line if needed.
    """
    init_csv()

    # Read current lines including header
    with open(DATA_FILE, "r", newline="") as f:
        lines = f.readlines()

    # Append new row as CSV string
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
    writer.writerow(row)
    new_line = output.getvalue()

    # Add new line to lines
    lines.append(new_line)

    # Pop oldest lines if exceeding MAX_LINES + header
    if len(lines) > MAX_LINES + 1:  # +1 for header
        lines = [lines[0]] + lines[-MAX_LINES:]

    # Rewrite CSV
    with open(DATA_FILE, "w", newline="") as f:
        f.writelines(lines)

def write_sensor_data_to_file() -> None:
    """
    Main loop of app. Writes to file
    """
    co2_sensor = get_sensor()
    init_csv()

    print("Starting sensor logging loop")

    while True:
        # Get latest value
        reading = co2_sensor.get_data()
        # Write and prune CSV
        append_row_rolling(reading)
        time.sleep(LOG_INTERVAL_SECONDS)


def read_full_history() -> list[dict]:
    """
    Read the full CSV file for all sensor history
    """
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(DATA_FILE)

    history_rows = []

    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            history_rows.append({
                TIMESTAMP: row[TIMESTAMP],
                CO2_PPM: float(row[CO2_PPM]),
                TEMPERATURE: float(row[TEMPERATURE]),
                HUMIDITY: float(row[HUMIDITY]),
            })

    return history_rows


def main():
    print("*"*50)
    print("Made by CptStubbs")
    print("Welcome to the CO2 Sensor App! \n")
    print("Running default terminal mode")
    print("Press Ctrl+C to exit")
    print("*" * 50)

    # Run main loop
    write_sensor_data_to_file()

if __name__ == "__main__":
    main()