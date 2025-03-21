import os
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from .nrf_window import NRFDownloadWindow
from .stm_window import STMDownloadWindow
from .smt_mode_window import SMTModeWindow
from .styles.button_styles import ButtonStyles
from ..utils.ui_utils import UIUtils
from ..utils.file_utils import FileUtils
from ..models.download_settings import DownloadSettings
from .gui.qc_window import QCWindow
from .gui.oc_window import OCWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = DownloadSettings()
        
        # 윈도우 초기화
        self.qc_window = None
        self.oc_window = None
        
        # UI 설정
        self.setWindowTitle('SerialPy')
        self.setFixedSize(*self.settings.window_size)
        
        # 타이틀 이미지 추가
        title_label = QLabel(self)
        pixmap = QPixmap('assets/title.png')
        if not pixmap.isNull():
            title_label.setPixmap(pixmap)
            title_label.setAlignment(Qt.AlignCenter)
            # 이미지 위치 설정 (기존 값 사용)
            title_label.move(30, 30)
        else:
            print("Error: Could not load title.png")
        
        self._setup_buttons(self)
        UIUtils.center_window(self)
        self.show()

    def _setup_buttons(self, central_widget):
        # 기존 버튼 대신 QC/OC 버튼 생성
        qc_btn = QPushButton('QC', central_widget)
        oc_btn = QPushButton('OC', central_widget)
        exit_btn = QPushButton('종료', central_widget)
        
        # 버튼 크기 설정
        qc_btn.setFixedSize(*self.settings.button_size)
        oc_btn.setFixedSize(*self.settings.button_size)
        exit_btn.setFixedSize(*self.settings.exit_button_size)
        
        # 버튼 위치 설정 (기존과 동일)
        qc_btn.move(30, 160)
        oc_btn.move(280, 160)
        exit_btn.move(410, 390)
        
        # 버튼 스타일 설정
        qc_btn.setStyleSheet(ButtonStyles.get_main_button_style(144, 238, 144))  # 연두색
        oc_btn.setStyleSheet(ButtonStyles.get_main_button_style(135, 206, 235))  # 하늘색
        exit_btn.setStyleSheet(ButtonStyles.get_exit_button_style())
        
        # 폰트 설정
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        
        small_font = QFont()
        small_font.setPointSize(12)
        small_font.setBold(True)
        
        qc_btn.setFont(font)
        oc_btn.setFont(font)
        exit_btn.setFont(small_font)
        
        # 시그널 연결
        qc_btn.clicked.connect(self.on_qc_clicked)
        oc_btn.clicked.connect(self.on_oc_clicked)
        exit_btn.clicked.connect(self.close)

    def on_qc_clicked(self):
        if not self.qc_window:
            self.qc_window = QCWindow()
        self.qc_window.show()

    def on_oc_clicked(self):
        if not self.oc_window:
            self.oc_window = OCWindow()
        self.oc_window.show()
