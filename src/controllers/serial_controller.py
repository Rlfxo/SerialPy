import serial
import serial.tools.list_ports

class PortManager:
    def __init__(self):
        self.current_port = None
        self.baudrate = 115200

    def get_available_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port):
        try:
            self.current_port = serial.Serial(port, self.baudrate)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

class DownloadManager:
    def __init__(self):
        self.current_file = None
        
    def start_download(self, file_path):
        self.current_file = file_path
        # 다운로드 로직 구현 예정
        pass

class DeviceCommManager:
    def __init__(self):
        self.device_info = {}
        
    def read_device_info(self):
        # 장치 정보 읽기 로직 구현 예정
        pass

class SerialController:
    def __init__(self):
        self.port_manager = PortManager()
        self.download_manager = DownloadManager()
        self.device_comm_manager = DeviceCommManager()
