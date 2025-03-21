from PyQt5.QtWidgets import (QWidget, QTextEdit, QVBoxLayout, 
                           QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt

class LogViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 로그 표시 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton('지우기')
        save_btn = QPushButton('저장')
        
        clear_btn.clicked.connect(self.clear_log)
        save_btn.clicked.connect(self.save_log)
        
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def append_log(self, text):
        """로그 추가"""
        self.log_text.append(text)

    def clear_log(self):
        """로그 지우기"""
        self.log_text.clear()

    def save_log(self):
        """로그 저장"""
        # TODO: 저장 기능 구현
        pass
