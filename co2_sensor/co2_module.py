import time
from board import SCL, SDA
from busio import I2C
from adafruit_scd30 import SCD30
from constants import (CO2_PPM,
                       ERROR,
                       HUMIDITY,
                       REFERENCE_LEVEL_CO2_PPM,
                       SAMPLING_INTERVAL_SECONDS,
                       STATUS,
                       TEMPERATURE, TIMESTAMP,
                       WAIT_INTERVAL_SECONDS)
from datetime import datetime



class Co2Sensor:
    def __init__(self):
        self.last_good_data = None
        self.available = False
        try:
            self.i2c = I2C(SCL, SDA)
            self.scd = SCD30(self.i2c)
            self.scd.measurement_interval = SAMPLING_INTERVAL_SECONDS
            self.available = True
        except Exception as e:
            self.error = str(e)
            self.scd = None
            self.i2c = None

    def calibrate_sensor(self):
        """
        Run the calibration routine for the sensor.

        Assumes that sensor is in stable, outside level air
        """

        self.scd.forced_recalibration_reference = REFERENCE_LEVEL_CO2_PPM

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
            if not self.scd.data_available:
                return self.last_good_data or {STATUS: "warming_up"}


            data = {
                CO2_PPM: self.scd.CO2,
                TEMPERATURE: self.scd.temperature,
                HUMIDITY: self.scd.relative_humidity,
                TIMESTAMP: datetime.now().astimezone().isoformat(timespec="seconds")
            }

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
        while not self.scd.data_available:
            time.sleep(WAIT_INTERVAL_SECONDS)

        while True:
            self.get_data()
            print(f"CO2: {self.scd.CO2:.1f} ppm")
            print(f"Temperature: {self.scd.temperature:.1f} °C")
            print(f"Humidity: {self.scd.relative_humidity:.1f} %")
            print("-" * 30)

if __name__ == "__main__":
    co2_sensor = Co2Sensor()
    co2_sensor.simple_terminal_mode()
