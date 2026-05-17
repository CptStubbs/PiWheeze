import logging
import os
import signal

from pyhap.accessory_driver import AccessoryDriver

from constants import HOMEKIT_PORT, HOMEKIT_STATE_DIR, HOMEKIT_STATE_FILE
from homekit.accessory import PiWheezeBridge


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    os.makedirs(HOMEKIT_STATE_DIR, exist_ok=True)

    driver = AccessoryDriver(
        port=HOMEKIT_PORT,
        persist_file=HOMEKIT_STATE_FILE,
    )
    driver.add_accessory(accessory=PiWheezeBridge(driver))

    signal.signal(signal.SIGTERM, driver.signal_handler)
    signal.signal(signal.SIGINT, driver.signal_handler)

    logger.info("Starting HomeKit bridge on port %d", HOMEKIT_PORT)
    driver.start()


if __name__ == "__main__":
    main()
