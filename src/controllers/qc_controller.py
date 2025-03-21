from .serial_controller import SerialController

class LogManager:
    def __init__(self):
        self.log_file = None
        
    def start_logging(self, file_path):
        self.log_file = file_path
        # 로깅 로직 구현 예정
        pass

class HeaderManager:
    def __init__(self):
        self.current_header = None
        
    def read_header(self, file_path):
        # 헤더 읽기 로직 구현 예정
        pass

class CLIManager:
    def __init__(self):
        self.command_history = []
        
    def execute_command(self, command):
        # 명령어 실행 로직 구현 예정
        pass

class QCController:
    def __init__(self):
        self.serial_controller = SerialController()
        self.log_manager = LogManager()
        self.header_manager = HeaderManager()
        self.cli_manager = CLIManager()
