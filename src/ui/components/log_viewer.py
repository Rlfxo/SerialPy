from PyQt5.QtWidgets import (QWidget, QTextEdit, QVBoxLayout, 
                           QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import datetime

class SerialReaderThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True

    def run(self):
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore')
                    if data:
                        self.data_received.emit(data)
            except Exception as e:
                print(f"Serial reading error: {str(e)}")
                break
            self.msleep(10)  # CPU 부하 감소

    def stop(self):
        self.running = False

class LogViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reader_thread = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 로그 표시 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)  # 자동 줄바꿈 비활성화
        
        # 모노스페이스 폰트 설정
        font = self.log_text.font()
        font.setFamily("Courier")
        self.log_text.setFont(font)
        
        layout.addWidget(self.log_text)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton('지우기')
        save_btn = QPushButton('저장')
        self.auto_scroll_btn = QPushButton('자동 스크롤')
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        
        clear_btn.clicked.connect(self.clear_log)
        save_btn.clicked.connect(self.save_log)
        
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(self.auto_scroll_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def start_monitoring(self, serial_port):
        """시리얼 모니터링 시작"""
        if self.reader_thread is not None:
            self.stop_monitoring()
        
        self.reader_thread = SerialReaderThread(serial_port)
        self.reader_thread.data_received.connect(self.append_log)
        self.reader_thread.start()

    def stop_monitoring(self):
        """시리얼 모니터링 중지"""
        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread.wait()
            self.reader_thread = None

    def append_log(self, text):
        """로그 추가"""
        timestamp = datetime.datetime.now().strftime('[%H:%M:%S.%f')[:-3] + '] '
        self.log_text.append(timestamp + text.strip())
        
        # 자동 스크롤이 활성화되어 있으면 스크롤
        if self.auto_scroll_btn.isChecked():
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """로그 지우기"""
        self.log_text.clear()

    def save_log(self):
        """로그 저장"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'log_{timestamp}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
        except Exception as e:
            print(f"로그 저장 실패: {str(e)}")
