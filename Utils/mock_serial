
class MockSerial:
    def __init__(self, port, baudrate):
        print(f"Initializing mock serial port: {port} with baudrate: {baudrate}")
    
    def write(self, data):
        print(f"Writing to mock serial: {data}")
    
    def readline(self):
        return "Mock response\n".encode()

    def close(self):
        print("Closing mock serial port")
