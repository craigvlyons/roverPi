import libcamera
import cv2
import numpy as np
import io
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from http import server
import logging
from time import sleep

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class CameraManager:
    def __init__(self, width=640, height=480, flip_horizontal=False, flip_vertical=True):
        # Initialize camera parameters
        self.width = width
        self.height = height
        self.flip_horizontal = flip_horizontal
        self.flip_vertical = flip_vertical
        
        # Initialize the camera
        self.picam2 = Picamera2()
        self.output = StreamingOutput()
        self._configure_camera()

    def _configure_camera(self):
        # Create the camera configuration with the specified resolution
        config = self.picam2.create_video_configuration(main={"size": (self.width, self.height)})

        # Apply flipping (horizontal/vertical) if needed
        preview_config = self.picam2.create_preview_configuration()
        preview_config["transform"] = libcamera.Transform(
            hflip=int(self.flip_horizontal), vflip=int(self.flip_vertical)
        )

        # Configure the camera with the defined settings
        self.picam2.configure(config)

    def start_stream(self):
        # Start the camera recording with the specified output
        self.picam2.start_recording(JpegEncoder(), FileOutput(self.output))

    def stop_stream(self):
        # Stop the camera recording
        self.picam2.stop_recording()

    def crop_to_rectangle(self, image):
        # This method crops the circular image into a rectangular one
        height, width = image.shape[:2]

        # Define the center of the image
        center_x, center_y = width // 2, height // 2

        # Define the desired width and height of the rectangular crop
        crop_size = min(width, height)

        # Calculate the crop area
        x1 = center_x - crop_size // 2
        y1 = center_y - crop_size // 2
        x2 = center_x + crop_size // 2
        y2 = center_y + crop_size // 2

        # Crop the image to a rectangle
        cropped_image = image[y1:y2, x1:x2]

        # Optionally resize the image to standard output resolution
        return cv2.resize(cropped_image, (self.width, self.height))

    def undistort_image(self, image, K, D):
        # Undistort a fisheye image using the camera matrix K and distortion coefficients D
        h, w = image.shape[:2]
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (w, h), cv2.CV_16SC2)
        undistorted_image = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        return undistorted_image

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
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

                    # Convert the frame to a numpy array for processing
                    np_img = np.frombuffer(frame, dtype=np.uint8)
                    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

                    # Optionally crop the image (if you need to crop to rectangle)
                    # img = camera_manager.crop_to_rectangle(img)

                    # Apply lens distortion correction
                    K = np.array([
                        [280, 0, 320],   # Lower focal length to correct zoom
                        [0, 280, 240],
                        [0, 0, 1]
                    ])
                    D = np.array([[-2.0], [0.8], [0.0], [0.0]])  # Stronger negative value for radial distortion (k1)

                    img = self.undistort_image(img, K, D)

                    # Encode the corrected image back to JPEG
                    _, jpeg = cv2.imencode('.jpg', img)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(jpeg))
                    self.end_headers()
                    self.wfile.write(jpeg)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(f'Removed streaming client {self.client_address}: {str(e)}')


