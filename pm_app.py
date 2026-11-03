import time

from app import append_row_rolling, init_csv
from constants import LOG_INTERVAL_SECONDS, PM_DATA_FILE, PM_FIELDNAMES
from pm_sensor.pm_module import PmSensor


def write_pm_data_to_file() -> None:
    """
    Main loop of the particulate sensor. Writes to its own rolling CSV.
    """
    pm_sensor = PmSensor()
    init_csv(PM_DATA_FILE, PM_FIELDNAMES)

    print("Starting particulate logging loop")

    while True:
        reading = pm_sensor.get_data()
        append_row_rolling(reading, PM_DATA_FILE, PM_FIELDNAMES)
        time.sleep(LOG_INTERVAL_SECONDS)


def main():
    print("Running PMSA003I particulate logger")
    print("Press Ctrl+C to exit")
    write_pm_data_to_file()


if __name__ == "__main__":
    main()
