from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QPushButton, QWidget, 
                           QProgressBar, QLabel, QHBoxLayout, QMessageBox,
                           QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMetaObject, Q_ARG
from ..controllers.esp_controller import DownloadThread as ESPDownloadThread
from ..models.esp_settings import ESPSettings
from ..models.stm_settings import STMSettings
import time
import sys
import subprocess
import os

class SMTModeWindow(QMainWindow):
    def __init__(self, esp_settings=None, stm_settings=None, mode="AC", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.esp_settings = esp_settings
        self.stm_settings = stm_settings
        self.download_in_progress = False
        self.initUI()
        
    def initUI(self):
        # 창 설정
        self.setWindowTitle(f"{self.mode} Production Mode")
        self.setMinimumSize(600, 400)
        
        # 중앙 위젯 및 레이아웃
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # 제목
        title_label = QLabel(f"{self.mode} Production Mode")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # 다운로드 버튼
        self.download_btn = QPushButton("DOWNLOAD")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 20px;
                font-size: 24px;
                font-weight: bold;
                border-radius: 10px;
                min-height: 100px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.download_btn.clicked.connect(self.start_download_sequence)
        main_layout.addWidget(self.download_btn)
        
        # 상태 레이블
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; margin: 10px 0;")
        main_layout.addWidget(self.status_label)
        
        # 프로그레스 바 영역
        progress_layout = QVBoxLayout()
        
        if self.mode == "AC":
            # ESP32 프로그레스 바 (AC 모드에서만)
            esp_layout = QHBoxLayout()
            esp_label = QLabel("ESP32:")
            esp_label.setFixedWidth(80)
            self.esp_progress = QProgressBar()
            self.esp_progress.setTextVisible(True)
            esp_layout.addWidget(esp_label)
            esp_layout.addWidget(self.esp_progress)
            progress_layout.addLayout(esp_layout)
        
        # STM32 프로그레스 바 (AC/DC 모드 모두)
        stm_layout = QHBoxLayout()
        stm_label = QLabel("STM32:")
        stm_label.setFixedWidth(80)
        self.stm_progress = QProgressBar()
        self.stm_progress.setTextVisible(True)
        stm_layout.addWidget(stm_label)
        stm_layout.addWidget(self.stm_progress)
        progress_layout.addLayout(stm_layout)
        
        main_layout.addLayout(progress_layout)
        
        # 하단 여백
        main_layout.addStretch()
        
        # 초기 상태 설정
        if self.mode == "AC":
            self.esp_progress.setValue(0)
        self.stm_progress.setValue(0)
    
    def start_download_sequence(self):
        """ESP32와 STM32 다운로드 순차 실행"""
        if self.download_in_progress:
            return
            
        self.download_in_progress = True
        self.download_btn.setEnabled(False)
        self.status_label.setText("Starting download sequence...")
        
        if self.mode == "AC":
            self.esp_progress.setValue(0)
        self.stm_progress.setValue(0)
        
        if self.mode == "AC":
            # AC 모드: ESP32 + STM32 다운로드
            self.sequence_thread = SequentialDownloadThread(
                self.esp_settings,
                self.stm_settings
            )
            self.sequence_thread.esp_progress_signal.connect(self.update_esp_progress)
        else:
            # DC 모드: STM32만 다운로드
            self.sequence_thread = SequentialDownloadThread(
                None,  # ESP 설정 없음
                self.stm_settings
            )
        
        # 공통 시그널 연결
        self.sequence_thread.stm_progress_signal.connect(self.update_stm_progress)
        self.sequence_thread.status_signal.connect(self.update_status)
        self.sequence_thread.completed_signal.connect(self.on_sequence_completed)
        
        # 스레드 시작
        self.sequence_thread.start()
    
    def update_esp_progress(self, value):
        """ESP32 진행률 업데이트 (AC 모드에서만)"""
        if self.mode == "AC":
            self.esp_progress.setValue(value)
            QApplication.processEvents()
    
    def update_stm_progress(self, value):
        """STM32 진행률 업데이트"""
        self.stm_progress.setValue(value)
        QApplication.processEvents()
    
    def update_status(self, status):
        """상태 메시지 업데이트"""
        self.status_label.setText(status)
        QApplication.processEvents()
    
    def on_sequence_completed(self, success):
        self.download_in_progress = False
        self.download_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", "다운로드 성공")
        else:
            QMessageBox.critical(self, "Error", "다운로드 실패")

class SequentialDownloadThread(QThread):
    # 시그널 정의
    esp_progress_signal = pyqtSignal(int)
    stm_progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    completed_signal = pyqtSignal(bool)
    
    def __init__(self, esp_settings, stm_settings):
        super().__init__()
        self.esp_settings = esp_settings
        self.stm_settings = stm_settings
        self.esp_success = False
        self.stm_success = False
        
    def run(self):
        try:
            if self.esp_settings:  # AC 모드
                # 1. ESP32 다운로드 실행
                self.status_signal.emit("Downloading ESP32 firmware...")
                
                # ESP32 다운로드 스레드 생성
                esp_thread = ESPDownloadThread(self.esp_settings)
                esp_thread.progress_updated.connect(self.esp_progress_signal.emit)
                esp_thread.status_updated.connect(self.status_signal.emit)
                
                # 다운로드 시작
                esp_thread.start()
                
                # 완료 대기
                while esp_thread.isRunning():
                    for _ in range(10):
                        QThread.msleep(10)
                        QApplication.processEvents()
                
                # ESP32 다운로드 결과 확인
                if hasattr(esp_thread, 'process') and esp_thread.process:
                    self.esp_success = esp_thread.process.returncode == 0
                else:
                    self.esp_success = False
                
                if not self.esp_success:
                    self.status_signal.emit("ESP32 download failed!")
                    self.completed_signal.emit(False)
                    return
                
                # 잠시 대기
                self.status_signal.emit("ESP32 download completed. Preparing STM32 download...")
                QThread.sleep(2)
            
            # 2. STM32 다운로드 실행 (AC/DC 모드 모두)
            self.status_signal.emit("Downloading STM32 firmware...")
            self.stm_success = self.download_stm32()
            
            # 최종 결과
            if self.esp_settings:  # AC 모드
                success = self.esp_success and self.stm_success
            else:  # DC 모드
                success = self.stm_success
            
            if success:
                self.status_signal.emit("Download sequence completed successfully!")
            else:
                self.status_signal.emit("Download sequence failed!")
            
            self.completed_signal.emit(success)
                
        except Exception as e:
            self.status_signal.emit(f"Error: {str(e)}")
            self.completed_signal.emit(False)
    
    def download_stm32(self):
        """STM32 다운로드 실행"""
        try:
            from ..controllers.stm_controller import STMController
            
            # STM 컨트롤러 생성
            stm_controller = STMController()
            stm_controller.settings = self.stm_settings
            
            # 진행률 업데이트 콜백
            def update_progress(value, status):
                self.stm_progress_signal.emit(value)
                self.status_signal.emit(status)
                QApplication.processEvents()  # 이벤트 처리 허용
            
            # 다운로드 실행
            success, message = stm_controller.download(update_progress)
            
            if not success:
                self.status_signal.emit(f"STM32 download failed: {message}")
            
            return success
            
        except Exception as e:
            self.status_signal.emit(f"STM32 download error: {str(e)}")
            return False
