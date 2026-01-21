import os
from flask import Flask, jsonify, request, render_template
from co2_sensor.co2_module import Co2Sensor

import os

config = {
    "refresh_interval_seconds": 1
}
APP_PORT = 5000
TEMPLATE_INDEX_PATH = os.path.join(os.path.dirname(__file__), "templates/index.html")
sensor = Co2Sensor()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template(
        TEMPLATE_INDEX_PATH,
        interval=config["refresh_interval_seconds"]
    )

@app.route("/data")
def data():
    return jsonify(sensor.get_data())

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