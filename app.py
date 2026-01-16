from co2_sensor.co2_module import Co2Sensor

def main():
    sensor = Co2Sensor()
    print("*"*50)
    print("Made by CptStubbs")
    print("Welcome to the CO2 Sensor App! \n")
    print("Type your selection below \n")
    print("1. Run monitoring in terminal")
    print("2. Run calibration routine. RUN OUTSIDE. DO NOT RUN OFTEN")
    print("*" * 50)
    selection = int(input("Selection: >>> "))

    if selection == 1:
        sensor.simple_terminal_mode()
    elif selection == 2:
        sensor.calibrate_sensor()
    else:
        print("Invalid selection")

if __name__ == "__main__":
    main()