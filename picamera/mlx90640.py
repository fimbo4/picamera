import serial

class Thermal:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.sensor = serial.Serial(port=port, baudrate=baud, timeout=3)

    def get_thermal_frame(self):
        return self.sensor.readline().decode('utf-8')

# mythermal = Thermal('/dev/ttyUSB2', 115200)
# print(mythermal.get_thermal_frame())