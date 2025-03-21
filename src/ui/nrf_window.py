from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QLabel, 
                           QFileDialog, QProgressBar, QCheckBox, QVBoxLayout, 
                           QHBoxLayout, QGridLayout, QFrame, QComboBox)
from PyQt5.QtCore import Qt
from ..controllers.nrf_controller import NRFController
from ..controllers.file_controller import FileController
from .components.esp_component import ESPDownloadComponent
from .styles.button_styles import ButtonStyles
from ..utils.ui_utils import UIUtils
import os
import sys
import serial.tools.list_ports

class NRFDownloadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.nrf_controller = NRFController()
        self.file_controller = FileController()
        
        # UI 요소 초기화
        self.nrf_file_label = None
        self.port_combo = None
        self.nrf_download_btn = None
        self.full_download_btn = None
        self.progress_bar = None
        
        # ESP 컴포넌트 초기화
        self.esp_component = None
        
        # UI 설정
        self.initUI()

    def initUI(self):
        self.setWindowTitle('nRF52 Board Download')
        self.setFixedSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # ESP32 다운로드 컴포넌트 추가
        self.esp_component = ESPDownloadComponent()
        layout.addWidget(self.esp_component)
        
        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # nRF52 섹션
        nrf_section = QVBoxLayout()
        
        # nRF52 Section Title
        nrf_title = QLabel("nRF52 Firmware")
        nrf_title.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        nrf_section.addWidget(nrf_title)
        
        # nRF 파일 선택
        self._setup_nrf_file_selection(nrf_section)
        
        # OpenOCD 체크박스
        self._setup_openocd_checkbox(nrf_section)
        
        # nRF 프로그레스바
        self._setup_progress_bar(nrf_section)
        
        layout.addLayout(nrf_section)
        
        # 포트 선택 섹션
        self._setup_port_section(layout)
        
        # 전체 다운로드 버튼
        self._setup_download_buttons(layout)
        
        UIUtils.center_window(self)

    def _setup_nrf_file_selection(self, layout):
        file_group = QGridLayout()
        
        nrf_label = QLabel('nRF52 Firmware:')
        self.nrf_file_label = QLabel('No file selected')
        nrf_select_btn = QPushButton('Select File')
        nrf_select_btn.clicked.connect(lambda: self.select_file('nrf'))
        
        file_group.addWidget(nrf_label, 0, 0)
        file_group.addWidget(self.nrf_file_label, 0, 1)
        file_group.addWidget(nrf_select_btn, 0, 2)
        
        layout.addLayout(file_group)

    def _setup_openocd_checkbox(self, layout):
        self.openocd_checkbox = QCheckBox('Use OpenOCD (ST-Link)')
        self.openocd_checkbox.setChecked(False)
        layout.addWidget(self.openocd_checkbox)

    def _setup_progress_bar(self, layout):
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

    def _setup_download_buttons(self, layout):
        button_section = QHBoxLayout()
        
        self.nrf_download_btn = QPushButton('Download nRF Firmware')
        self.nrf_download_btn.setStyleSheet(ButtonStyles.DOWNLOAD_STYLE)
        self.nrf_download_btn.clicked.connect(self.nrf_download)
        
        self.full_download_btn = QPushButton('Full Download')
        self.full_download_btn.setStyleSheet(ButtonStyles.DOWNLOAD_STYLE)
        self.full_download_btn.clicked.connect(self.full_download)
        
        button_section.addWidget(self.nrf_download_btn)
        button_section.addWidget(self.full_download_btn)
        layout.addLayout(button_section)
        
        self.update_button_states()

    def select_file(self, file_type):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            f"Select {file_type.upper()} Firmware",
            "",
            "Hex Files (*.hex);;All Files (*.*)"
        )
        
        if file_path:
            if file_type == 'nrf':
                self.nrf_controller.set_firmware(file_path)
                # 파일 경로를 라벨에 표시
                file_name = os.path.basename(file_path)
                self.nrf_file_label.setText(f"Selected: {file_name}")
            
            self.update_button_states()

    def update_button_states(self):
        """버튼 상태 업데이트"""
        if not all(hasattr(self, attr) for attr in ['nrf_download_btn', 'full_download_btn', 'port_combo']):
            return
            
        # nRF 파일 선택 확인
        nrf_file_selected = (hasattr(self.nrf_controller.settings, 'firmware_path') and 
                            self.nrf_controller.settings.firmware_path is not None)
        
        # ESP 파일들 선택 확인
        esp_files_selected = all(
            hasattr(self.esp_component.esp_controller.settings, f'{ft}_path') and
            getattr(self.esp_component.esp_controller.settings, f'{ft}_path') is not None
            for ft in ['bootloader', 'partition', 'ota', 'app']
        )
        
        # 포트 선택 확인
        port_selected = bool(self.port_combo and 
                            self.port_combo.currentText() and 
                            self.port_combo.currentText() != "No ports available" and
                            not self.port_combo.currentText().startswith("Error:"))
        
        print(f"Button states - Port selected: {port_selected}, "
              f"nRF file: {nrf_file_selected}, "
              f"ESP files: {esp_files_selected}")  # 디버깅용 출력
        
        # nRF 다운로드 버튼 - nRF 파일과 포트가 모두 선택되어야 활성화
        if self.nrf_download_btn:
            self.nrf_download_btn.setEnabled(nrf_file_selected and port_selected)
        
        # 전체 다운로드 버튼 - 모든 파일과 포트가 선택되어야 활성화
        if self.full_download_btn:
            self.full_download_btn.setEnabled(
                nrf_file_selected and 
                esp_files_selected and 
                port_selected
            )

    def nrf_download(self):
        self.nrf_download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        success = self.nrf_controller.download(
            self.openocd_checkbox.isChecked(),
            lambda v: self.progress_bar.setValue(v)
        )
        
        if success:
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.setValue(0)
        
        self.nrf_download_btn.setEnabled(True)

    def full_download(self):
        self.full_download_btn.setEnabled(False)
        
        # ESP32 다운로드
        self.esp_component.start_download()
        
        # nRF52 다운로드
        self.nrf_download()
        
        self.full_download_btn.setEnabled(True)

    def get_serial_ports(self):
        """시리얼 포트 목록 반환"""
        try:
            # pyserial의 내장 함수를 사용하여 포트 검색
            ports = list(serial.tools.list_ports.comports())
            
            # 디버깅을 위한 포트 정보 출력
            print(f"Found {len(ports)} ports:")
            for port in ports:
                print(f"- {port.device} ({port.description})")
            
            if sys.platform.startswith('darwin'):  # macOS
                # cu.* 포트 우선 정렬
                return sorted([p.device for p in ports], 
                            key=lambda x: (not x.startswith('/dev/cu.'), x))
            else:
                return [p.device for p in ports]
                
        except Exception as e:
            print(f"Error scanning ports: {str(e)}")
            return []

    def refresh_ports(self):
        """포트 목록 새로고침"""
        if not hasattr(self, 'port_combo'):
            return
            
        try:
            current_port = self.port_combo.currentText()
            self.port_combo.clear()
            
            available_ports = self.get_serial_ports()
            print(f"Available ports: {available_ports}")  # 디버깅용 출력
            
            if available_ports:
                self.port_combo.addItems(available_ports)
                if current_port in available_ports:
                    index = self.port_combo.findText(current_port)
                    self.port_combo.setCurrentIndex(index)
                else:
                    self.port_combo.setCurrentIndex(0)
            else:
                self.port_combo.addItem("No ports available")
                print("No ports were found")
                
        except Exception as e:
            error_msg = f"Error refreshing ports: {str(e)}"
            print(error_msg)
            self.port_combo.addItem(error_msg)
        
        self.update_button_states()

    def _setup_port_section(self, layout):
        port_section = QHBoxLayout()
        
        # 포트 선택 그룹
        port_group = QHBoxLayout()
        
        port_label = QLabel('Select Port:')
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(250)
        self.port_combo.setMaximumWidth(400)
        
        # 포트 변경 시 이벤트 연결
        self.port_combo.currentTextChanged.connect(self.on_port_changed)
        
        refresh_btn = QPushButton('Refresh')
        refresh_btn.setStyleSheet(ButtonStyles.DEFAULT_STYLE)
        refresh_btn.clicked.connect(self.refresh_ports)
        refresh_btn.setFixedWidth(80)
        
        port_group.addWidget(port_label)
        port_group.addWidget(self.port_combo)
        port_group.addWidget(refresh_btn)
        port_group.addStretch()
        
        port_section.addLayout(port_group)
        layout.addLayout(port_section)
        
        # 초기 포트 목록 로드
        self.refresh_ports()

    def on_port_changed(self, port):
        """포트 선택 변경 시 호출되는 메서드"""
        print(f"Selected port: {port}")  # 디버깅용 출력
        self.update_button_states()
