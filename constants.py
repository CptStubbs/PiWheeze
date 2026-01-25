import os


APP_PORT = 5000
DATA_FILE = os.path.join("data_storage", "data.csv")
INDEX_HTML = "index.html"
HISTORY_HOURS = 24
LOG_INTERVAL_SECONDS = 10

# Sensor Field Names
CO2_PPM = "co2_ppm"
ERROR = "error"
HUMIDITY = "humidity"
STATUS = "status"
TEMPERATURE = "temperature"
TIMESTAMP = "timestamp"

# Sensor Params
S2C_FREQUENCY = 50000
REFERENCE_LEVEL_CO2_PPM = 425
SAMPLING_INTERVAL_SECONDS = 10
WAIT_INTERVAL_SECONDS = 1