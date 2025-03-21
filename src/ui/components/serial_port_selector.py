from PyQt5.QtWidgets import (QWidget, QComboBox, QPushButton, 
                           QHBoxLayout, QLabel)
from PyQt5.QtCore import pyqtSignal
import serial.tools.list_ports
from ..styles.button_styles import ButtonStyles

class SerialPortSelector(QWidget):
    port_changed = pyqtSignal(str)  # 포트 변경 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 포트 선택 레이블
        port_label = QLabel('포트:')
        layout.addWidget(port_label)
        
        # 포트 선택 콤보박스
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        self.port_combo.currentTextChanged.connect(self._on_port_changed)
        layout.addWidget(self.port_combo)
        
        # 새로고침 버튼
        refresh_btn = QPushButton('새로고침')
        refresh_btn.setStyleSheet(ButtonStyles.DEFAULT_STYLE)
        refresh_btn.clicked.connect(self.refresh_ports)
        refresh_btn.setFixedWidth(80)
        layout.addWidget(refresh_btn)
        
        # 여백 추가
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 초기 포트 목록 로드
        self.refresh_ports()

    def refresh_ports(self):
        """사용 가능한 시리얼 포트 목록 새로고침"""
        current = self.port_combo.currentText()
        self.port_combo.clear()
        
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)
        
        # 이전 선택 포트가 있으면 복원
        if current in ports:
            self.port_combo.setCurrentText(current)

    def _on_port_changed(self, port):
        """포트 변경 시그널 발생"""
        self.port_changed.emit(port)

    def get_current_port(self):
        """현재 선택된 포트 반환"""
        return self.port_combo.currentText()
