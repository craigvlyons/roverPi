# serial_communication.py

import json
import threading
import serial

class SerialCommands:
    def __init__(self, port='/dev/ttyS0', baudrate=1000000):
        self.ser = serial.Serial(port, baudrate, timeout=2)
        self.lock = threading.Lock()

    # Send a command without expecting a response
    def send_serial_command(self, command):
        command_str = json.dumps(command).encode()
        self._write_command(command_str, expect_response=False)

    # Send a command and expect a response
    def send_serial_command_with_response(self, command):
        command_str = json.dumps(command).encode()
        return self._write_command(command_str, expect_response=True)

    # Helper function for sending commands (with or without expecting a response)
    def _write_command(self, command_str, expect_response):
        with self.lock:
            print(f"Sending command: {command_str}")
            self.ser.write(command_str)

            if expect_response:
                # Wait for a response from the device
                response = self.ser.read(1024)  # Read up to 1024 bytes
                print(f"Received response: {response}")
                return response
            else:
                # No response expected
                print("No response expected for this command.")
                return None
