import csv
import os
import time
import threading
from flask import Flask, jsonify, request, render_template, Response
from co2_sensor.co2_module import Co2Sensor
from constants import APP_PORT, CO2_PPM, DATA_FILE, HUMIDITY, INDEX_HTML, LOG_INTERVAL_SECONDS, TEMPERATURE, TIMESTAMP
from collections import deque

history = deque()
config = {
    "refresh_interval_seconds": 1
}
app = Flask(__name__)
sensor = None

def get_sensor() -> Co2Sensor:
    """
    Set up the CO2 sensor to be global for the app
    """
    global sensor
    if sensor is None:
        sensor = Co2Sensor()
    return sensor

def init_csv() -> None:
    """ Initialize the CSV file """
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                TIMESTAMP,
                CO2_PPM,
                TEMPERATURE,
                HUMIDITY
            ])

def write_sensor_data_to_file() -> None:
    """
    Main loop of app. Writes to file
    """
    co2_sensor = get_sensor()
    init_csv()

    print("Starting sensor logging loop")

    while True:
        try:
            reading = co2_sensor.get_data()

            # Open file as type append
            with open(DATA_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    reading[TIMESTAMP],
                    reading[CO2_PPM],
                    reading[TEMPERATURE],
                    reading[HUMIDITY]
                ])

            print(f"Debug! Timestamp> {reading[TIMESTAMP]}")

        except Exception as e:
            # Do NOT crash the loop on sensor hiccups
            print("Sensor read error:", e)

        time.sleep(LOG_INTERVAL_SECONDS)

@app.route("/")
def index() -> str:
    return render_template(
        INDEX_HTML,
        interval=config["refresh_interval_seconds"]
    )

@app.route("/data")
def data() -> Response:
    # Get current value
    reading = get_sensor().get_data()
    # Write value to file for history
    #write_to_file(reading)
    return jsonify(reading)

@app.route("/config", methods=["POST"])
def update_config() -> Response:
    config.update(request.json)
    return jsonify(config)

@app.route("/history")
def history():
    if not os.path.exists(DATA_FILE):
        return jsonify([])

    rows = []

    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                TIMESTAMP: row[TIMESTAMP],
                CO2_PPM: float(row[CO2_PPM]),
                TEMPERATURE: float(row[TEMPERATURE]),
                HUMIDITY: float(row[HUMIDITY])
            })

    return jsonify(rows)

def main():
    print("*"*50)
    print("Made by CptStubbs")
    print("Welcome to the CO2 Sensor App! \n")
    print("Running default terminal mode")
    print("Press Ctrl+C to exit")
    print("*" * 50)

    # Run main loop
    t = threading.Thread(target=write_sensor_data_to_file(), daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=APP_PORT)

if __name__ == "__main__":
    main()