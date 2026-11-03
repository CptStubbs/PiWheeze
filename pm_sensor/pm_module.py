import time
from datetime import datetime

from smbus2 import SMBus, i2c_msg

from constants import (ERROR,
                       PM1_0,
                       PM2_5,
                       PM10,
                       PMSA003I_FRAME_LENGTH,
                       PMSA003I_I2C_ADDRESS,
                       PMSA003I_I2C_BUS,
                       PMSA003I_MAX_UG_M3,
                       READ_FAILURES_BEFORE_RECONNECT,
                       SAMPLING_INTERVAL_SECONDS,
                       STATUS,
                       TIMESTAMP)


class PmSensor:
    """
    Reader for the Adafruit PMSA003I particulate sensor over I2C.

    Mirrors Co2Sensor: get_data() never raises, and a sensor that is missing
    or stops answering is retried on later calls rather than failing forever.
    """

    def __init__(self):
        self.last_good_data = None
        self.available = False
        self.error = None
        self.bus = None
        self._read_failures = 0
        self._last_logged_error = None
        self._connect()

    def _log_error(self, message: str) -> None:
        """Print an error, but only when it differs from the last one printed."""
        if message != self._last_logged_error:
            print(f"[PmSensor] {message}", flush=True)
            self._last_logged_error = message

    def _connect(self) -> None:
        """
        Open the I2C bus and check the sensor answers. Safe to call repeatedly;
        called from __init__ and again from get_data() while unavailable.
        """
        try:
            if self.bus is None:
                self.bus = SMBus(PMSA003I_I2C_BUS)
            self._read_frame()
        except Exception as e:
            self.available = False
            self.error = repr(e)
            self._log_error(f"init failed: {self.error}")
            return

        self.available = True
        self.error = None
        if self._last_logged_error is not None:
            print("[PmSensor] sensor connected", flush=True)
            self._last_logged_error = None

    def _read_frame(self) -> bytes:
        """Read and validate one 32-byte frame, returning the raw bytes."""
        read = i2c_msg.read(PMSA003I_I2C_ADDRESS, PMSA003I_FRAME_LENGTH)
        self.bus.i2c_rdwr(read)
        frame = bytes(read)

        if frame[0:2] != b"BM":
            raise ValueError("bad frame header")
        if sum(frame[:-2]) != int.from_bytes(frame[-2:], "big"):
            raise ValueError("frame checksum mismatch")
        return frame

    def get_data(self) -> dict:
        if not self.available:
            self._connect()

        if not self.available:
            return self.last_good_data or {
                STATUS: "sensor_unavailable",
                ERROR: self.error,
                PM1_0: None,
                PM2_5: None,
                PM10: None,
                TIMESTAMP: datetime.now().astimezone().isoformat(timespec="seconds")
            }

        try:
            frame = self._read_frame()

            # Words 3-5 (bytes 10-15) are the atmospheric-environment
            # concentrations in ug/m3, as opposed to the factory "standard
            # particle" values in words 0-2.
            pm1_0, pm2_5, pm10 = (
                int.from_bytes(frame[i:i + 2], "big") for i in (10, 12, 14)
            )

            data = {
                PM1_0: pm1_0,
                PM2_5: pm2_5,
                PM10: pm10,
                TIMESTAMP: datetime.now().astimezone().isoformat(timespec="seconds")
            }

            # Out-of-range values mean a malfunction; treat as missing so
            # they don't reach HomeKit / the CSV.
            for key in (PM1_0, PM2_5, PM10):
                if not (0 <= data[key] <= PMSA003I_MAX_UG_M3):
                    data[key] = None

            self.last_good_data = data
            self._read_failures = 0
            self._last_logged_error = None
            return data

        except Exception as e:
            self._log_error(f"read failed: {e!r}")
            self._read_failures += 1
            if self._read_failures >= READ_FAILURES_BEFORE_RECONNECT:
                self._read_failures = 0
                self.available = False
            return self.last_good_data or {STATUS: "i2c_error"}

    def simple_terminal_mode(self):
        """
        Prints info to terminal
        Mostly used for debugging
        """
        while True:
            data = self.get_data()
            print(f"PM1.0: {data.get(PM1_0)} ug/m3")
            print(f"PM2.5: {data.get(PM2_5)} ug/m3")
            print(f"PM10: {data.get(PM10)} ug/m3")
            print("-" * 30)
            time.sleep(SAMPLING_INTERVAL_SECONDS)


if __name__ == "__main__":
    pm_sensor = PmSensor()
    pm_sensor.simple_terminal_mode()
