from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout)
from ...controllers.qc_controller import QCController
from ..components.serial_port_selector import SerialPortSelector
from ..components.log_viewer import LogViewer
from ..components.cli_interface import CLIInterface
from ..components.header_editor import HeaderEditor
from ..components.device_info_panel import DeviceInfoPanel

class QCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.qc_controller = QCController()
        
        # UI 컴포넌트 초기화
        self.port_selector = None
        self.log_viewer = None
        self.cli_interface = None
        self.header_editor = None
        self.device_info = None
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Quality Control')
        self.setFixedSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 컴포넌트 추가
        self.port_selector = SerialPortSelector()
        self.log_viewer = LogViewer()
        self.cli_interface = CLIInterface()
        self.header_editor = HeaderEditor()
        self.device_info = DeviceInfoPanel()
        
        layout.addWidget(self.port_selector)
        layout.addWidget(self.log_viewer)
        layout.addWidget(self.cli_interface)
        layout.addWidget(self.header_editor)
        layout.addWidget(self.device_info)
