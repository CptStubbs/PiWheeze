import os
import json
from flask import Flask, jsonify, request, render_template
from co2_sensor.co2_module import Co2Sensor
from collections import deque


HISTORY_HOURS = 24
history = deque()

config = {
    "refresh_interval_seconds": 1
}
APP_PORT = 5000
DATA_FILE = os.path.join("data_storage", "data.csv")
app = Flask(__name__)
INDEX_HTML = "index.html"
sensor = None

app = Flask(__name__)

def get_sensor():
    global sensor
    if sensor is None:
        sensor = Co2Sensor()
    return sensor

@app.route("/")
def index():
    return render_template(
        INDEX_HTML,
        interval=config["refresh_interval_seconds"]
    )

@app.route("/data")
def data():
    # Get current value
    reading = get_sensor().get_data()
    # Write value to file for history
    with open(DATA_FILE, "w") as f:
        f.write(json.dumps(reading))
    return jsonify(reading)

@app.route("/config", methods=["POST"])
def update_config():
    config.update(request.json)
    return jsonify(config)

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