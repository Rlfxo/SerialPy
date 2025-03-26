from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QWidget, 
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QPushButton, QHBoxLayout, QFileDialog, QMessageBox,
                           QGroupBox, QGridLayout, QLabel, QLineEdit, QFrame,
                           QRadioButton, QComboBox)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
import hashlib
import binascii
from ..components.download_panel import DownloadPanel
import time

class HeaderManager:
    def __init__(self):
        self.HEADER_SIZE = 1024  # 헤더 전체 크기
        self.header_fields = {
            'sha256': {'size': 32, 'editable': False},
            'length': {'size': 4, 'editable': False},
            'model_name': {'size': 64, 'editable': True},
            'cpo_id': {'size': 32, 'editable': True},
            'version': {'size': 3, 'editable': True},
            'image_type': {'size': 1, 'editable': True},
            'dev_version': {'size': 16, 'editable': False},
            'debug_level': {'size': 1, 'editable': True}
        }

    def format_hex_value(self, value: bytes, field: str) -> str:
        """헥사값을 형식에 맞게 포맷팅"""
        if field in ['debug_level', 'image_type']:  # 1바이트 필드
            return f"0x{value.hex().upper():0>2}"  # 0x 형식으로 수정
        return value.hex().upper()

    def read_header(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                if len(file_data) < self.HEADER_SIZE:
                    raise Exception(f"파일이 너무 작습니다. (최소 {self.HEADER_SIZE} 바이트 필요)")

                header_info = {}
                offset = 0

                for field, config in self.header_fields.items():
                    size = config['size']
                    value = file_data[offset:offset + size]

                    if field == 'sha256':
                        header_info[field] = value.hex()
                    elif field == 'length':
                        header_info[field] = int.from_bytes(value, 'little')
                    elif field in ['model_name', 'cpo_id', 'dev_version']:
                        try:
                            header_info[field] = value.split(b'\x00')[0].decode('utf-8')
                        except:
                            header_info[field] = "N/A"
                    else:
                        # 1바이트 필드는 0x 형식으로 표시
                        header_info[field] = self.format_hex_value(value, field)

                    offset += size

                return header_info

        except Exception as e:
            raise Exception(f"헤더 읽기 실패: {str(e)}")

    def create_header(self, field_values):
        """새로운 헤더 생성"""
        header = bytearray(self.HEADER_SIZE)  # 전체 헤더를 0으로 초기화
        
        # SHA256 위치를 0으로 초기화 (32바이트)
        header[0:32] = bytes(32)
        
        # 나머지 헤더 필드 추가
        current_offset = 32
        for field, config in self.header_fields.items():
            if field == 'sha256':
                continue  # SHA256은 이미 추가됨
                
            size = config['size']
            value = field_values.get(field)
            
            try:
                if field == 'length':
                    # length는 정수를 bytes로 변환
                    header[current_offset:current_offset + size] = int(value).to_bytes(size, 'little')
                elif field == 'dev_version':
                    # dev_version은 16바이트 0으로 채움
                    header[current_offset:current_offset + size] = bytes(size)
                elif field in ['model_name', 'cpo_id']:
                    # 문자열 필드는 UTF-8로 인코딩하고 패딩
                    encoded = str(value).encode('utf-8')
                    header[current_offset:current_offset + size] = encoded.ljust(size, b'\x00')[:size]
                else:
                    # 0x 접두어가 있으면 제거
                    hex_value = value.replace('0x', '')
                    # 1바이트 필드는 항상 2자리 헥사값으로 처리
                    if field in ['debug_level', 'image_type']:
                        hex_value = hex_value.zfill(2)
                    header[current_offset:current_offset + size] = bytes.fromhex(hex_value)
                    
            except Exception as e:
                raise ValueError(f"필드 '{field}' 변환 실패: {str(e)}")
                
            current_offset += size
            
        return header

    def calculate_sha256(self, header, data):
        """SHA256 계산"""
        sha256 = hashlib.sha256()
        sha256.update(header)
        sha256.update(data)
        return sha256.digest()

    def update_header_with_sha256(self, header, digest):
        """헤더에 SHA256 digest 업데이트"""
        header[0:32] = digest
        return header

class QCManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header_manager = HeaderManager()
        self.setWindowTitle('Quality Control Management')
        self.setFixedSize(800, 650)

        # 메인 레이아웃
        layout = QVBoxLayout()
        
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        
        # 각 탭의 기본 위젯 생성
        self.header_tab = QWidget()
        self.device_tab = QWidget()
        self.download_tab = QWidget()
        
        # 각 탭 설정
        self._setup_header_tab()
        self._setup_device_tab()
        self._setup_download_tab()
        
        # 탭 추가
        self.tab_widget.addTab(self.header_tab, "Header")
        self.tab_widget.addTab(self.device_tab, "Device")
        self.tab_widget.addTab(self.download_tab, "Download")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
        # 포트 상태 업데이트
        self.update_port_status()

    def _setup_header_tab(self):
        """Header 탭 설정"""
        layout = QVBoxLayout(self.header_tab)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        load_button = QPushButton("파일 불러오기")
        self.save_button = QPushButton("파일 저장")  # 저장 버튼 추가
        self.save_button.setEnabled(False)  # 초기에는 비활성화
        
        load_button.clicked.connect(self.load_header_file)
        self.save_button.clicked.connect(self.save_header_file)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 헤더 정보 테이블
        self.header_table = QTableWidget()
        self.header_table.setColumnCount(4)
        self.header_table.setHorizontalHeaderLabels(["필드", "크기(bytes)", "수정가능", "값"])
        
        # 테이블 스타일 설정
        self.header_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.header_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        # 헤더 필드 정보 설정
        header_fields = {
            'sha256': {'size': 32, 'editable': False},
            'length': {'size': 4, 'editable': False},
            'model_name': {'size': 64, 'editable': True},
            'cpo_id': {'size': 32, 'editable': True},
            'version': {'size': 3, 'editable': True},
            'image_type': {'size': 1, 'editable': True},
            'dev_version': {'size': 16, 'editable': False},
            'debug_level': {'size': 1, 'editable': True}
        }
        
        # 테이블에 데이터 추가
        self.header_table.setRowCount(len(header_fields))
        for row, (field, info) in enumerate(header_fields.items()):
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
        
        layout.addWidget(self.header_table)

        # 테이블 값 변경 이벤트 연결
        self.header_table.itemChanged.connect(self.on_value_changed)
        
        self.current_file_path = None  # 현재 로드된 파일 경로 저장

    def on_value_changed(self, item):
        """테이블 값이 변경되었을 때 호출"""
        if item.column() == 3:  # 값 컬럼만 처리
            self.save_button.setEnabled(True)  # 저장 버튼 활성화

    def format_sha256(self, sha256_value):
        """SHA256 값을 0x로 시작하는 대문자 형식으로 변환"""
        return f"0x{sha256_value.upper()}"

    def load_header_file(self):
        """헤더 파일 불러오기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 파일 선택",
            "",
            "Image Files (*.img);;All Files (*.*)"
        )
        
        if file_path:
            try:
                self.current_file_path = file_path
                header_info = self.header_manager.read_header(file_path)
                
                # 테이블 업데이트
                for row in range(self.header_table.rowCount()):
                    field_name = self.header_table.item(row, 0).text()
                    value = header_info.get(field_name)
                    
                    if value is not None:
                        if field_name == 'length':
                            display_value = f"{value:,} bytes"
                        elif field_name == 'sha256':
                            display_value = self.format_sha256(value)
                        elif field_name in ['debug_level', 'image_type']:
                            # 1바이트 필드는 항상 0x00 형식으로 표시
                            display_value = value  # 이미 format_hex_value에서 처리됨
                        else:
                            display_value = str(value)
                            
                        self.header_table.item(row, 3).setText(display_value)
                
                self.save_button.setEnabled(False)  # 초기 로드 시에는 저장 버튼 비활성화
                QMessageBox.information(self, "성공", "파일을 성공적으로 불러왔습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일 로드 중 오류 발생: {str(e)}")

    def save_header_file(self):
        """헤더 정보를 파일에 저장"""
        if not self.current_file_path:
            return
            
        try:
            # 현재 테이블의 값들을 수집
            field_values = {}
            for row in range(self.header_table.rowCount()):
                field_name = self.header_table.item(row, 0).text()
                value = self.header_table.item(row, 3).text()
                
                # 특별한 형식의 값들을 원래 형식으로 변환
                if field_name == 'length':
                    value = int(value.split()[0].replace(',', ''))
                elif field_name == 'sha256':
                    value = value[2:]  # '0x' 제거
                
                field_values[field_name] = value

            # 새 헤더 생성
            new_header = self.header_manager.create_header(field_values)
            
            # 파일 데이터 읽기
            with open(self.current_file_path, 'rb') as f:
                f.seek(self.header_manager.HEADER_SIZE)
                file_data = f.read()

            # SHA256 계산 및 업데이트
            sha256_digest = self.header_manager.calculate_sha256(new_header, file_data)
            new_header = self.header_manager.update_header_with_sha256(new_header, sha256_digest)
            
            # SHA256 표시 업데이트
            sha256_item = None
            for row in range(self.header_table.rowCount()):
                if self.header_table.item(row, 0).text() == 'sha256':
                    sha256_item = self.header_table.item(row, 3)
                    break
            
            if sha256_item:
                sha256_item.setText(self.format_sha256(sha256_digest.hex()))

            # 파일에 저장
            with open(self.current_file_path, 'r+b') as f:
                f.write(new_header)

            self.save_button.setEnabled(False)
            QMessageBox.information(self, "성공", "파일이 성공적으로 저장되었습니다.")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 저장 중 오류 발생: {str(e)}")

    def _setup_device_tab(self):
        """Device 탭 설정"""
        layout = QVBoxLayout(self.device_tab)
        
        # 포트 상태 표시 그룹
        port_status_group = QGroupBox("포트 상태")
        port_status_layout = QGridLayout()

        # 포트 상태 레이블 생성
        self.port1_status = QLabel("미연결")
        self.port2_status = QLabel("미연결")
        self.port1_status.setStyleSheet("color: red")
        self.port2_status.setStyleSheet("color: red")

        # 포트 선택 라디오 버튼
        self.port1_radio = QRadioButton("Monitor 1")
        self.port2_radio = QRadioButton("Monitor 2")
        self.port1_radio.setChecked(True)  # 기본값 Monitor 1 선택

        # 포트 상태 레이아웃 구성
        port_status_layout.addWidget(self.port1_radio, 0, 0)
        port_status_layout.addWidget(self.port1_status, 0, 1)
        port_status_layout.addWidget(self.port2_radio, 1, 0)
        port_status_layout.addWidget(self.port2_status, 1, 1)

        port_status_group.setLayout(port_status_layout)
        layout.addWidget(port_status_group)

        # 기본 정보 입력 그룹
        info_group = QGroupBox("모델 정보")
        info_layout = QGridLayout()

        # 모델명 입력
        self.model_name_input = QLineEdit()
        info_layout.addWidget(QLabel("모델명:"), 0, 0)
        info_layout.addWidget(self.model_name_input, 0, 1)

        # 시리얼 번호 입력
        self.serial_number_input = QLineEdit()
        info_layout.addWidget(QLabel("시리얼 번호:"), 1, 0)
        info_layout.addWidget(self.serial_number_input, 1, 1)

        # 읽기/쓰기 버튼
        read_btn = QPushButton("정보 읽기")
        write_btn = QPushButton("정보 쓰기")
        read_btn.clicked.connect(self.read_model_info)
        write_btn.clicked.connect(self.write_model_info)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(read_btn)
        btn_layout.addWidget(write_btn)
        info_layout.addLayout(btn_layout, 2, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 빠른 쓰기 그룹
        quick_write_group = QGroupBox("빠른 정보 쓰기")
        quick_write_layout = QGridLayout()

        # 모델명 콤보박스
        self.model_combo = QComboBox()
        model_list = [
            "E01AS007K10KR0101",
            "E01AS011K10KR0101",
            "E01DM050K10KR0102"
        ]
        self.model_combo.addItems(model_list)
        quick_write_layout.addWidget(QLabel("모델명:"), 0, 0)
        quick_write_layout.addWidget(self.model_combo, 0, 1, 1, 2)

        # 시리얼 번호 구성 요소들
        serial_layout = QHBoxLayout()
        
        # 시리얼 접두어 콤보박스
        self.serial_prefix_combo = QComboBox()
        serial_prefix_list = ["EVSCA", "EVSCB", "EVSCC", "EVSCD"]
        self.serial_prefix_combo.addItems(serial_prefix_list)
        
        # 시리얼 번호 입력 필드
        self.serial_number_edit = QLineEdit()
        self.serial_number_edit.setPlaceholderText("숫자 6자리")
        self.serial_number_edit.setMaxLength(6)
        self.serial_number_edit.setValidator(QIntValidator(0, 999999))

        serial_layout.addWidget(self.serial_prefix_combo)
        serial_layout.addWidget(self.serial_number_edit)

        quick_write_layout.addWidget(QLabel("시리얼 번호:"), 1, 0)
        quick_write_layout.addLayout(serial_layout, 1, 1, 1, 2)

        # 빠른 쓰기 버튼
        quick_write_btn = QPushButton("빠른 쓰기")
        quick_write_btn.clicked.connect(self.quick_write_model_info)
        quick_write_layout.addWidget(quick_write_btn, 2, 1)

        quick_write_group.setLayout(quick_write_layout)
        layout.addWidget(quick_write_group)

    def _setup_download_tab(self):
        """Download 탭 설정"""
        layout = QVBoxLayout(self.download_tab)
        
        # 다운로드 패널 추가
        self.download_panel = DownloadPanel()
        layout.addWidget(self.download_panel)
        
        # 여백 추가
        layout.addStretch()

    def update_port_status(self):
        """포트 연결 상태 업데이트"""
        # QCWindow의 포트 상태 확인
        if hasattr(self.parent(), 'left_port_selector'):
            port_selector = self.parent().left_port_selector
            is_connected = port_selector.is_connected
            port_name = port_selector.port_combo.currentText() if is_connected else ""
            
            status_text = f"{port_name} 연결됨" if is_connected else "미연결"
            self.port1_status.setText(status_text)
            self.port1_status.setStyleSheet("color: green" if is_connected else "color: red")
        
        if hasattr(self.parent(), 'right_port_selector'):
            port_selector = self.parent().right_port_selector
            is_connected = port_selector.is_connected
            port_name = port_selector.port_combo.currentText() if is_connected else ""
            
            status_text = f"{port_name} 연결됨" if is_connected else "미연결"
            self.port2_status.setText(status_text)
            self.port2_status.setStyleSheet("color: green" if is_connected else "color: red")

    def read_model_info(self):
        """모델 정보 읽기"""
        if not self._check_selected_port_connected():
            return

        try:
            # 선택된 포트의 SerialPort 객체 가져오기
            serial_port = self._get_selected_serial_port()
            if not serial_port:
                return

            # 명령어 전송
            command = "db r model\r\n"
            serial_port.write(command.encode())

            # 응답 읽기
            response = ""
            while True:
                if serial_port.in_waiting:
                    line = serial_port.readline().decode('utf-8', errors='ignore')
                    response += line
                    
                    # 응답이 완료되었는지 확인
                    if "serial_number =" in line:
                        break

            # 응답 파싱
            model_name = ""
            serial_number = ""
            
            for line in response.split('\n'):
                line = line.strip()
                if "model_name" in line:
                    model_name = line.split('=')[1].strip()
                elif "serial_number" in line:
                    serial_number = line.split('=')[1].strip()

            # UI 업데이트
            self.model_name_input.setText(model_name)
            self.serial_number_input.setText(serial_number)

        except Exception as e:
            QMessageBox.critical(self, "오류", f"모델 정보 읽기 실패: {str(e)}")

    def _get_selected_serial_port(self):
        """선택된 포트의 SerialPort 객체 반환"""
        parent = self.parent()
        if self.port1_radio.isChecked():
            if hasattr(parent, 'left_port_selector'):
                return parent.left_port_selector.serial_port
        else:
            if hasattr(parent, 'right_port_selector'):
                return parent.right_port_selector.serial_port
        
        QMessageBox.warning(self, "경고", "선택된 포트를 찾을 수 없습니다.")
        return None

    def _format_response_text(self, text):
        """응답 텍스트 포맷팅"""
        formatted = ""
        for line in text.split('\n'):
            line = line.strip()
            if line:
                if '=' in line:
                    key, value = line.split('=', 1)
                    formatted += f"{key.strip():15} = {value.strip()}\n"
                else:
                    formatted += line + '\n'
        return formatted.strip()

    def _write_serial_with_delay(self, serial_port, command, char_delay=0.001):
        """글자 단위로 딜레이를 주면서 시리얼 데이터 전송"""
        try:
            for char in command:
                serial_port.write(char.encode('utf-8'))
                serial_port.flush()
                time.sleep(char_delay)  # 각 글자 사이에 1ms 딜레이
        except Exception as e:
            print(f"시리얼 전송 오류: {str(e)}")
            raise e

    def write_model_info(self):
        """일반 모델 정보 쓰기"""
        if not self._check_selected_port_connected():
            QMessageBox.warning(self, "경고", "선택된 포트가 연결되어 있지 않습니다.")
            return

        try:
            model_name = self.model_name_input.text().strip()
            serial_number = self.serial_number_input.text().strip()

            if not model_name or not serial_number:
                QMessageBox.warning(self, "경고", "모델명과 시리얼 번호를 모두 입력해주세요.")
                return

            command = f"db w model 1 {model_name} {serial_number}\r\n"
            print(f"전송 명령어: [{command.strip()}]")
            
            serial_port = self._get_selected_serial_port()
            self._write_serial_with_delay(serial_port, command)
            
            time.sleep(0.1)
            
            QMessageBox.information(self, "성공", "모델 정보가 성공적으로 저장되었습니다.")
            self.read_model_info()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"모델 정보 저장 중 오류가 발생했습니다: {str(e)}")

    def _check_selected_port_connected(self):
        """선택된 포트의 연결 상태 확인"""
        if self.port1_radio.isChecked():
            if self.port1_status.text() == "미연결":
                QMessageBox.warning(self, "경고", "Monitor 1이 연결되지 않았습니다.")
                return False
        else:
            if self.port2_status.text() == "미연결":
                QMessageBox.warning(self, "경고", "Monitor 2가 연결되지 않았습니다.")
                return False
        return True

    def quick_write_model_info(self):
        """빠른 정보 쓰기 실행"""
        if not self._check_selected_port_connected():
            QMessageBox.warning(self, "경고", "선택된 포트가 연결되어 있지 않습니다.")
            return

        try:
            model_name = self.model_combo.currentText()
            serial_prefix = self.serial_prefix_combo.currentText()
            serial_number = self.serial_number_edit.text().strip()

            if not serial_number:
                QMessageBox.warning(self, "경고", "시리얼 번호를 입력해주세요.")
                return

            serial_number = serial_number.zfill(6)
            full_serial = f"{serial_prefix}{serial_number}"

            command = f"db w model 1 {model_name} {full_serial}\r\n"
            print(f"전송 명령어: [{command.strip()}]")
            
            serial_port = self._get_selected_serial_port()
            self._write_serial_with_delay(serial_port, command)
            
            time.sleep(0.1)
            
            QMessageBox.information(self, "성공", "모델 정보가 성공적으로 저장되었습니다.")
            self.read_model_info()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"모델 정보 저장 중 오류가 발생했습니다: {str(e)}")

    def show_device_tab(self):
        """Device 탭으로 전환"""
        self.tab_widget.setCurrentIndex(1) 