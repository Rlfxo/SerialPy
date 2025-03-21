import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from src.ui.main_window import MainWindow

def check_openocd():
    try:
        subprocess.run(["openocd", "--version"], 
                     capture_output=True, 
                     text=True)
        return True
    except FileNotFoundError:
        msg = """
OpenOCD가 설치되어 있지 않습니다. 아래 방법으로 설치해주세요:

macOS:
    brew install open-ocd

Windows:
1. http://openocd.org/ 에서 다운로드
2. 시스템 PATH에 추가

Ubuntu/Debian:
    sudo apt-get install openocd
"""
        QMessageBox.warning(None, "OpenOCD 설치 필요", msg)
        return False

def main():
    # Windows에서 High DPI 스케일링 활성화
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Mac에서 IMKClient 로그 메시지 숨기기
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    
    app = QApplication(sys.argv)
    
    # Windows에서 기본 폰트 크기 조정
    if sys.platform == 'win32':
        font = app.font()
        font.setPointSize(9)  # Windows 기본 폰트 크기
        app.setFont(font)
    
    # OpenOCD 설치 확인
    if not check_openocd():
        sys.exit(1)
        
    ex = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
