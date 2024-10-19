import logging
import threading
import json
import time
from Utils.motor  import convert_joystick_to_motor_speed
from Utils.commands import Commands 
from Utils.SerialCommands import SerialCommands



class MotorSerial:
    def __init__(self, serial_commands):
        self.serial_commands = serial_commands
        self.lock = threading.Lock()
        self.x = 0
        self.y = 0
        self.last_command = Commands.SPEED_INPUT.copy()

        # Initialize logger
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)


    def update_joystick(self, x, y):
        with self.lock:
            self.x = x
            self.y = y
            self.logger.debug(f"Joystick updated: x={x}, y={y}")

            # Convert joystick values to motor speed
            L, R = convert_joystick_to_motor_speed(self.x, self.y)
            self.logger.debug(f"Joystick (x, y): {self.x}, {self.y} -> Motor (L, R): {L}, {R}")

            # If the motor command is different, send the update
            if self.last_command["L"] != L or self.last_command["R"] != R:
                self.last_command["L"] = L
                self.last_command["R"] = R
                self.logger.info(f"Sending motor command: {self.last_command}")
                self.serial_commands.send_serial_command(self.last_command)


    def emergency_stop(self):
        with self.lock:
            # Send the emergency stop command
            self.logger.info("Sending emergency stop command")
            self.serial_commands.send_serial_command(Commands.EMERGENCY_STOP)
