import csv
import os
from flask import Flask, jsonify, request, render_template, Response
from co2_sensor.co2_module import Co2Sensor
from constants import APP_PORT, CO2_PPM, DATA_FILE, HUMIDITY, INDEX_HTML, TEMPERATURE, TIMESTAMP
from collections import deque


history = deque()
config = {
    "refresh_interval_seconds": 1
}
app = Flask(__name__)
sensor = None

def get_sensor():
    global sensor
    if sensor is None:
        sensor = Co2Sensor()
    return sensor

def write_to_file(reading:dict[str, float]):
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    file_exists = os.path.isfile(DATA_FILE)

    # open as "append" type
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[TIMESTAMP, CO2_PPM, TEMPERATURE, HUMIDITY],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            TIMESTAMP: reading[TIMESTAMP],
            CO2_PPM: reading[CO2_PPM],
            TEMPERATURE: reading[TEMPERATURE],
            HUMIDITY: reading[HUMIDITY],
        })

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
    write_to_file(reading)
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
    app.run(host="0.0.0.0", port=APP_PORT)

if __name__ == "__main__":
    main()