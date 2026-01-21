import time
from board import SCL, SDA
from busio import I2C
from adafruit_scd30 import SCD30

REFERENCE_LEVEL_CO2_PPM = 425
SAMPLING_INTERVAL_SECONDS = 10
WAIT_INTERVAL_SECONDS = 1

class Co2Sensor:
    def __init__(self):
        self.i2c = I2C(SCL, SDA)
        self.scd = SCD30(self.i2c)
        self.scd.measurement_interval = SAMPLING_INTERVAL_SECONDS

    def calibrate_sensor(self):
        """
        Run the calibration routine for the sensor.

        Assumes that sensor is in stable, outside level air
        """

        self.scd.forced_recalibration_reference = REFERENCE_LEVEL_CO2_PPM


    def get_data(self) -> None:
        """
        Get data from sensor or wait
        """
        while True:
            if self.scd.data_available:
                return
            else:
                time.sleep(WAIT_INTERVAL_SECONDS)

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
