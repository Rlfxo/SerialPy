import serial.tools.list_ports
import sys

def get_available_ports():
    ports = []
    for port in serial.tools.list_ports.comports():
        # Windows에서는 'COM'으로 시작하는 포트만 필터링
        if sys.platform == 'win32':
            if port.device.startswith('COM'):
                ports.append(port.device)
        else:
            # Linux/Mac의 경우 기존 로직 유지
            if 'USB' in port.description:
                ports.append(port.device)
    return ports
