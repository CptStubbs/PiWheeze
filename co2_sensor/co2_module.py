import time
from datetime import datetime

from scd30_i2c import SCD30

from constants import (CO2_PPM,
                       ERROR,
                       HUMIDITY,
                       REFERENCE_LEVEL_CO2_PPM,
                       SAMPLING_INTERVAL_SECONDS,
                       STATUS,
                       TEMPERATURE, TIMESTAMP,
                       WAIT_INTERVAL_SECONDS)


class Co2Sensor:
    def __init__(self):
        self.last_good_data = None
        self.available = False
        self.error = None
        try:
            self.scd = SCD30()
            self.scd.set_measurement_interval(SAMPLING_INTERVAL_SECONDS)
            self.scd.start_periodic_measurement()
            self.available = True
        except Exception as e:
            self.error = repr(e)
            self.scd = None
            print(f"[Co2Sensor] init failed: {self.error}", flush=True)

    def calibrate_sensor(self):
        """
        Run the calibration routine for the sensor.

        Assumes that sensor is in stable, outside level air
        """
        self.scd.force_recalibration(REFERENCE_LEVEL_CO2_PPM)

    def get_data(self) -> dict:
        if not self.available:
            return self.last_good_data or {
                STATUS: "sensor_unavailable",
                ERROR: self.error,
                CO2_PPM: None,
                TEMPERATURE: None,
                HUMIDITY: None,
                TIMESTAMP: datetime.now().astimezone().isoformat(timespec="seconds")
            }

        try:
            if not self.scd.get_data_ready():
                return self.last_good_data or {STATUS: "warming_up"}

            measurement = self.scd.read_measurement()
            if measurement is None:
                return self.last_good_data or {STATUS: "no_measurement"}

            co2, temperature, humidity = measurement

            data = {
                CO2_PPM: co2,
                TEMPERATURE: temperature,
                HUMIDITY: humidity,
                TIMESTAMP: datetime.now().astimezone().isoformat(timespec="seconds")
            }

            # SCD30 datasheet ranges. Out-of-range values come from sensor
            # malfunction or tampering; treat as missing so downstream
            # consumers don't push absurd values into HomeKit / the CSV.
            if not (0 <= data[CO2_PPM] <= 40000):
                data[CO2_PPM] = None
            if not (-40 <= data[TEMPERATURE] <= 85):
                data[TEMPERATURE] = None
            if not (0 <= data[HUMIDITY] <= 100):
                data[HUMIDITY] = None

            self.last_good_data = data
            return data

        except Exception:
            return self.last_good_data or {STATUS: "i2c_error"}

    def simple_terminal_mode(self):
        """
        Prints info to terminal
        Mostly used for debugging
        """
        print("Warming up sensor...")
        while not self.scd.get_data_ready():
            time.sleep(WAIT_INTERVAL_SECONDS)

        while True:
            data = self.get_data()
            print(f"CO2: {data[CO2_PPM]} ppm")
            print(f"Temperature: {data[TEMPERATURE]} °C")
            print(f"Humidity: {data[HUMIDITY]} %")
            print("-" * 30)
            time.sleep(SAMPLING_INTERVAL_SECONDS)


if __name__ == "__main__":
    co2_sensor = Co2Sensor()
    co2_sensor.simple_terminal_mode()
