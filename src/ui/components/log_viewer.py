from PyQt5.QtWidgets import (QWidget, QTextEdit, QVBoxLayout, 
                           QPushButton, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import datetime
import os

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
        self.log_dir = self._ensure_log_directory()
        self.initUI()

    def _ensure_log_directory(self):
        """로그 디렉토리 생성 및 경로 반환"""
        # 프로젝트 루트 디렉토리 기준으로 log 폴더 생성
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))), 'log')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir

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
        save_btn = QPushButton('전체 저장')
        save_selection_btn = QPushButton('선택 저장')
        self.auto_scroll_btn = QPushButton('자동 스크롤')
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        
        clear_btn.clicked.connect(self.clear_log)
        save_btn.clicked.connect(self.save_log)
        save_selection_btn.clicked.connect(self.save_selected_log)
        
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(save_selection_btn)
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
        """전체 로그 저장"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'log_{timestamp}.txt'
            filepath = os.path.join(self.log_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            
            QMessageBox.information(self, "저장 완료", 
                                  f"로그가 저장되었습니다.\n저장 위치: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "저장 실패", f"로그 저장 중 오류 발생: {str(e)}")

    def save_selected_log(self):
        """선택된 부분만 저장"""
        try:
            cursor = self.log_text.textCursor()
            if not cursor.hasSelection():
                QMessageBox.warning(self, "선택 없음", "저장할 텍스트를 선택해주세요.")
                return

            # 선택 시작과 끝 위치 가져오기
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            
            # 새로운 커서를 만들어 선택된 텍스트를 블록 단위로 가져오기
            doc = self.log_text.document()
            cursor_start = QTextCursor(doc)
            cursor_start.setPosition(start)
            cursor_end = QTextCursor(doc)
            cursor_end.setPosition(end)
            
            start_block = cursor_start.blockNumber()
            end_block = cursor_end.blockNumber()
            
            # 선택된 텍스트를 줄 단위로 수집
            selected_lines = []
            for i in range(start_block, end_block + 1):
                block = doc.findBlockByNumber(i)
                line = block.text()
                
                # 첫 번째 블록이고 부분 선택된 경우
                if i == start_block:
                    start_in_block = start - block.position()
                    line = line[start_in_block:]
                
                # 마지막 블록이고 부분 선택된 경우
                if i == end_block:
                    end_in_block = end - block.position()
                    line = line[:end_in_block]
                
                selected_lines.append(line)
            
            # 줄바꿈으로 연결
            selected_text = '\n'.join(selected_lines)
            
            if not selected_text.strip():
                QMessageBox.warning(self, "선택 없음", "저장할 텍스트를 선택해주세요.")
                return
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'log_partial_{timestamp}.txt'
            filepath = os.path.join(self.log_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(selected_text)
            
            QMessageBox.information(self, "저장 완료", 
                                  f"선택된 로그가 저장되었습니다.\n저장 위치: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "저장 실패", f"로그 저장 중 오류 발생: {str(e)}")
