from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QSplitter, QFrame, QLabel)
from PyQt5.QtCore import Qt
from ...controllers.qc_controller import QCController
from ..components.serial_port_selector import SerialPortSelector
from ..components.log_viewer import LogViewer
from ..components.cli_interface import CLIInterface
from ..components.header_editor import HeaderEditor
from ..components.device_info_panel import DeviceInfoPanel
from .qc_management_dialog import QCManagementDialog  # 새로 만들 관리 팝업

class QCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.qc_controller = QCController()
        self.management_dialog = None
        
        # UI 컴포넌트 초기화
        self.port_selector = None
        self.log_viewer = None
        self.cli_interface = None
        self.header_editor = None
        self.device_info = None
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Quality Control - Monitoring')
        self.showMaximized()
        
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(main_widget)
        
        # 상단 모니터링 영역 (좌우 분할)
        monitoring_area = QSplitter(Qt.Horizontal)
        
        # 왼쪽 모니터
        left_monitor = QFrame()
        left_layout = QVBoxLayout(left_monitor)
        self.left_port_selector = SerialPortSelector()
        self.left_log_viewer = LogViewer()
        left_layout.addWidget(QLabel("Monitor 1"))
        left_layout.addWidget(self.left_port_selector)
        left_layout.addWidget(self.left_log_viewer)
        
        # 오른쪽 모니터
        right_monitor = QFrame()
        right_layout = QVBoxLayout(right_monitor)
        self.right_port_selector = SerialPortSelector()
        self.right_log_viewer = LogViewer()
        right_layout.addWidget(QLabel("Monitor 2"))
        right_layout.addWidget(self.right_port_selector)
        right_layout.addWidget(self.right_log_viewer)
        
        # 모니터 추가
        monitoring_area.addWidget(left_monitor)
        monitoring_area.addWidget(right_monitor)
        monitoring_area.setSizes([self.width() // 2, self.width() // 2])  # 50:50 분할
        
        main_layout.addWidget(monitoring_area)
        
        # 하단 버튼 영역
        button_layout = QHBoxLayout()
        
        # 관리 기능 버튼들
        header_btn = QPushButton('Header 관리')
        device_btn = QPushButton('Device 정보')
        download_btn = QPushButton('Download')
        
        # 버튼 스타일 설정
        for btn in [header_btn, device_btn, download_btn]:
            btn.setFixedSize(150, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
            """)
        
        # 버튼 이벤트 연결
        header_btn.clicked.connect(self.show_header_management)
        device_btn.clicked.connect(self.show_device_management)
        download_btn.clicked.connect(self.show_download_management)
        
        button_layout.addStretch()
        button_layout.addWidget(header_btn)
        button_layout.addWidget(device_btn)
        button_layout.addWidget(download_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)

        # 시리얼 포트 연결 시그널 연결
        self.left_port_selector.port_connected.connect(self.on_left_port_connection_changed)
        self.right_port_selector.port_connected.connect(self.on_right_port_connection_changed)

    def show_header_management(self):
        if not self.management_dialog:
            self.management_dialog = QCManagementDialog(self)
        self.management_dialog.show_header_tab()
        self.management_dialog.exec_()

    def show_device_management(self):
        if not self.management_dialog:
            self.management_dialog = QCManagementDialog(self)
        self.management_dialog.show_device_tab()
        self.management_dialog.exec_()

    def show_download_management(self):
        if not self.management_dialog:
            self.management_dialog = QCManagementDialog(self)
        self.management_dialog.show_download_tab()
        self.management_dialog.exec_()

    def on_left_port_connection_changed(self, connected):
        if connected:
            serial_port = self.left_port_selector.get_serial_port()
            self.left_log_viewer.start_monitoring(serial_port)
            print("Left monitor started")
        else:
            self.left_log_viewer.stop_monitoring()
            print("Left monitor stopped")

    def on_right_port_connection_changed(self, connected):
        if connected:
            serial_port = self.right_port_selector.get_serial_port()
            self.right_log_viewer.start_monitoring(serial_port)
            print("Right monitor started")
        else:
            self.right_log_viewer.stop_monitoring()
            print("Right monitor stopped")
