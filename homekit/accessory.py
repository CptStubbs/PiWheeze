import logging

from pyhap.accessory import Accessory, Bridge
from pyhap.const import CATEGORY_SENSOR

from constants import (
    CO2_ABNORMAL_THRESHOLD_PPM,
    CO2_PPM,
    HOMEKIT_BRIDGE_NAME,
    HOMEKIT_MANUFACTURER,
    HOMEKIT_MODEL,
    HOMEKIT_POLL_INTERVAL_SECONDS,
    HUMIDITY,
    TEMPERATURE,
)
from homekit.csv_reader import read_latest_row

logger = logging.getLogger(__name__)


class CO2Accessory(Accessory):
    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_info_service(
            manufacturer=HOMEKIT_MANUFACTURER,
            model=HOMEKIT_MODEL,
            serial_number="piwheeze-co2",
        )
        service = self.add_preload_service(
            "CarbonDioxideSensor",
            chars=["CarbonDioxideLevel"],
        )
        self.char_detected = service.configure_char("CarbonDioxideDetected")
        self.char_level = service.configure_char("CarbonDioxideLevel")

    def update(self, ppm: float) -> None:
        self.char_level.set_value(ppm)
        self.char_detected.set_value(
            1 if ppm >= CO2_ABNORMAL_THRESHOLD_PPM else 0
        )


class TemperatureAccessory(Accessory):
    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_info_service(
            manufacturer=HOMEKIT_MANUFACTURER,
            model=HOMEKIT_MODEL,
            serial_number="piwheeze-temp",
        )
        service = self.add_preload_service("TemperatureSensor")
        self.char_temp = service.configure_char("CurrentTemperature")

    def update(self, celsius: float) -> None:
        self.char_temp.set_value(celsius)


class HumidityAccessory(Accessory):
    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_info_service(
            manufacturer=HOMEKIT_MANUFACTURER,
            model=HOMEKIT_MODEL,
            serial_number="piwheeze-hum",
        )
        service = self.add_preload_service("HumiditySensor")
        self.char_humidity = service.configure_char("CurrentRelativeHumidity")

    def update(self, percent: float) -> None:
        self.char_humidity.set_value(percent)


class PiWheezeBridge(Bridge):
    def __init__(self, driver, display_name: str = HOMEKIT_BRIDGE_NAME):
        super().__init__(driver, display_name)
        self.set_info_service(
            manufacturer=HOMEKIT_MANUFACTURER,
            model=HOMEKIT_MODEL,
            serial_number="piwheeze-bridge",
        )
        self.co2 = CO2Accessory(driver, "PiWheeze CO2")
        self.temperature = TemperatureAccessory(driver, "PiWheeze Temperature")
        self.humidity = HumidityAccessory(driver, "PiWheeze Humidity")
        self.add_accessory(self.co2)
        self.add_accessory(self.temperature)
        self.add_accessory(self.humidity)
        self._warned_missing = False

    @Accessory.run_at_interval(HOMEKIT_POLL_INTERVAL_SECONDS)
    def run(self) -> None:
        try:
            row = read_latest_row()
        except Exception:
            logger.exception("Unexpected error reading sensor data")
            return

        if row is None:
            if not self._warned_missing:
                logger.warning(
                    "Sensor data file unavailable; keeping last known values"
                )
                self._warned_missing = True
            return
        self._warned_missing = False

        co2 = row.get(CO2_PPM)
        temp = row.get(TEMPERATURE)
        hum = row.get(HUMIDITY)

        try:
            if co2 is not None:
                self.co2.update(co2)
            if temp is not None:
                self.temperature.update(temp)
            if hum is not None:
                self.humidity.update(hum)
        except Exception:
            logger.exception("Failed to push sensor values to HomeKit")
