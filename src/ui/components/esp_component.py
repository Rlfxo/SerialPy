import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QFileDialog, 
                           QProgressBar, QVBoxLayout, QHBoxLayout, 
                           QGridLayout, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
import serial.tools.list_ports
from ...controllers.esp_controller import ESPController, DownloadThread
from ..styles.button_styles import ButtonStyles
import subprocess
import sys

class ESPDownloadComponent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.esp_controller = ESPController()
        
        # UI 요소 초기화
        self.download_btn = None
        self.port_combo = None
        self.bootloader_label = None
        self.partition_label = None
        self.ota_label = None
        self.app_label = None
        self.progress_bar = None
        self.status_label = None
        
        # 기본 파일 경로 설정
        self.default_files = {
            'bootloader': 'config/esp/bootloader.bin',
            'partition': 'config/esp/partition-table.bin',
            'ota': 'config/esp/ota_data_initial.bin'
        }
        
        # UI 설정 전에 기본 파일 로드
        self.load_default_files()
        
        # UI 설정
        self.initUI()

    def load_default_files(self):
        """기본 ESP 파일들을 로드"""
        try:
            # 현재 실행 경로 확인
            current_path = os.getcwd()
            print(f"Current working directory: {current_path}")
            
            # 프로젝트 루트 경로 찾기 (여러 방법 시도)
            base_paths = [
                current_path,  # 현재 실행 경로
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  # src의 상위
                os.path.join(current_path, 'DownloadPy')  # 프로젝트 폴더명으로 시도
            ]
            
            # 각 기본 파일 검색
            for base_path in base_paths:
                print(f"\nTrying base path: {base_path}")
                found_files = False
                
                for file_type, relative_path in self.default_files.items():
                    full_path = os.path.join(base_path, relative_path)
                    print(f"Checking {file_type} file: {full_path}")
                    
                    if os.path.exists(full_path):
                        print(f"Found {file_type} file: {full_path}")
                        setattr(self.esp_controller.settings, f'{file_type}_path', full_path)
                        found_files = True
                    else:
                        print(f"Not found: {full_path}")
                        
                if found_files:
                    print(f"Using base path: {base_path}")
                    break
                
            # 설정된 파일 경로 출력
            print("\nFinal file paths:")
            for file_type in self.default_files.keys():
                path = getattr(self.esp_controller.settings, f'{file_type}_path', None)
                print(f"{file_type}: {path}")
                
        except Exception as e:
            print(f"Error loading default files: {str(e)}")
            import traceback
            traceback.print_exc()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # ESP32 Section Title
        esp_title = QLabel("ESP32 Firmware")
        esp_title.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        layout.addWidget(esp_title)
        
        # 파일 선택 섹션
        self._setup_file_selection(layout)
        
        # 포트 선택 섹션
        self._setup_port_section(layout)
        
        # 다운로드 섹션
        self._setup_download_section(layout)
        
        # 초기 상태 설정
        self.update_download_button()

    def _setup_file_selection(self, layout):
        """파일 선택 UI 설정"""
        file_group = QGridLayout()
        
        # 각 파일 선택 행 생성 및 설정
        for row, (file_type, title) in enumerate([
            ('bootloader', 'Bootloader:'),
            ('partition', 'Partition Table:'),
            ('ota', 'OTA Data:'),
            ('app', 'Application:')
        ]):
            label = QLabel(title)
            file_label = QLabel('No file selected')
            setattr(self, f'{file_type}_label', file_label)
            
            # 기본 파일이 로드되었는지 확인
            if hasattr(self.esp_controller.settings, f'{file_type}_path'):
                path = getattr(self.esp_controller.settings, f'{file_type}_path')
                if path:
                    file_label.setText(f"Selected: {os.path.basename(path)}")
            
            select_btn = QPushButton('Select File')
            select_btn.clicked.connect(lambda checked, ft=file_type: self.select_file(ft))
            
            file_group.addWidget(label, row, 0)
            file_group.addWidget(file_label, row, 1)
            file_group.addWidget(select_btn, row, 2)
        
        layout.addLayout(file_group)

    def _setup_port_section(self, layout):
        """포트 선택 UI 설정"""
        port_section = QHBoxLayout()
        port_group = QHBoxLayout()
        
        port_label = QLabel('Select Port:')
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(250)
        self.port_combo.setMaximumWidth(400)
        
        # 포트 변경 이벤트 연결 수정
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

    def _setup_download_section(self, layout):
        """다운로드 섹션 UI 설정"""
        download_group = QVBoxLayout()
        
        # 상태 라벨
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        download_group.addWidget(self.status_label)
        
        # 프로그레스 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)  # nRF와 동일한 정렬
        self.progress_bar.setTextVisible(True)
        download_group.addWidget(self.progress_bar)
        
        # 다운로드 버튼
        self.download_btn = QPushButton("Download ESP32 Firmware")  # 버튼 텍스트 통일
        self.download_btn.setStyleSheet(ButtonStyles.DOWNLOAD_STYLE)  # nRF와 동일한 스타일
        self.download_btn.clicked.connect(self.start_download)
        download_group.addWidget(self.download_btn)
        
        layout.addLayout(download_group)

    def select_file(self, file_type):
        """파일 선택 처리"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            f"Select {file_type.title()} File",
            "",
            "Binary Files (*.bin);;All Files (*.*)"
        )
        
        if file_path:
            # 파일 타입에 따라 올바른 속성 이름 사용
            attr_name = {
                'bootloader': 'bootloader_path',
                'partition': 'partition_path',
                'ota': 'ota_path',
                'app': 'app_path'
            }.get(file_type)
            
            if attr_name:
                setattr(self.esp_controller.settings, attr_name, file_path)
                self.update_file_label(file_type, file_path)
                self.update_download_button()

    def update_file_label(self, file_type, file_path):
        """파일 라벨 업데이트"""
        label_map = {
            'bootloader': self.bootloader_label,
            'partition': self.partition_label,
            'ota': self.ota_label,
            'app': self.app_label
        }
        
        if label_map[file_type]:
            if file_path:
                label_map[file_type].setText(f"Selected: {os.path.basename(file_path)}")
            else:
                label_map[file_type].setText("No file selected")

    def get_serial_ports(self):
        """시리얼 포트 목록 반환"""
        try:
            ports = list(serial.tools.list_ports.comports())
            print(f"ESP: Found {len(ports)} ports:")
            for port in ports:
                print(f"- {port.device} ({port.description})")
            
            return sorted([p.device for p in ports], 
                        key=lambda x: (not x.startswith('/dev/cu.'), x))
        except Exception as e:
            print(f"ESP: Error scanning ports: {str(e)}")
            return []

    def refresh_ports(self):
        """포트 목록 새로고침"""
        if not hasattr(self, 'port_combo'):
            return
            
        try:
            current_port = self.port_combo.currentText()
            self.port_combo.clear()
            
            available_ports = self.get_serial_ports()
            print(f"ESP: Available ports: {available_ports}")
            
            if available_ports:
                self.port_combo.addItems(available_ports)
                
                # 우선순위에 따라 포트 자동 선택
                preferred_port = None
                
                # Mac에서 cu.usbserial로 시작하는 포트 우선 선택
                if sys.platform == 'darwin':  # Mac OS
                    for port in available_ports:
                        if '/dev/cu.usbserial' in port:
                            preferred_port = port
                            break
                
                # 이전에 선택한 포트가 있고 여전히 사용 가능하면 그 포트 선택
                if current_port in available_ports:
                    index = self.port_combo.findText(current_port)
                    self.port_combo.setCurrentIndex(index)
                # 우선 선택 포트가 있으면 그 포트 선택
                elif preferred_port:
                    index = self.port_combo.findText(preferred_port)
                    self.port_combo.setCurrentIndex(index)
                    # 선택된 포트 이벤트 발생
                    self.on_port_changed(preferred_port)
                else:
                    self.port_combo.setCurrentIndex(0)
                    # 첫 번째 포트 선택 시 이벤트 발생
                    self.on_port_changed(self.port_combo.currentText())
            else:
                self.port_combo.addItem("No ports available")
                self.on_port_changed("No ports available")
                
        except Exception as e:
            error_msg = f"Error refreshing ports: {str(e)}"
            print(f"ESP: {error_msg}")
            self.port_combo.addItem(error_msg)
            self.on_port_changed(error_msg)
        
        self.update_download_button()

    def on_port_changed(self, port):
        """포트 선택 변경 시 호출되는 메서드"""
        print(f"ESP: Selected port: {port}")
        if port and not port.startswith("No ports") and not port.startswith("Error"):
            self.esp_controller.settings.port = port
        else:
            self.esp_controller.settings.port = None
        
        # 다운로드 버튼 상태 업데이트
        self.update_download_button()

    def update_download_button(self):
        """다운로드 버튼 상태 업데이트"""
        if not hasattr(self, 'download_btn') or self.download_btn is None:
            return
            
        # 각 파일의 실제 존재 여부 확인
        files_exist = all(
            hasattr(self.esp_controller.settings, f'{ft}_path') and
            getattr(self.esp_controller.settings, f'{ft}_path') and
            os.path.exists(getattr(self.esp_controller.settings, f'{ft}_path'))
            for ft in ['bootloader', 'partition', 'ota', 'app']
        )
        
        # 파일이 존재하지 않으면 해당 설정 초기화
        for ft in ['bootloader', 'partition', 'ota', 'app']:
            path = getattr(self.esp_controller.settings, f'{ft}_path', None)
            if path and not os.path.exists(path):
                setattr(self.esp_controller.settings, f'{ft}_path', None)
                label = getattr(self, f'{ft}_label', None)
                if label:
                    label.setText("No file selected")
        
        # 포트 선택 상태 확인
        port_selected = bool(self.port_combo and 
                            self.port_combo.currentText() and 
                            self.port_combo.currentText() != "No ports available" and
                            not self.port_combo.currentText().startswith("Error:"))
        
        print(f"ESP Button state - Port selected: {port_selected} "
              f"({self.esp_controller.settings.port if port_selected else 'None'}), "
              f"Files exist: {files_exist}")
        
        # 모든 조건이 충족될 때만 버튼 활성화
        self.download_btn.setEnabled(files_exist and port_selected)

    def update_progress(self, value):
        if self.progress_bar:
            self.progress_bar.setValue(value)

    def start_download(self):
        if not self.esp_controller.check_esptool_installed():
            reply = QMessageBox.question(
                self,
                "esptool Not Found",
                "esptool is required but not installed.\nWould you like to install it now?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "esptool"])
                    QMessageBox.information(self, "Success", "esptool has been installed successfully.\nPlease try downloading again.")
                    return
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(self, "Error", f"Failed to install esptool: {str(e)}")
                    return
            else:
                return

        if not self.validate_download():
            return
        
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.download_thread = DownloadThread(self.esp_controller.settings)
        self.download_thread.progress_updated.connect(self._update_progress)
        self.download_thread.status_updated.connect(self._update_status)
        self.download_thread.download_completed.connect(self._download_finished)
        self.download_thread.start()

    def _update_progress(self, value):
        self.progress_bar.setValue(value)

    def _update_status(self, status):
        self.status_label.setText(status)

    def _download_finished(self, success):
        self.download_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", "Firmware download completed")
        else:
            QMessageBox.critical(self, "Error", "Firmware download failed")

    def get_download_status(self):
        """ESP 다운로드 상태 반환"""
        files_selected = all(
            hasattr(self.esp_controller.settings, f'{ft}_path') 
            for ft in ['bootloader', 'partition', 'ota', 'app']
        )
        port_selected = self.port_combo and self.port_combo.currentText() != ''
        return {
            'files_selected': files_selected,
            'port_selected': port_selected
        }

    def validate_download(self):
        if not self.esp_controller.settings.port:
            print("Error: No port selected")
            return False
        return True
