import json
import threading
import serial

'''For more details and descriptions of each command, you can refer to the 
[WAVE ROVER page on Waveshare's Wiki](https://www.waveshare.com/wiki/WAVE_ROVER).'''

class Commands:
    EMERGENCY_STOP =         {"T": 0}
    PID_SET =                {"T":2,"P":170,"I":90}
    SPEED_INPUT =            {"T":1,"L":0,"R":0}
    OLED_SET =               {"T":3,"lineNum":0,"Text":"YourText"}
    OLED_DEFAULT =           {"T":-3}
    PWM_SERVO_CTRL =         {"T":40,"pos":90,"spd":30}
    PWM_SERVO_MID =          {"T":-4}
    BUS_SERVO_CTRL =         {"T":50, "id":1, "pos":2047, "spd":500, "acc":30}
    BUS_SERVO_MID =          {"T":-5, "id":1}
    BUS_SERVO_SCAN =         {"T":52,"num":20}
    BUS_SERVO_INFO =         {"T":53,"id":1}
    BUS_SERVO_ID_SET =       {"T":54,"old":1,"new":2}
    BUS_SERVO_TORQUE_LOCK =  {"T":55,"id":1,"status":1}
    BUS_SERVO_TORQUE_LIMIT = {"T":56,"id":1,"limit":500}
    BUS_SERVO_MODE =         {"T":57,"id":1,"mode":0}
    WIFI_SCAN =              {"T":60}
    WIFI_TRY_STA =           {"T":61}
    WIFI_AP_DEFAULT =        {"T":62}
    WIFI_INFO =              {"T":65} 
    WIFI_OFF =               {"T":66}  # Turn off the WiFi module.
    INA219_INFO =            {"T":70}  # Get information about the INA219, including the voltage and current power of the power supply.
    IMU_INFO =               {"T":71}  # Get information about the IMU,  including heading angle, geomagnetic field, acceleration, attitude, temperature, etc.
    ENCODER_INFO =           {"T":73}  
    DEVICE_INFO =            {"T":74}  #
    IO_IR_CUT =              {"T":80,"status":1}  # Control the IR-CUT of the camera. IO5 pin 
    SET_SPD_RATE =           {"T":901,"L":1.0,"R":1.0}  # Set the speed ratio of the left and right motors.
    GET_SPD_RATE =           {"T":902}
    SPD_RATE_SAVE =          {"T":903}
    GET_NVS_SPACE =          {"T":904}
    NVS_CLEAR =              {"T":905}
    

# class SerialCommands:
#     def __init__(self, port='/dev/ttyS0', baudrate=1000000):
#         self.ser = serial.Serial(port, baudrate, timeout=2)
#         self.lock = threading.Lock()
        

#    # 1. Send a command without expecting a response
#     def send_serial_command(self, command: Commands):
#         command_str = json.dumps(command).encode()
#         self.write_command(command_str, expect_response=False)

#     # 2. Send a command and expect a response
#     def send_serial_command_with_response(self, command: Commands):
#         command_str = json.dumps(command).encode()
#         return self.write_command(command_str, expect_response=True)

#     # Helper function for sending commands (with or without expecting a response)
#     def write_command(self, command_str, expect_response):
#         with self.lock:
#             print(f"Sending command: {command_str}")
#             self.ser.write(command_str)

#             if expect_response:
#                 # Wait for a response from the device
#                 response = self.ser.read(1024)  # Read up to 1024 bytes
#                 print(f"Received response: {response}")
#                 return response
#             else:
#                 # No response expected
#                 print("No response expected for this command.")
#                 return None

#     def get_responce(self):
#         return self.responce
