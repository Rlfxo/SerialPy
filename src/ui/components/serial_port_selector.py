from PyQt5.QtWidgets import (QWidget, QComboBox, QPushButton, 
                           QHBoxLayout, QLabel)
from PyQt5.QtCore import pyqtSignal
import serial.tools.list_ports

class SerialPortSelector(QWidget):
    port_connected = pyqtSignal(bool)  # 연결 상태 변경 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.serial_port = None
        self.baud_rate = 115200  # 고정 보레이트
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
        layout.addWidget(self.port_combo)
        
        # 보레이트 표시 레이블
        baud_label = QLabel(f'{self.baud_rate} bps')
        layout.addWidget(baud_label)
        
        # 새로고침 버튼
        refresh_btn = QPushButton('새로고침')
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(refresh_btn)
        
        # 연결/해제 버튼
        self.connect_btn = QPushButton('연결')
        self.connect_btn.setFixedWidth(80)
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        # 여백 추가
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 스타일 설정
        self.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                padding: 5px;
            }
        """)
        
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
            
        # 포트가 없으면 연결 버튼 비활성화
        self.connect_btn.setEnabled(len(ports) > 0)

    def toggle_connection(self):
        """연결/해제 토글"""
        if not self.is_connected:
            try:
                port = self.port_combo.currentText()
                if not port:
                    return
                
                # 시리얼 포트 연결
                self.serial_port = serial.Serial(
                    port=port,
                    baudrate=self.baud_rate,
                    timeout=1
                )
                
                self.is_connected = True
                self.connect_btn.setText('해제')
                self.connect_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #c0392b;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e74c3c;
                    }
                """)
                
                # UI 상태 업데이트
                self.port_combo.setEnabled(False)
                self.port_connected.emit(True)
                
            except Exception as e:
                print(f"연결 실패: {str(e)}")
                self.is_connected = False
                self.serial_port = None
                self.port_connected.emit(False)
        else:
            # 연결 해제
            if self.serial_port:
                self.serial_port.close()
            
            self.is_connected = False
            self.serial_port = None
            self.connect_btn.setText('연결')
            self.connect_btn.setStyleSheet("""
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
            
            # UI 상태 업데이트
            self.port_combo.setEnabled(True)
            self.port_connected.emit(False)

    def get_serial_port(self):
        """현재 연결된 시리얼 포트 객체 반환"""
        return self.serial_port

    def is_port_connected(self):
        """현재 연결 상태 반환"""
        return self.is_connected
