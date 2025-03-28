from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout)
from ...controllers.oc_controller import OCController
from ..components.serial_port_selector import SerialPortSelector
from ..components.device_info_panel import DeviceInfoPanel
from ..components.enhanced_progress_bar import EnhancedProgressBar
from ..components.shortcut_manager import ShortcutManager

class OCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.oc_controller = OCController()
        
        # UI 컴포넌트 초기화
        self.port_selector = None
        self.device_info = None
        self.progress_bar = None
        self.shortcut_manager = None
        
        self.setWindowTitle('Operation Center')
        self.initUI()
        
    def initUI(self):
        self.setFixedSize(800, 400)  # QC보다 작은 크기
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 컴포넌트 추가
        self.port_selector = SerialPortSelector()
        self.device_info = DeviceInfoPanel(mode='oc')
        self.progress_bar = EnhancedProgressBar()
        self.shortcut_manager = ShortcutManager()
        
        layout.addWidget(self.port_selector)
        layout.addWidget(self.device_info)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.shortcut_manager)
        
        # 단축키 설정
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """단축키 설정"""
        self.shortcut_manager.setup_default_shortcuts(
            download_callback=self.start_download,
            increment_callback=self.device_info.increment_serial,
            decrement_callback=self.device_info.decrement_serial
        )

    def start_download(self):
        """다운로드 시작"""
        # TODO: 다운로드 로직 구현
        pass
