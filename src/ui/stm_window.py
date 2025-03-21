from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QLabel, 
                           QFileDialog, QProgressBar, QVBoxLayout, 
                           QHBoxLayout, QGridLayout, QMessageBox, QFrame,
                           QApplication)
from PyQt5.QtCore import Qt, QTimer
import os
from src.controllers.stm_controller import STMController
from src.ui.styles.button_styles import ButtonStyles
from src.ui.components.esp_component import ESPDownloadComponent
from src.ui.smt_mode_window import SMTModeWindow
import logging
import shutil

class STMDownloadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STM32 Board Download")
        self.stm_controller = STMController()
        
        # UI 요소 초기화
        self.download_btn = None
        self.firmware_label = None
        self.progress_bar = None
        self.status_label = None
        self.mode_toggle = None
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # UI 설정
        self.initUI()
        
        # 초기 모드 설정 (AC)
        self.load_default_firmware("AC")
        
    def initUI(self):
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # ESP32 섹션 (상단)
        self.esp_component = ESPDownloadComponent()
        layout.addWidget(self.esp_component)
        
        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # STM32 섹션 (하단)
        stm_widget = QWidget()
        stm_layout = QVBoxLayout(stm_widget)
        
        # STM32 Section Title
        stm_title = QLabel("STM32 Firmware")
        stm_title.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        stm_layout.addWidget(stm_title)
        
        # 파일 선택 섹션
        self._setup_file_selection(stm_layout)
        
        # ST-Link 정보 표시
        stlink_info = QLabel("Using ST-Link for programming (OpenOCD required)")
        stlink_info.setStyleSheet("color: #2980b9; font-style: italic;")
        stm_layout.addWidget(stlink_info)
        
        # 다운로드 섹션
        self._setup_download_section(stm_layout)
        
        layout.addWidget(stm_widget)
        
        # 하단 버튼 영역
        bottom_layout = QHBoxLayout()
        
        # SMT Mode 버튼들 추가
        self.smt_ac_mode_btn = QPushButton("SMT AC Mode")
        self.smt_ac_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;  /* 주황색 */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
            QPushButton:disabled {
                background-color: #D3D3D3;
                color: #A9A9A9;
            }
        """)
        self.smt_ac_mode_btn.clicked.connect(self.open_smt_ac_mode)
        self.smt_ac_mode_btn.setEnabled(False)
        bottom_layout.addWidget(self.smt_ac_mode_btn)
        
        self.smt_dc_mode_btn = QPushButton("SMT DC Mode")
        self.smt_dc_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #800080;  /* 자주색 */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9400D3;
            }
            QPushButton:disabled {
                background-color: #D3D3D3;
                color: #A9A9A9;
            }
        """)
        self.smt_dc_mode_btn.clicked.connect(self.open_smt_dc_mode)
        self.smt_dc_mode_btn.setEnabled(False)
        bottom_layout.addWidget(self.smt_dc_mode_btn)
        
        layout.addLayout(bottom_layout)
        
        # 초기 상태 설정
        self.update_download_button()
        self.update_smt_button_state()
        
        # 기본 파일 로드 상태 업데이트
        self.update_firmware_label()
        
        # 타이머 설정 (주기적으로 버튼 상태 업데이트)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_smt_button_state)
        self.timer.start(1000)  # 1초마다 업데이트
        
        # 윈도우 크기 설정
        self.setFixedSize(600, 600)

    def _setup_file_selection(self, layout):
        file_section = QHBoxLayout()
        
        # STM32 Firmware 라벨
        firmware_label = QLabel("STM32 Firmware:")
        file_section.addWidget(firmware_label)
        
        # AC/DC 토글 버튼 추가
        self.mode_toggle = QPushButton("AC")
        self.mode_toggle.setCheckable(True)
        self.mode_toggle.setFixedWidth(60)
        self.mode_toggle.clicked.connect(self.toggle_mode)
        self.mode_toggle.setStyleSheet("""
            QPushButton {
                background-color: #FF8C00;  /* 주황색 (AC 모드) */
                color: white;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #800080;  /* 자주색 (DC 모드) */
            }
            QPushButton:hover {
                background-color: #FFA500;  /* 주황색 hover */
            }
            QPushButton:checked:hover {
                background-color: #9400D3;  /* 자주색 hover */
            }
        """)
        file_section.addWidget(self.mode_toggle)
        
        # 파일 선택 결과 표시 라벨
        self.firmware_label = QLabel("No file selected")
        file_section.addWidget(self.firmware_label)
        
        # 파일 선택 버튼
        select_file_btn = QPushButton("Select File")
        select_file_btn.clicked.connect(self.select_file)
        file_section.addWidget(select_file_btn)
        
        layout.addLayout(file_section)

    def _setup_download_section(self, layout):
        download_group = QVBoxLayout()
        
        # 상태 라벨
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        download_group.addWidget(self.status_label)
        
        # 프로그레스 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        download_group.addWidget(self.progress_bar)
        
        # 다운로드 버튼
        self.download_btn = QPushButton("Download STM32 Firmware")
        self.download_btn.setStyleSheet(ButtonStyles.DOWNLOAD_STYLE)
        self.download_btn.clicked.connect(self.start_download)
        download_group.addWidget(self.download_btn)
        
        layout.addLayout(download_group)

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select STM32 Firmware File",
            "",
            "Binary Files (*.bin);;All Files (*.*)"
        )
        
        if file_path:
            self.stm_controller.settings.firmware_path = file_path
            self.update_firmware_label()
            self.update_download_button()

    def update_download_button(self):
        if not hasattr(self, 'download_btn') or self.download_btn is None:
            return
            
        # 파일이 선택되었는지 확인
        file_selected = bool(self.stm_controller.settings.firmware_path)
        self.download_btn.setEnabled(file_selected)

    def start_download(self):
        if not self.stm_controller.settings.firmware_path:
            QMessageBox.warning(self, "Warning", "Please select firmware file first")
            return
        
        self.download_btn.setEnabled(False)
        self.firmware_label.setEnabled(False)
        self.progress_bar.setValue(0)
        
        def update_progress(value, status):
            self.progress_bar.setValue(value)
            self.status_label.setText(status)
            QApplication.processEvents()
        
        success, message = self.stm_controller.download(update_progress)
        
        self.download_btn.setEnabled(True)
        self.firmware_label.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def validate_download(self):
        if not self.stm_controller.settings.firmware_path:
            QMessageBox.warning(self, "Warning", "Please select a firmware file first.")
            return False
        return True

    def update_smt_button_state(self):
        """SMT 모드 버튼 상태 업데이트"""
        # ESP32와 STM32 모두 다운로드 준비가 되었는지 확인
        esp_ready = all([
            self.esp_component.esp_controller.settings.bootloader_path,
            self.esp_component.esp_controller.settings.partition_path,
            self.esp_component.esp_controller.settings.ota_path,
            self.esp_component.esp_controller.settings.app_path,
            self.esp_component.esp_controller.settings.port
        ])
        
        # AC/DC 모드별 펌웨어 파일 존재 여부 확인
        ac_firmware_exists = self.stm_controller.settings.ac_firmware.exists()
        dc_firmware_exists = self.stm_controller.settings.dc_firmware.exists()
        
        # AC 모드는 ESP와 STM 모두 준비되어야 하고, AC 펌웨어가 존재해야 함
        self.smt_ac_mode_btn.setEnabled(esp_ready and ac_firmware_exists)
        
        # DC 모드는 DC 펌웨어가 존재해야 함
        self.smt_dc_mode_btn.setEnabled(dc_firmware_exists)

    def open_smt_ac_mode(self):
        """SMT AC 모드 창 열기"""
        try:
            # AC 모드로 강제 전환
            self.mode_toggle.setChecked(False)  # AC 모드는 체크 해제 상태
            self.mode_toggle.setText("AC")
            self.load_default_firmware("AC")
            
            # SMT 모드 창 열기
            self.smt_window = SMTModeWindow(
                esp_settings=self.esp_component.esp_controller.settings,
                stm_settings=self.stm_controller.settings,
                mode="AC"
            )
            self.smt_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open SMT AC Mode: {str(e)}")

    def open_smt_dc_mode(self):
        """SMT DC 모드 창 열기"""
        try:
            # DC 모드로 강제 전환
            self.mode_toggle.setChecked(True)  # DC 모드는 체크된 상태
            self.mode_toggle.setText("DC")
            self.load_default_firmware("DC")
            
            # SMT 모드 창 열기
            self.smt_window = SMTModeWindow(
                esp_settings=None,  # ESP 설정은 전달하지 않음
                stm_settings=self.stm_controller.settings,
                mode="DC"
            )
            self.smt_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open SMT DC Mode: {str(e)}")

    def update_firmware_label(self):
        """펌웨어 라벨 업데이트"""
        if self.stm_controller.settings.firmware_path:
            filename = os.path.basename(self.stm_controller.settings.firmware_path)
            self.firmware_label.setText(f"Selected: {filename}")
        else:
            self.firmware_label.setText("No file selected")

    def toggle_mode(self):
        """AC/DC 모드 토글"""
        if self.mode_toggle.isChecked():
            self.mode_toggle.setText("DC")
            self.load_default_firmware("DC")
        else:
            self.mode_toggle.setText("AC")
            self.load_default_firmware("AC")

    def load_default_firmware(self, mode):
        """모드에 따른 기본 펌웨어 파일 로드"""
        from pathlib import Path
        
        # 기본 펌웨어 경로 설정
        base_path = Path(__file__).parent.parent.parent / 'config' / 'stm' / mode
        firmware_file = f"stm32{mode}.bin"
        default_firmware = base_path / firmware_file
        
        # 디렉토리가 없으면 생성
        base_path.mkdir(parents=True, exist_ok=True)
        
        # 이전 경로의 파일 확인
        old_firmware = Path(__file__).parent.parent.parent / 'config' / 'stm' / 'stm32.bin'
        if old_firmware.exists() and not default_firmware.exists():
            # 새 경로로 파일 복사
            shutil.copy2(old_firmware, default_firmware)
            self.logger.info(f"Copied default firmware to {mode} mode: {default_firmware}")
        
        if default_firmware.exists():
            self.stm_controller.settings.firmware_path = str(default_firmware.absolute())
            self.update_firmware_label()
            self.logger.info(f"Loaded {mode} mode firmware: {default_firmware}")
        else:
            self.stm_controller.settings.firmware_path = None
            self.firmware_label.setText(f"Default {mode} firmware not found")
            self.logger.warning(f"Default {mode} firmware not found at {default_firmware}")
        
        # SMT 모드 버튼 상태 업데이트
        self.update_smt_button_state()
