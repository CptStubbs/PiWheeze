from co2_sensor.co2_module import Co2Sensor

def main():
    sensor = Co2Sensor()
    print("*"*50)
    print("Made by CptStubbs")
    print("Welcome to the CO2 Sensor App! \n")
    print("Running default terminal mode")
    print("Press Ctrl+C to exit")
    print("*" * 50)

    sensor.simple_terminal_mode()

if __name__ == "__main__":
    main()