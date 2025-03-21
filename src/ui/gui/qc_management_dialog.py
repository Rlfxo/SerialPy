from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QWidget)
from ..components.header_editor import HeaderEditor
from ..components.device_info_panel import DeviceInfoPanel
from ..components.download_panel import DownloadPanel  # 새로 만들어야 함

class QCManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Quality Control Management')
        self.setFixedSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 탭 위젯 설정
        self.tab_widget = QTabWidget()
        
        # 각 기능별 탭 생성
        self.header_tab = QWidget()
        self.device_tab = QWidget()
        self.download_tab = QWidget()
        
        # 탭별 컴포넌트 설정
        self._setup_header_tab()
        self._setup_device_tab()
        self._setup_download_tab()
        
        # 탭 추가
        self.tab_widget.addTab(self.header_tab, "Header 관리")
        self.tab_widget.addTab(self.device_tab, "Device 정보")
        self.tab_widget.addTab(self.download_tab, "Download")
        
        layout.addWidget(self.tab_widget)

    def _setup_header_tab(self):
        layout = QVBoxLayout(self.header_tab)
        self.header_editor = HeaderEditor()
        layout.addWidget(self.header_editor)

    def _setup_device_tab(self):
        layout = QVBoxLayout(self.device_tab)
        self.device_info = DeviceInfoPanel(mode='qc')
        layout.addWidget(self.device_info)

    def _setup_download_tab(self):
        layout = QVBoxLayout(self.download_tab)
        self.download_panel = DownloadPanel()
        layout.addWidget(self.download_panel)

    def show_header_tab(self):
        self.tab_widget.setCurrentIndex(0)

    def show_device_tab(self):
        self.tab_widget.setCurrentIndex(1)

    def show_download_tab(self):
        self.tab_widget.setCurrentIndex(2) 