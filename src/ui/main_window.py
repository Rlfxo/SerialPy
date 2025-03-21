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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = DownloadSettings()
        self.base_dir = FileUtils.get_project_root()
        self.img_dir = os.path.join(self.base_dir, 'img')
        self.nrf_window = None
        self.stm_window = None
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Firmware Download Tool')
        self.setFixedSize(*self.settings.window_size)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set gray background for the window
        self.setStyleSheet("QMainWindow { background-color: #E0E0E0; }")
        central_widget.setStyleSheet("QWidget { background-color: #E0E0E0; }")
        
        self._setup_title_image(central_widget)
        self._setup_buttons(central_widget)
        
        # Show window
        UIUtils.center_window(self)
        self.show()

    def _setup_title_image(self, central_widget):
        title_label = QLabel(central_widget)
        title_label.setAlignment(Qt.AlignCenter)
        
        img_path = os.path.join(self.img_dir, 'title.png')
        print(f"이미지 경로: {img_path}")
        
        if os.path.exists(img_path):
            title_pixmap = QPixmap(img_path)
            if not title_pixmap.isNull():
                scaled_pixmap = title_pixmap.scaled(500, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                title_label.setPixmap(scaled_pixmap)
                print("이미지 로딩 성공")
            else:
                self._set_default_title(title_label, img_path)
        else:
            self._set_default_title(title_label, img_path)
        
        title_label.setFixedSize(500, 90)
        title_label.move(10, 30)

    def _set_default_title(self, label, img_path):
        print(f"이미지 파일이 존재하지 않습니다: {img_path}")
        label.setText("EVAR")
        label.setStyleSheet("QLabel { color: black; font-size: 40px; font-weight: bold; }")

    def _setup_buttons(self, central_widget):
        # Create buttons with new labels
        nrf_board_btn = QPushButton('nRF52', central_widget)
        stm_board_btn = QPushButton('STM32', central_widget)
        exit_btn = QPushButton('종료', central_widget)
        
        # Set button sizes
        nrf_board_btn.setFixedSize(*self.settings.button_size)
        stm_board_btn.setFixedSize(*self.settings.button_size)
        exit_btn.setFixedSize(*self.settings.exit_button_size)
        
        # Set button positions
        nrf_board_btn.move(30, 160)
        stm_board_btn.move(280, 160)
        exit_btn.move(410, 390)
        
        # Set button styles
        nrf_board_btn.setStyleSheet(ButtonStyles.get_main_button_style(144, 238, 144))
        stm_board_btn.setStyleSheet(ButtonStyles.get_main_button_style(135, 206, 235))
        exit_btn.setStyleSheet(ButtonStyles.get_exit_button_style())
        
        # Set fonts
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        
        small_font = QFont()
        small_font.setPointSize(12)
        small_font.setBold(True)
        
        nrf_board_btn.setFont(font)
        stm_board_btn.setFont(font)
        exit_btn.setFont(small_font)
        
        # Connect signals
        nrf_board_btn.clicked.connect(self.on_nrf_board_clicked)
        stm_board_btn.clicked.connect(self.on_stm_board_clicked)
        exit_btn.clicked.connect(self.close)

    def on_nrf_board_clicked(self):
        if not self.nrf_window:
            self.nrf_window = NRFDownloadWindow()
        self.nrf_window.show()

    def on_stm_board_clicked(self):
        if not self.stm_window:
            self.stm_window = STMDownloadWindow()
        self.stm_window.show()
