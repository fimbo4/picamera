from flask import Flask, Response, render_template_string, render_template
from picamera2 import Picamera2
import cv2
import time
import serial
import RPi.GPIO as GPIO

app = Flask(__name__)

#camera setup start
camera = Picamera2()

config = camera.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
camera.configure(config)
camera.start()

time.sleep(2)
#camera setup end

#mount setup start
SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 2400
EN_PIN = 17
ADDRESS = 0x01
SPEED = 0x20

GPIO.setmode(GPIO.BCM)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.output(EN_PIN, GPIO.LOW)

ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=BAUD_RATE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)
#mount setup end

def generate_frames():
    while True:
        frame = camera.capture_array()
        frame = cv2.flip(frame, 0) #flip image in my case
        ret, jpeg = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpeg.tobytes()
            + b"\r\n"
        )

def pelco_cmd(cmd1, cmd2, data1, data2):
    checksum = (ADDRESS + cmd1 + cmd2 + data1 + data2) % 256
    packet = bytes([0xFF, ADDRESS, cmd1, cmd2, data1, data2, checksum])

    GPIO.output(EN_PIN, GPIO.HIGH)
    time.sleep(0.001)
    ser.write(packet)
    ser.flush()
    time.sleep(0.001)
    GPIO.output(EN_PIN, GPIO.LOW)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/move/<direction>", methods=['POST'])
def move(direction):
    if direction == "left":
        pelco_cmd(0x00, 0x04, SPEED, 0x00)
    elif direction == "right":
        pelco_cmd(0x00, 0x02, SPEED, 0x00)
    elif direction == "up":
        pelco_cmd(0x00, 0x08, 0x00, SPEED)
    elif direction == "down":
        pelco_cmd(0x00, 0x10, 0x00, SPEED)
    else:
        return "bad direction", 400
    return "move"

@app.route("/stop", methods=['POST'])
def stop():
    pelco_cmd(0x00, 0x00, 0x00, 0x00)
    return "stop"

if __name__ == "__main__":
    app.run(
        #debug=True, this will crash
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
