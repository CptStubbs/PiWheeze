import time
import board
import busio
import adafruit_scd30

REFERENCE_LEVEL_CO2_PPM = 425
SAMPLING_INTERVAL_SECONDS = 30

class Co2Sensor:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.scd = adafruit_scd30.SCD30(self.i2c)

    def calibrate_sensor(self):
        """
        Run the calibration routine for the sensor.

        Assumes that sensor is in stable, outside level air
        """

        self.scd.forced_recalibration_reference = REFERENCE_LEVEL_CO2_PPM

    def simple_terminal_mode(self):
        """
        Prints info to terminal
        Mostly used for debugging
        """
        print("Warming up sensor...")
        while not self.scd.data_available:
            time.sleep(SAMPLING_INTERVAL_SECONDS)

        while True:
            print(f"CO2: {self.scd.CO2:.1f} ppm")
            print(f"Temperature: {self.scd.temperature:.1f} °C")
            print(f"Humidity: {self.scd.relative_humidity:.1f} %")
            print("-" * 30)
            time.sleep(SAMPLING_INTERVAL_SECONDS)

if __name__ == "__main__":
    co2_sensor = Co2Sensor()
    co2_sensor.simple_terminal_mode()
