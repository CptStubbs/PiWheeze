DATA_FILE = "/data_storage/data.csv"
LOG_INTERVAL_SECONDS = 10
LOGGING_WINDOW_HOURS = 72
MAX_LINES = int(LOGGING_WINDOW_HOURS * 3600 / LOG_INTERVAL_SECONDS)

# Sensor Field Names
CO2_PPM = "co2_ppm"
ERROR = "error"
HUMIDITY = "humidity"
STATUS = "status"
TEMPERATURE = "temperature"
TIMESTAMP = "timestamp"
FIELDNAMES = [TIMESTAMP, CO2_PPM, TEMPERATURE, HUMIDITY]

# Particulate sensor (PMSA003I) field names, stored in their own CSV so the CO2
# and particulate sensors fail and recover independently
PM1_0 = "pm1_0"
PM2_5 = "pm2_5"
PM10 = "pm10"
PM_DATA_FILE = "/data_storage/pm_data.csv"
PM_FIELDNAMES = [TIMESTAMP, PM1_0, PM2_5, PM10]

# Sensor Params
S2C_FREQUENCY = 50000
REFERENCE_LEVEL_CO2_PPM = 425
SAMPLING_INTERVAL_SECONDS = 10
WAIT_INTERVAL_SECONDS = 1
READ_FAILURES_BEFORE_RECONNECT = 6  # consecutive failed reads (~1 min) before re-initialising

# PMSA003I (particulate sensor) params
PMSA003I_I2C_ADDRESS = 0x12
PMSA003I_I2C_BUS = 1
PMSA003I_FRAME_LENGTH = 32
PMSA003I_MAX_UG_M3 = 1000  # datasheet range is 0-1000 ug/m3

# HomeKit
HOMEKIT_STATE_DIR = "/homekit_state"
HOMEKIT_STATE_FILE = f"{HOMEKIT_STATE_DIR}/accessory.state"
HOMEKIT_PORT = 51826
HOMEKIT_POLL_INTERVAL_SECONDS = 10
CO2_ABNORMAL_THRESHOLD_PPM = 1000
HOMEKIT_BRIDGE_NAME = "PiWheeze"
HOMEKIT_MANUFACTURER = "CptStubbs"
HOMEKIT_MODEL = "PiWheeze-SCD30"
HOMEKIT_PM_MODEL = "PiWheeze-PMSA003I"
# Upper PM2.5 bounds (ug/m3) for HomeKit AirQuality 1 (Excellent) through 4 (Inferior);
# anything above is 5 (Poor). Based on the US EPA AQI PM2.5 breakpoints.
PM2_5_AIR_QUALITY_BOUNDS = (9.0, 35.4, 55.4, 150.4)