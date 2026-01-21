import time
from board import SCL, SDA
from busio import I2C
from adafruit_scd30 import SCD30
from datetime import datetime

S2C_FREQUENCY = 50000
REFERENCE_LEVEL_CO2_PPM = 425
SAMPLING_INTERVAL_SECONDS = 10
WAIT_INTERVAL_SECONDS = 1

class Co2Sensor:
    def __init__(self):
        self.i2c = I2C(SCL, SDA, frequency=S2C_FREQUENCY)
        self.scd = SCD30(self.i2c)
        self.scd.measurement_interval = SAMPLING_INTERVAL_SECONDS

    def calibrate_sensor(self):
        """
        Run the calibration routine for the sensor.

        Assumes that sensor is in stable, outside level air
        """

        self.scd.forced_recalibration_reference = REFERENCE_LEVEL_CO2_PPM


    def get_data(self) -> dict:
        """
        Get data from sensor or wait
        :return: dict of data
        """
        while not self.scd.data_available:
            time.sleep(WAIT_INTERVAL_SECONDS)

        data = {
            "co2_ppm": self.scd.CO2,
            "temperature": self.scd.temperature,
            "humidity": self.scd.relative_humidity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data

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
