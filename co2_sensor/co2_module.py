import time
from datetime import datetime

from scd30_i2c import SCD30

from constants import (CO2_PPM,
                       ERROR,
                       HUMIDITY,
                       READ_FAILURES_BEFORE_RECONNECT,
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
        self.scd = None
        self._read_failures = 0
        self._last_logged_error = None
        self._connect()

    def _log_error(self, message: str) -> None:
        """Print an error, but only when it differs from the last one printed.

        get_data() runs every few seconds, so a sensor that stays broken would
        otherwise flood the logs with the same line.
        """
        if message != self._last_logged_error:
            print(f"[Co2Sensor] {message}", flush=True)
            self._last_logged_error = message

    def _connect(self) -> None:
        """
        Start periodic measurement and set self.available / self.error.

        Safe to call repeatedly: the I2C bus is opened once and reused, so a
        retry only re-sends the setup commands. Called from __init__ and again
        from get_data() whenever the sensor is unavailable, so a sensor that
        wasn't ready at boot recovers on its own.
        """
        try:
            if self.scd is None:
                self.scd = SCD30()
            self.scd.set_measurement_interval(SAMPLING_INTERVAL_SECONDS)
            self.scd.start_periodic_measurement()
        except Exception as e:
            self.available = False
            self.error = repr(e)
            self._log_error(f"init failed: {self.error}")
            self._try_soft_reset()
            return

        self.available = True
        self.error = None
        if self._last_logged_error is not None:
            print("[Co2Sensor] sensor connected", flush=True)
            self._last_logged_error = None

    def _try_soft_reset(self) -> None:
        """
        Best-effort sensor restart (no power cycle needed) after a failed setup.

        A Pi reboot doesn't cut power to the SCD30, so it can come back up stuck
        in a state where it ignores commands. The next _connect() attempt then
        finds it freshly reset.
        """
        if self.scd is None:
            return
        try:
            self.scd.soft_reset()
        except Exception:
            pass  # sensor isn't answering at all; try again next round

    def calibrate_sensor(self):
        """
        Run the calibration routine for the sensor.

        Assumes that sensor is in stable, outside level air
        """
        self.scd.force_recalibration(REFERENCE_LEVEL_CO2_PPM)

    def get_data(self) -> dict:
        if not self.available:
            self._connect()

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
            self._read_failures = 0
            self._last_logged_error = None
            return data

        except Exception as e:
            self._log_error(f"read failed: {e!r}")
            self._read_failures += 1
            if self._read_failures >= READ_FAILURES_BEFORE_RECONNECT:
                # Sensor has stopped answering; the next get_data() call
                # re-initialises it instead of failing forever.
                self._read_failures = 0
                self.available = False
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
