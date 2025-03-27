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
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = DownloadSettings()
        
        # 윈도우 초기화
        self.qc_window = None
        self.oc_window = None
        
        # UI 설정
        self.setWindowTitle('SerialPy')
        self.resize(900, 800)  # 윈도우 크기 설정
        self.setMinimumSize(900, 800)  # 최소 크기 설정
        
        # 타이틀 이미지 로드
        self._setup_title_image()
        self._setup_buttons(self)
        
        # 윈도우 중앙 정렬
        UIUtils.center_window(self)
        self.show()

    def _setup_title_image(self):
        """타이틀 이미지 설정"""
        title_label = QLabel(self)
        
        # 프로젝트 루트 디렉토리 기준으로 이미지 경로 설정
        root_dir = Path(__file__).parent.parent.parent
        image_path = os.path.join(root_dir, 'img', 'title.png')
        
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            print(f"Original image size: {pixmap.width()} x {pixmap.height()}")
            
            # 레이블 크기 설정 (원하는 표시 크기)
            desired_width = 450
            desired_height = 100
            title_label.setFixedSize(desired_width, desired_height)
            
            # 이미지를 레이블 크기에 맞게 스케일링
            scaled_pixmap = pixmap.scaled(desired_width, desired_height, 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            
            # 레이블에 이미지 설정
            title_label.setPixmap(scaled_pixmap)
            title_label.setScaledContents(True)  # 레이블 크기에 맞게 이미지 조정
            title_label.setAlignment(Qt.AlignCenter)
            
            # 윈도우 중앙에 이미지 배치
            x_position = (self.width() - desired_width) // 2
            title_label.move(x_position, 100)
            
            print(f"Scaled image size: {scaled_pixmap.width()} x {scaled_pixmap.height()}")
            print(f"Label size: {title_label.width()} x {title_label.height()}")
            print(f"Image position: ({x_position}, 30)")
        else:
            print(f"Error: Could not load title image from {image_path}")
            print(f"Image path exists: {os.path.exists(image_path)}")

    def _setup_buttons(self, central_widget):
        # 버튼 생성
        oc_btn = QPushButton(central_widget)
        qc_btn = QPushButton(central_widget)
        exit_btn = QPushButton('종료', central_widget)
        
        # 버튼 크기 설정
        button_size = (300, 300)
        oc_btn.setFixedSize(*button_size)
        qc_btn.setFixedSize(*button_size)
        exit_btn.setFixedSize(100, 40)
        
        # 버튼 위치 설정
        oc_btn.move(100, 350)
        qc_btn.move(500, 350)
        exit_btn.move(780, 730)

        # 버튼 스타일 설정
        button_style_oc = f"""
            QPushButton {{
                background-color: rgb(135, 206, 235);
                border: none;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: rgb(155, 226, 255);
            }}
            QPushButton:pressed {{
                background-color: rgb(115, 186, 215);
            }}
            QPushButton QLabel {{
                background: transparent;
                width: 100%;
                height: 100%;
            }}
        """

        button_style_qc = f"""
            QPushButton {{
                background-color: rgb(144, 238, 144);
                border: none;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: rgb(164, 255, 164);
            }}
            QPushButton:pressed {{
                background-color: rgb(124, 218, 124);
            }}
            QPushButton QLabel {{
                background: transparent;
                width: 100%;
                height: 100%;
            }}
        """

        # 버튼 텍스트 설정 (QLabel 사용)
        oc_text = QLabel(oc_btn)
        oc_text.setAlignment(Qt.AlignCenter)
        oc_text.setText("""
            <div style='text-align: center;'>
                <div style='font-size: 60pt; font-weight: bold; color: black;'>OC</div>
                <div style='font-size: 20pt; color: black;'>Operation Center</div>
            </div>
        """)
        oc_text.setGeometry(0, 0, button_size[0], button_size[1])
        oc_text.setAttribute(Qt.WA_TransparentForMouseEvents)  # 마우스 이벤트를 버튼으로 전달

        qc_text = QLabel(qc_btn)
        qc_text.setAlignment(Qt.AlignCenter)
        qc_text.setText("""
            <div style='text-align: center;'>
                <div style='font-size: 60pt; font-weight: bold; color: black;'>QC</div>
                <div style='font-size: 20pt; color: black;'>Quality Center</div>
            </div>
        """)
        qc_text.setGeometry(0, 0, button_size[0], button_size[1])
        qc_text.setAttribute(Qt.WA_TransparentForMouseEvents)  # 마우스 이벤트를 버튼으로 전달

        # 스타일 적용
        oc_btn.setStyleSheet(button_style_oc)
        qc_btn.setStyleSheet(button_style_qc)
        exit_btn.setStyleSheet(ButtonStyles.get_exit_button_style())

        # 종료 버튼 폰트 설정
        small_font = QFont()
        small_font.setPointSize(14)
        small_font.setBold(True)
        exit_btn.setFont(small_font)
        
        # 시그널 연결
        oc_btn.clicked.connect(self.on_oc_clicked)
        qc_btn.clicked.connect(self.on_qc_clicked)
        exit_btn.clicked.connect(self.close)

    def on_qc_clicked(self):
        if not self.qc_window:
            self.qc_window = QCWindow()
        self.qc_window.show()

    def on_oc_clicked(self):
        if not self.oc_window:
            self.oc_window = OCWindow()
        self.oc_window.show()
