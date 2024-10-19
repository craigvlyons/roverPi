import threading
import json
import time
import Utils.motor as motor 
import Utils.commands as commands


class MotorSerialThread(threading.Thread):
    def __init__(self, serial_commands, joystick_update_interval=0.1):
        super().__init__()
        self.serial_commands = serial_commands
        self.joystick_update_interval = joystick_update_interval
        self.running = False
        self.lock = threading.Lock()
        self.x = 0
        self.y = 0
        self.last_command = commands.SPEED_INPUT.copy()

    def run(self):
        self.running = True
        while self.running:
            with self.lock:
                L, R = motor.convert_joystick_to_motor_speed(self.x, self.y)
                if self.last_command["L"] != L or self.last_command["R"] != R:
                    self.last_command["L"] = L
                    self.last_command["R"] = R
                    self.serial_commands.send_serial_command(self.last_command)
            time.sleep(self.joystick_update_interval)

    def update_joystick(self, x, y):
        with self.lock:
            self.x = x
            self.y = y

    def stop(self):
        self.running = False
