import json
import subprocess

from Utils.commands import Commands, SerialCommands
from typing import AnyStr 

ser = SerialCommands()

class VoltageData:
    def __init__(self, voltage_mV, bus_voltage_V, power_mW):
        self.voltage_mV = voltage_mV
        self.bus_voltage_V = bus_voltage_V
        self.power_mW = power_mW

class UpdateTable:
    def __init__(self):
        self.ip_address = self.get_ip_address()
        self.imu_temperature = self.get_imu_temperature()
        self.voltage = self.get_voltage()
        self.pitch = self.get_pitch()
        self.roll = self.get_roll()
        self.yaw = self.get_yaw()
        self.gyro = self.get_gyro()
        self.display_output()

    def get_table_data(self):
        table_data = {
            "ip_address": self.ip_address,
            "imu_temperature": self.imu_temperature,
            "voltage": self.voltage,
            "pitch": self.pitch,
            "roll": self.roll,
            "yaw": self.yaw
        }
        return table_data

    def get_ip_address(self):
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ip_address = result.stdout.strip()
        return ip_address

    def get_imu_temperature(self):
        result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
        temperature = result.stdout.strip().split('=')[1]
        return temperature

    def get_voltage(self):
        # use the commands.INA219_INFO command to get the voltage
        print("Getting voltage")
        response = ser.send_serial_command(Commands.INA219_INFO)
        print(f"response: {response}")
         # Decode the bytes to a string
        #decoded_response = response.decode('utf-8')
        #print(f"decoded response : {decoded_response}")
        try:
            decoded_response = response.decode('utf-8')  # Decode the bytes to a string
            # data = json.loads(response)
            # print(data)
            # voltage_mV = data.get("mV", None)
            # bus_voltage_V = data.get("bus_V", None)
            # power_mW = data.get("power_mW", None)
            # voltage_data = VoltageData(voltage_mV, bus_voltage_V, power_mW)
            return decoded_response

        except (json.JSONDecodeError, AttributeError):
            print("Failed to decode JSON data from response:", response)

        return "none"
    

    def get_pitch(self)-> AnyStr:
        # Add code to get the pitch of the rover
        # print("get_pitch")
        # print(self.gyro)
        return str(5)

    def get_roll(self)-> AnyStr:
        # Add code to get the roll of the rover
        
        return str(7)

    def get_yaw(self)-> AnyStr:
        # Add code to get the yaw of the rover
        
        return str(9)
    
    def get_gyro(self)-> AnyStr:
        # use utils.commands to get the gyro of the rover
        imu_info = ser.send_serial_command(Commands.IMU_INFO)
        print("get_gyro")
        print(imu_info)
        
        return str(11)

    def display_output(self)-> AnyStr:
        # use the commands.OLED_SET command to display the output        
        pass
