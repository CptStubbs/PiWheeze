# PiWheeze
At home CO2 / Temp / Humidity / particulate monitoring, connected to Apple Home

## This Project
This project assumes a few things:
1. A Raspberry Pi 3B+ (or newer)
2. An SCD30 CO2 + Temp + Humidity sensor connected over I2C
3. An optional Adafruit PMSA003I particulate sensor on the same I2C bus (address `0x12`)
4. Docker + Docker Compose installed on the Pi
5. The `i2c` group exists on the Pi (default on Raspberry Pi OS); the `app`
   user inside the containers joins it to read `/dev/i2c-1`

## Services
Five containers, all defined in `docker-compose.yml`:

| Service       | Purpose                                         |
| ------------- | ----------------------------------------------- |
| `sensor_data` | Reads the SCD30 over I2C, appends to CSV        |
| `pm_sensor_data` | Reads the PMSA003I (PM1.0 / PM2.5 / PM10) over I2C, appends to its own CSV |
| `dashboard`   | Streamlit live charts + login, internal only    |
| `proxy`       | Caddy reverse proxy in front of the dashboard   |
| `homekit`     | HAP-python bridge — exposes sensors to Apple Home |

## First-time setup
Clone the repo onto the Pi.

Generate a bcrypt hash for the dashboard password (run as is, "hash-password" is the name of the subcommand, it will
prompt for actual password):
```
docker run -it --rm caddy:2-alpine caddy hash-password
```

Generate a random secret key for signing the "stay logged in" cookie:
```
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the example env file and fill in both values:
```
cp .env.example .env
# edit .env, set DASHBOARD_PASSWORD_HASH=<hash from above>
# edit .env, set DASHBOARD_COOKIE_KEY=<secret from above>
```

## Run
```
docker compose up --build -d
```

Check logs: `docker compose logs -f`

Stop: `docker compose down`

## Dashboard
Open `http://<pi-ip>:8501/` in any browser on the LAN. Log in with username
`piwheeze` and the password you hashed during setup. A "stay logged in"
cookie keeps you signed in for a year, including on iOS "Add to Home
Screen" shortcuts, so you shouldn't need to log in again after the first
time. Use the "Log out" button in the sidebar to end the session early.

### Previewing chart changes
Charts are built in `charts.py` and can be previewed from mock data without
the sensors, Docker or a login:
```
pip install -r requirements-dev.in
python -m tests.preview     # writes previews/*.html (good air, warnings, spikes + gaps) and opens them
python -m pytest            # checks y-ranges, warning bands and colours too
```

## Apple Home
On first boot the `homekit` service prints an 8-digit pairing PIN in its
logs (`docker compose logs homekit`). Open the iPhone Home app, tap **+** →
**Add Accessory** → **More Options** → enter the PIN. Four tiles appear:
CO2, Temperature, Humidity, Air Quality (PM2.5 / PM10 density plus an
Excellent-to-Poor rating based on PM2.5). If you paired before the PMSA003I
was added, the Air Quality tile appears on its own after a restart. Pairing state persists across restarts in the
`homekit-state` volume.

## Data
The rolling CSVs (`data.csv` and `pm_data.csv`) live in the `data-storage` named volume (capped at 72
hours of history at the default 10-second interval). To export:
```
docker run --rm -v piwheeze_data-storage:/d alpine cat /d/data.csv > backup.csv
```
