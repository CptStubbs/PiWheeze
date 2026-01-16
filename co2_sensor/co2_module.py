import time
import board
import busio
import adafruit_scd30

i2c = busio.I2C(board.SCL, board.SDA)
scd = adafruit_scd30.SCD30(i2c)

# Optional: force recalibration to current CO2 level (outdoors ~415 ppm)
# scd.forced_recalibration_reference = 415


def experimental():

    print("Warming up sensor...")
    while not scd.data_available:
        time.sleep(0.5)

    while True:
        print(f"CO2: {scd.CO2:.1f} ppm")
        print(f"Temperature: {scd.temperature:.1f} °C")
        print(f"Humidity: {scd.relative_humidity:.1f} %")
        print("-" * 30)
        time.sleep(2)

if __name__ == "__main__":
    experimental()