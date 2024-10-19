

import os
import io
import json
import logging
import sys

import socketserver
import threading
import Utils.settings as settings
import libcamera

from Utils.commands import Commands
from Utils.SerialCommands import SerialCommands
from Utils.MotorSerial import MotorSerial 
from http import server
from threading import Condition
from urllib.parse import urlparse

from Utils.update_table import UpdateTable
from typing import Tuple
from time import sleep, time
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from Utils.CameraManager import CameraManager

# print(sys.path)
# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize serial communication
ser = SerialCommands('/dev/ttyS0')
commands = Commands
motor_serial = MotorSerial(ser)
esp_commands = SerialCommands('/dev/ttyS0')

# Global variables
camera_manager = None
output = None


def run_camera():
    global camera_manager, output

    camera_manager = CameraManager(width=640, height=480)
    camera_manager.start_stream()
    output = camera_manager.output  # Assign the camera output for streaming


#start camera thread.
camera_thread = threading.Thread(target=run_camera)
camera_thread.start()


def load_file(path):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    absolute_path = os.path.join(script_dir, path)
    with open(absolute_path, 'rb') as file:
        return file.read()


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

        elif self.path == '/index.html':
            content = load_file('index.html')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path.startswith("/css/") or self.path.startswith("/images/"):
            # Extract file path and serve files from css and images directories
            parsed_path = urlparse(self.path)
            file_path = os.path.join('.', parsed_path.path[1:])  # Remove leading slash
            if os.path.exists(file_path) and os.path.isfile(file_path):
                content = load_file(file_path)
                if file_path.endswith(".css"):
                    content_type = 'text/css'
                elif file_path.endswith((".jpg", ".jpeg")):
                    content_type = 'image/jpeg'
                elif file_path.endswith(".png"):
                    content_type = 'image/png'
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404)
                self.end_headers()

        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))     
                 
        elif self.path == '/status':                  
            # Use the UpdateTable class to get the rover's information
            #table_data = UpdateTable().get_table_data()
            #table_json = json.dumps(table_data).encode()

            self.send_response(200)
            #self.send_header('Content-Type', 'application/json')
            #self.send_header('Content-Length', len(table_json))
            #self.end_headers()
            #self.wfile.write(table_json)
 
        else:
            self.send_error(404)
            self.end_headers()


    def do_POST(self):
        if self.path == '/control':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                 # Validate data (e.g., ensure 'x' and 'y' keys exist)
                if 'x' not in data or 'y' not in data:
                    self.send_error(400, "Invalid data")
                    return

                x = data['x']
                y = data['y']
                if x == 0 and y == 0:
                   # Emergency stop when x and y are 0
                    motor_serial.emergency_stop()
                else:
                    # Update joystick values and send the motor command
                    motor_serial.update_joystick(x, y)
        
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')

            except json.JSONDecodeError:
                self.send_error(400, "Malformed JSON data")
                return

        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, output):
        super().__init__(server_address, RequestHandlerClass)
        self.output = output
        

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler, output)
    server.serve_forever()
finally:
    if camera_manager:
        camera_manager.stop_stream()

