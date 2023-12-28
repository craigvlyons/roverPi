#!/usr/bin/python3

import os
import io
import json
import logging
import serial
import socketserver
from http import server
from threading import Condition
from urllib.parse import urlparse
from motor import convert_joystick_to_motor_speed
from typing import Tuple
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

x_min = 0
x_max = 0
y_min = 0
y_max = 0
joystick_val = 50

ser = serial.Serial('/dev/ttyS0', 1000000)

def load_file(path):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    absolute_path = os.path.join(script_dir, path)
    with open(absolute_path, 'rb') as file:
        return file.read()

class MockSerial:
    def __init__(self, port, baudrate):
        print(f"Initializing mock serial port: {port} with baudrate: {baudrate}")
    
    def write(self, data):
        print(f"Writing to mock serial: {data}")
    
    def readline(self):
        return "Mock response\n".encode()

    def close(self):
        print("Closing mock serial port")

#if os.path.exists('/dev/ttyS0'):
    #ser = serial.Serial('/dev/ttyS0', 1000000)
#else:
    #ser = MockSerial('/dev/ttyS0', 1000000)


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
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/control':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            x = data['x']
            y = data['y']
        
            # Convert x, y joystick values to motor speeds (L and R)    
            L, R = convert_joystick_to_motor_speed(x, y)

            command = {"T": 1, "L": L, "R": R}
            command_str = json.dumps(command).encode()
            print(f"sending command: {command_str}")
            ser.write(command_str)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
