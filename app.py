import csv
import os
import time
import threading
from flask import Flask, jsonify, request, render_template, Response
from co2_sensor.co2_module import Co2Sensor
from constants import APP_PORT, CO2_PPM, DATA_FILE, HUMIDITY, INDEX_HTML, LOG_INTERVAL_SECONDS,RETENTION_DAYS, TEMPERATURE, TIMESTAMP
from collections import deque
from datetime import datetime, timedelta

history = deque()
config = {
    "refresh_interval_seconds": 1
}
app = Flask(__name__)
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

def prune_csv() -> None:
    """
    Delete old values in the CSV file
    """
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(DATA_FILE)

    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    kept_rows = []

    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            print(f"!! DEBUG !! {row}")
            ts = datetime.fromisoformat(row["timestamp"])
            if ts >= cutoff:
                kept_rows.append(row)

    # Rewrite file with kept rows
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)

def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[TIMESTAMP, CO2_PPM, TEMPERATURE, HUMIDITY])
            writer.writeheader()

def append_row(row):
    global latest_row
    latest_row = row
    with open(DATA_FILE, "a", newline="") as f:
        fieldnames = [TIMESTAMP, CO2_PPM, TEMPERATURE, HUMIDITY]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({
            TIMESTAMP: row["timestamp"],
            CO2_PPM: row["co2_ppm"],
            TEMPERATURE: row["temperature"],
            HUMIDITY: row["humidity"],
        })

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
        append_row(reading)
        prune_csv()

        time.sleep(LOG_INTERVAL_SECONDS)


def read_full_history() -> list[dict]:
    """
    Read the full CSV file for all sensor history
    """
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(DATA_FILE)

    rows = []

    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                TIMESTAMP: row[TIMESTAMP],
                CO2_PPM: float(row[CO2_PPM]),
                TEMPERATURE: float(row[TEMPERATURE]),
                HUMIDITY: float(row[HUMIDITY]),
            })

    return rows


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/current")
def current():
    return jsonify(latest_row)

@app.route("/data")
def data() -> Response:
    # Get current value
    reading = get_sensor().get_data()
    # Write value to file for history
    return jsonify(reading)

@app.route("/config", methods=["POST"])
def update_config() -> Response:
    config.update(request.json)
    return jsonify(config)

@app.route("/history")
def history():
    return jsonify(read_full_history())

def main():
    print("*"*50)
    print("Made by CptStubbs")
    print("Welcome to the CO2 Sensor App! \n")
    print("Running default terminal mode")
    print("Press Ctrl+C to exit")
    print("*" * 50)

    # Run main loop
    t = threading.Thread(target=write_sensor_data_to_file, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=APP_PORT)

if __name__ == "__main__":
    main()