from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QProgressBar, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

class DownloadPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 파일 선택 영역
        file_layout = QHBoxLayout()
        self.file_label = QLabel("선택된 파일: 없음")
        select_file_btn = QPushButton("파일 선택")
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)

        # 진행 상태 표시
        self.status_label = QLabel("준비")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # 프로그레스 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        # 다운로드 버튼
        self.download_btn = QPushButton("다운로드")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)  # 파일 선택 전에는 비활성화
        layout.addWidget(self.download_btn)

        # 여백 추가
        layout.addStretch()

        # 스타일 설정
        self.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QLabel {
                font-size: 12px;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2980b9;
            }
        """)

    def select_file(self):
        """파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "다운로드 파일 선택",
            "",
            "Binary Files (*.bin);;All Files (*.*)"
        )
        
        if file_path:
            self.file_label.setText(f"선택된 파일: {file_path}")
            self.download_btn.setEnabled(True)

    def start_download(self):
        """다운로드 시작"""
        # TODO: 실제 다운로드 기능 구현
        QMessageBox.information(self, "알림", "다운로드 기능이 구현될 예정입니다.")

    def update_progress(self, value):
        """진행률 업데이트"""
        self.progress_bar.setValue(value)

    def update_status(self, status):
        """상태 메시지 업데이트"""
        self.status_label.setText(status)

    def download_completed(self):
        """다운로드 완료 처리"""
        self.status_label.setText("다운로드 완료")
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(100)

    def download_failed(self, error_message):
        """다운로드 실패 처리"""
        self.status_label.setText(f"다운로드 실패: {error_message}")
        self.download_btn.setEnabled(True) 