from PyQt5.QtWidgets import (QWidget, QProgressBar, QVBoxLayout, QLabel)
from PyQt5.QtCore import Qt

class EnhancedProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 상태 레이블
        self.status_label = QLabel('준비')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 프로그레스 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)

    def set_progress(self, value):
        """진행률 설정"""
        self.progress_bar.setValue(value)

    def set_status(self, text):
        """상태 텍스트 설정"""
        self.status_label.setText(text)
