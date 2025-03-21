from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QSplitter, QFrame, QLabel, QFileDialog, QMessageBox, QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from ...controllers.qc_controller import QCController
from ..components.serial_port_selector import SerialPortSelector
from ..components.log_viewer import LogViewer
from ..components.cli_interface import CLIInterface
from ..components.header_editor import HeaderEditor
from ..components.device_info_panel import DeviceInfoPanel
from .qc_management_dialog import QCManagementDialog  # 새로 만들 관리 팝업
from ...file.core.header_manager import HeaderManager

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
        
        # 헤더 매니저 초기화
        self.header_manager = HeaderManager()
        
        # 탭 위젯 설정
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Download 탭
        self.download_tab = QWidget()
        self.download_layout = QVBoxLayout()
        self.download_tab.setLayout(self.download_layout)
        self.tab_widget.addTab(self.download_tab, "Download")

        # Header 관리 탭
        self.init_header_tab()
        
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

    def init_header_tab(self):
        """Header 관리 탭 초기화"""
        self.header_tab = QWidget()
        self.header_layout = QVBoxLayout()
        self.header_tab.setLayout(self.header_layout)

        # 헤더 매니저 초기화
        self.header_manager = HeaderManager()

        # 파일 선택 버튼
        self.header_load_button = QPushButton("이미지 파일 불러오기")
        self.header_load_button.clicked.connect(self.load_image_file)
        self.header_layout.addWidget(self.header_load_button)

        # 헤더 정보 테이블 생성
        self.header_table = QTableWidget()
        self.header_table.setColumnCount(4)
        self.header_table.setHorizontalHeaderLabels(["필드", "크기(bytes)", "수정가능", "값"])
        
        # 테이블 스타일 설정
        self.header_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.header_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        # 헤더 필드 정보로 테이블 초기화
        self.init_header_table()
        
        self.header_layout.addWidget(self.header_table)
        self.tab_widget.addTab(self.header_tab, "Header 관리")

    def init_header_table(self):
        """헤더 테이블 초기화"""
        self.header_table.setRowCount(len(self.header_manager.header_fields))
        
        for row, (field, info) in enumerate(self.header_manager.header_fields.items()):
            # 필드 이름
            field_item = QTableWidgetItem(field)
            field_item.setFlags(field_item.flags() & ~Qt.ItemIsEditable)
            self.header_table.setItem(row, 0, field_item)
            
            # 크기
            size_item = QTableWidgetItem(str(info['size']))
            size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)
            self.header_table.setItem(row, 1, size_item)
            
            # 수정 가능 여부
            editable_item = QTableWidgetItem("예" if info['editable'] else "아니오")
            editable_item.setFlags(editable_item.flags() & ~Qt.ItemIsEditable)
            self.header_table.setItem(row, 2, editable_item)
            
            # 값 (초기에는 빈칸)
            value_item = QTableWidgetItem("-")
            if not info['editable']:
                value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            self.header_table.setItem(row, 3, value_item)

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

    def load_image_file(self):
        """이미지 파일을 불러와서 헤더 정보를 표시"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "이미지 파일 선택",
                "",
                "Image Files (*.img);;All Files (*.*)"
            )
            
            if not file_path:
                return
                
            # 헤더 정보 읽기
            header_info = self.header_manager.read_header(file_path)
            
            # 테이블 업데이트
            for row in range(self.header_table.rowCount()):
                field_name = self.header_table.item(row, 0).text()
                value = header_info.get(field_name)
                
                if value is not None:
                    if field_name == 'length':
                        display_value = f"{value:,} bytes"
                    elif field_name == 'sha256':
                        display_value = f"{value[:16]}..."
                    else:
                        display_value = str(value)
                        
                    self.header_table.item(row, 3).setText(display_value)
            
            QMessageBox.information(self, "성공", "이미지 파일을 성공적으로 로드했습니다.")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 로드 중 오류 발생: {str(e)}")
