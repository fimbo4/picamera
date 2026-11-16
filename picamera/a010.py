import serial
import time

class Lidar:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.header = bytes([0x00, 0xff])
        self.sensor = serial.Serial(port=port, baudrate=baud, timeout=0.1, write_timeout=1.0)
        self.buffer = bytearray()

    def start(self):
        self.sensor.write(b'AT+DISP=3\r')
        time.sleep(0.2)
        self.sensor.write(b'AT+FPS=10\r')
        time.sleep(0.2)

    def get_lidar_frame(self):
        while True:

            waiting = self.sensor.in_waiting

            if not waiting:
                continue

            chunk = self.sensor.read(waiting)
            self.buffer.extend(chunk)
            packet_start = self.buffer.find(self.header)

            if packet_start == -1:
                continue

            if len(self.buffer) < packet_start + 4:
                continue

            packet_length = self.buffer[packet_start + 2 : packet_start + 4]
            packet_length = int.from_bytes(packet_length, "little")
            total_packet_length = packet_length + 6

            if not (len(self.buffer) - packet_start >= total_packet_length):
                continue

            frame = self.buffer[packet_start : packet_start + total_packet_length]

            if frame[-2] == sum(frame[:-2]) & 0xFF: 
                self.buffer.clear()
                return frame
            else:
                self.buffer.clear()
                continue

# mylidar = Lidar("/dev/ttyUSB0", 115200)
# mylidar.start()
# print(mylidar.header, mylidar.port, mylidar.baud, mylidar.sensor)
# print(mylidar.get_lidar_frame())