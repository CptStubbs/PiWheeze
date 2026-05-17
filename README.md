# PiWheeze
At home CO2 / Temp / Humidity monitoring, connected to Apple Home

## This Project
This project assumes a few things:
1. A Raspberry Pi 3B+ (or newer)
2. An SCD30 CO2 + Temp + Humidity sensor connected over I2C
3. Docker + Docker Compose installed on the Pi
4. The `i2c` group exists on the Pi (default on Raspberry Pi OS); the `app`
   user inside the containers joins it to read `/dev/i2c-1`

## Services
Four containers, all defined in `docker-compose.yml`:

| Service       | Purpose                                         |
| ------------- | ----------------------------------------------- |
| `sensor_data` | Reads the SCD30 over I2C, appends to CSV        |
| `dashboard`   | Streamlit live charts, internal only            |
| `proxy`       | Caddy reverse proxy in front of the dashboard, basic auth |
| `homekit`     | HAP-python bridge — exposes sensors to Apple Home |

## First-time setup
Clone the repo onto the Pi.

Generate a bcrypt hash for the dashboard password (run as is, "hash-password" is the name of the subcommand, it will
prompt for actual password):
```
docker run -it --rm caddy:2-alpine caddy hash-password
```

Copy the example env file and paste the hash in:
```
cp .env.example .env
# edit .env, set DASHBOARD_BASIC_AUTH_HASH=<hash from above>
```

## Run
```
docker compose up --build -d
```

Check logs: `docker compose logs -f`

Stop: `docker compose down`

## Dashboard
Open `http://<pi-ip>:8501/` in any browser on the LAN. Log in with username
`piwheeze` and the password you hashed during setup.

## Apple Home
On first boot the `homekit` service prints an 8-digit pairing PIN in its
logs (`docker compose logs homekit`). Open the iPhone Home app, tap **+** →
**Add Accessory** → **More Options** → enter the PIN. Three tiles appear:
CO2, Temperature, Humidity. Pairing state persists across restarts in the
`homekit-state` volume.

## Data
The rolling CSV lives in the `data-storage` named volume (capped at 7000
rows ≈ 20 hours at the default 10-second interval). To export:
```
docker run --rm -v piwheeze_data-storage:/d alpine cat /d/data.csv > backup.csv
```
