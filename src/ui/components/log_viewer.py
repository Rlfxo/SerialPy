from PyQt5.QtWidgets import (QWidget, QTextEdit, QVBoxLayout, 
                           QPushButton, QHBoxLayout, QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QTextDocument
import datetime
import os
from PyQt5.QtWidgets import QApplication
import re
from PyQt5.QtWidgets import QScrollBar

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
        self.user_scrolling = False
        self.is_paused = False
        self.scroll_timer = None
        self.log_dir = self._ensure_log_directory()
        self.initUI()
        self.setup_scroll_handling()

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
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        
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
        self.pause_btn = QPushButton('일시정지')
        self.auto_scroll_btn = QPushButton('자동 스크롤')
        
        self.pause_btn.setCheckable(True)
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        
        clear_btn.clicked.connect(self.clear_log)
        save_btn.clicked.connect(self.save_log)
        save_selection_btn.clicked.connect(self.save_selected_log)
        self.pause_btn.clicked.connect(self.toggle_pause)
        
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(save_selection_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.auto_scroll_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 스팟 검색 UI 추가
        self.search_layout = QHBoxLayout()
        self.spot_edit = QLineEdit()
        self.spot_edit.setPlaceholderText("Spotlight 검색")
        self.search_layout.addWidget(self.spot_edit)
        layout.addLayout(self.search_layout)
        
        # 검색 타이머 설정 (성능 최적화)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.spot_edit.textChanged.connect(self.schedule_search)
        
        self.setLayout(layout)

    def setup_scroll_handling(self):
        """스크롤 이벤트 처리 설정"""
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.valueChanged.connect(self.on_scroll_value_changed)
        scrollbar.sliderPressed.connect(self.on_scroll_pressed)
        scrollbar.sliderReleased.connect(self.on_scroll_released)

    def on_scroll_pressed(self):
        """사용자가 스크롤바를 드래그하기 시작할 때"""
        self.user_scrolling = True

    def on_scroll_released(self):
        """사용자가 스크롤바 드래그를 멈출 때"""
        scrollbar = self.log_text.verticalScrollBar()
        # 스크롤바가 맨 아래에 있으면 자동 스크롤 재개
        if scrollbar.value() == scrollbar.maximum():
            self.user_scrolling = False

    def on_scroll_value_changed(self, value):
        """스크롤바 값이 변경될 때"""
        scrollbar = self.log_text.verticalScrollBar()
        # 맨 아래로 스크롤되면 자동 스크롤 재개
        if value == scrollbar.maximum():
            self.user_scrolling = False

    def start_monitoring(self, serial_port):
        """시리얼 모니터링 시작"""
        if self.reader_thread is not None:
            self.stop_monitoring()
        
        self.reader_thread = SerialReaderThread(serial_port)
        self.reader_thread.data_received.connect(self.process_log)
        self.reader_thread.start()

    def stop_monitoring(self):
        """시리얼 모니터링 중지"""
        if self.reader_thread is not None:
            self.reader_thread.stop()
            self.reader_thread.wait()  # 스레드가 완전히 종료될 때까지 대기
            self.reader_thread = None

    def process_log(self, text):
        """로그 텍스트 처리"""
        if self.is_paused:
            return  # 일시정지 상태면 로그 업데이트 하지 않음
            
        cursor = self.log_text.textCursor()
        had_selection = cursor.hasSelection()
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()
        
        # ANSI 이스케이프 코드 제거
        ansi_pattern = re.compile(r'\x1b\[\d+m')
        clean_text = ansi_pattern.sub('', text)
        
        # 현재 커서 위치 저장
        current_position = cursor.position()
        
        # 텍스트 끝으로 이동하여 추가
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(clean_text)
        
        # 선택 영역이 있었다면 복원
        if had_selection:
            cursor.setPosition(selection_start)
            cursor.setPosition(selection_end, QTextCursor.KeepAnchor)
            self.log_text.setTextCursor(cursor)
            self.user_scrolling = True
        
        # 자동 스크롤 처리
        if self.auto_scroll_btn.isChecked() and not self.user_scrolling:
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def append_log(self, text):
        """로그 추가"""
        self.process_log(text)

    def clear_log(self):
        """로그 지우기"""
        self.log_text.clear()
        self.user_scrolling = False  # 스크롤 상태 초기화

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

    def schedule_search(self):
        """검색 타이머 시작 (타이핑 중에는 검색하지 않음)"""
        self.search_timer.start(300)  # 300ms 후에 검색 시작
        
    def perform_search(self):
        """실제 검색 수행"""
        search_text = self.spot_edit.text()
        if not search_text:
            # 검색어가 없으면 하이라이트 제거
            cursor = self.log_text.textCursor()
            cursor.select(QTextCursor.Document)
            cursor.setCharFormat(QTextCharFormat())
            return
            
        try:
            cursor = self.log_text.textCursor()
            format = QTextCharFormat()
            format.setBackground(QColor("yellow"))
            format.setForeground(QColor("black"))  # 글자색을 검은색으로 설정
            
            # 이전 하이라이트 제거
            cursor.select(QTextCursor.Document)
            cursor.setCharFormat(QTextCharFormat())
            
            # 최근 1000줄만 검색 (성능 최적화)
            document = self.log_text.document()
            block_count = document.blockCount()
            start_block = max(0, block_count - 1000)
            
            finder = QTextDocument.FindFlags()
            pos = document.findBlockByNumber(start_block).position()
            
            while True:
                cursor = document.find(search_text, pos, finder)
                if cursor.isNull():
                    break
                    
                cursor.mergeCharFormat(format)
                pos = cursor.position()
                
                # UI 응답성을 위해 주기적으로 이벤트 처리
                QApplication.processEvents()
                
        except Exception as e:
            print(f"검색 중 오류 발생: {str(e)}")

    def toggle_pause(self):
        """로그 업데이트 일시정지/재개"""
        self.is_paused = self.pause_btn.isChecked()
        if self.is_paused:
            self.pause_btn.setText('재개')
        else:
            self.pause_btn.setText('일시정지')
