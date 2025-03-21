import subprocess
import sys
import os
import serial
import serial.tools.list_ports
import time
from ..models.esp_settings import ESPSettings
import re
from PyQt5.QtCore import QProcess, QThread, pyqtSignal
import logging
from pathlib import Path
import esptool  # 직접 import

# 로거 설정
logger = logging.getLogger(__name__)

class ESPController:
    def __init__(self):
        self.settings = ESPSettings()
        self.esptool_path = "esptool.py" if self._check_esptool() else None
        self.retry_count = 3
        self.retry_delay = 1
        self.process = None
        self.current_section = 0  # 현재 진행 중인 섹션 (0-3)
        self.total_sections = 4   # 총 섹션 수

    def _check_esptool(self):
        try:
            # Python 모듈로 실행
            subprocess.run(
                [sys.executable, "-m", "esptool", "--version"],
                capture_output=True,
                text=True
            )
            return True
        except FileNotFoundError:
            print("Error: esptool not found. Please install it using: pip install esptool")
            return False

    def scan_ports(self):
        """사용 가능한 시리얼 포트 스캔"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports

    def _create_flash_command(self):
        """플래시 명령어 생성"""
        cmd = [
            self.esptool_path,
            "--chip", "esp32",
            "--port", self.settings.port,
            "--baud", str(self.settings.BAUD_RATE_FLASH),
            "--before", "default_reset",
            "--after", "hard_reset",
            "write_flash",
            "-z",
            "--flash_mode", self.settings.FLASH_MODE,
            "--flash_freq", self.settings.FLASH_FREQ,
            "--flash_size", self.settings.FLASH_SIZE
        ]

        # 각 파일 추가
        if self.settings.bootloader_path:
            cmd.extend([self.settings.BOOTLOADER_ADDR, self.settings.bootloader_path])
        if self.settings.partition_path:
            cmd.extend([self.settings.PARTITION_ADDR, self.settings.partition_path])
        if self.settings.ota_path:
            cmd.extend([self.settings.OTA_DATA_ADDR, self.settings.ota_path])
        if self.settings.app_path:
            cmd.extend([self.settings.APP_ADDR, self.settings.app_path])

        return cmd

    def flash_all(self, progress_callback=None):
        """전체 펌웨어 플래싱"""
        if not self.esptool_path:
            return False

        if not all([self.settings.bootloader_path, 
                   self.settings.partition_path,
                   self.settings.ota_path, 
                   self.settings.app_path,
                   self.settings.port]):
            print("Error: Missing required files or port")
            return False

        for attempt in range(self.retry_count):
            try:
                cmd = self._create_flash_command()
                self.process = QProcess()
                
                # 진행률 업데이트를 위한 콜백 연결
                if progress_callback:
                    self.process.readyReadStandardOutput.connect(
                        lambda: self._handle_output(self.process.readAllStandardOutput(), progress_callback)
                    )
                
                self.process.start(cmd[0], cmd[1:])
                self.process.waitForFinished(-1)  # 완료될 때까지 대기
                
                if self.process.exitCode() == 0:
                    return True
                
            except Exception as e:
                print(f"Error during flashing (attempt {attempt + 1}): {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                continue

        return False

    def _handle_output(self, output, progress_callback):
        """프로세스 출력 처리 및 진행률 업데이트"""
        try:
            output = bytes(output).decode('utf-8')
            print(output, end='')  # 콘솔에 출력
            
            # 새로운 섹션 시작 감지
            if "Writing at 0x00001000" in output:
                self.current_section = 0
            elif "Writing at 0x00008000" in output:
                self.current_section = 1
            elif "Writing at 0x0000d000" in output:
                self.current_section = 2
            elif "Writing at 0x00010000" in output:
                self.current_section = 3
            
            # 진행률 찾기
            match = re.search(r'\((\d+)\s*%\)', output)
            if match:
                section_progress = int(match.group(1))
                # 전체 진행률 계산
                total_progress = (self.current_section * 100 + section_progress) // self.total_sections
                progress_callback(total_progress)
                
            # 해시 검증 성공 시 섹션 완료로 처리
            if "Hash of data verified." in output:
                total_progress = ((self.current_section + 1) * 100) // self.total_sections
                progress_callback(total_progress)
                
        except Exception as e:
            print(f"Output handling error: {str(e)}")

    def check_esptool_installed(self):
        try:
            import esptool
            return True
        except ImportError:
            return False

    def download(self, progress_callback):
        self.logger.info("\n=== ESP32 Download Start ===")
        
        try:
            # Windows와 Mac/Linux 분기 처리
            if sys.platform == 'win32':
                return self._download_windows(progress_callback)
            else:
                return self._download_unix(progress_callback)
        except Exception as e:
            self.logger.error(f"Download initialization failed: {str(e)}")
            return False, f"Download failed: {str(e)}"

    def _download_windows(self, progress_callback):
        try:
            # Windows에서는 Python 실행파일을 통해 esptool을 실행
            cmd = [
                sys.executable, "-m", "esptool",  # python -m esptool 형식으로 실행
                "--chip", "esp32",
                "--port", self.settings.port,
                "--baud", "460800",
                "--before", "default_reset",
                "--after", "hard_reset",
                "write_flash",
                "-z", "--flash_mode", "dio",
                "--flash_freq", "40m",
                "--flash_size", "detect",
                "0x1000", self.settings.bootloader_path,
                "0x8000", self.settings.partitions_path,
                "0x10000", self.settings.firmware_path,
                "0x3F0000", self.settings.coex_path
            ]

            self.logger.info(f"Executing command: {' '.join(cmd)}")
            progress_callback(50, "Downloading firmware...")

            # subprocess.Popen 사용하여 실행
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            while True:
                output = self.process.stderr.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.logger.info(f"ESP32 output: {output.strip()}")

            if self.process.returncode == 0:
                progress_callback(100, "Download completed")
                return True, "Download completed successfully"
            else:
                error_output = self.process.stderr.read()
                return False, f"Download failed: {error_output}"

        except Exception as e:
            self.logger.error(f"Windows download failed: {str(e)}")
            return False, f"Download failed: {str(e)}"

    def _download_unix(self, progress_callback):
        try:
            cmd = [
                sys.executable, "-m", "esptool",
                "--chip", "esp32",
                "--port", self.settings.port,
                "--baud", "460800",
                "--before", "default_reset",
                "--after", "hard_reset",
                "write_flash",
                "-z", "--flash_mode", "dio",
                "--flash_freq", "40m",
                "--flash_size", "detect",
                "0x1000", self.settings.bootloader_path,
                "0x8000", self.settings.partitions_path,
                "0x10000", self.settings.firmware_path,
                "0x3F0000", self.settings.coex_path
            ]

            self.logger.info(f"Executing command: {' '.join(cmd)}")
            progress_callback(50, "Downloading firmware...")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            while True:
                output = self.process.stderr.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.logger.info(f"ESP32 output: {output.strip()}")

            if self.process.returncode == 0:
                progress_callback(100, "Download completed")
                return True, "Download completed successfully"
            else:
                error_output = self.process.stderr.read()
                return False, f"Download failed: {error_output}"

        except Exception as e:
            self.logger.error(f"Unix download failed: {str(e)}")
            return False, f"Download failed: {str(e)}"

class DownloadThread(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    download_completed = pyqtSignal(bool)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.logger = logging.getLogger('ESP32')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[ESP32] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # 진행률 계산을 위한 변수들
        self.app_start_address = 0x00010000  # 애플리케이션 시작 주소
        self.current_address = 0
        self.total_size = 0
        self.is_app_section = False

    def _calculate_progress(self, address_str):
        try:
            current_addr = int(address_str, 16)
            
            # 0x00010000 이전 주소는 준비 단계
            if current_addr < self.app_start_address:
                return 0
            
            # 애플리케이션 섹션 시작
            if not self.is_app_section and current_addr >= self.app_start_address:
                self.is_app_section = True
                return 0
            
            # 애플리케이션 섹션에서의 진행률 계산
            if self.is_app_section and self.total_size > 0:
                relative_addr = current_addr - self.app_start_address
                progress = (relative_addr * 100) // (self.total_size)
                return min(max(progress, 0), 100)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Progress calculation error: {str(e)}")
            return 0

    def run(self):
        try:
            self.logger.info("Starting ESP32 firmware download...")
            
            if sys.platform == 'win32':
                python_executable = 'python'
            else:
                python_executable = sys.executable
            
            cmd = [
                python_executable,
                "-m", "esptool",
                "--chip", "esp32",
                "--port", self.settings.port,
                "--baud", "921600",
                "--before", "default_reset",
                "--after", "hard_reset",
                "write_flash",
                "-z", "--flash_mode", "dio",
                "--flash_freq", "40m",
                "--flash_size", "detect",
                "0x1000", self.settings.bootloader_path,
                "0x8000", self.settings.partition_path,
                "0xd000", self.settings.ota_path,
                "0x10000", self.settings.app_path
            ]

            self.logger.info(f"Executing command: {' '.join(cmd)}")
            
            # 환경 변수 설정 - 버퍼링 비활성화
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            # subprocess.PIPE 대신 subprocess.STDOUT 사용하여 출력 통합
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # stderr를 stdout으로 리다이렉트
                text=True,
                shell=sys.platform == 'win32',
                bufsize=0,  # 버퍼링 완전 비활성화
                env=env,
                universal_newlines=True
            )
            
            # 출력 처리를 위한 변수들
            for line in iter(self.process.stdout.readline, ''):
                line = line.strip()
                if line:
                    # 앱 섹션의 전체 크기 캡처
                    if "Compressed" in line and "bytes to" in line:
                        try:
                            size_str = line.split("Compressed ")[1].split(" bytes")[0]
                            self.total_size = int(size_str)
                            if self.total_size > 100000:  # 앱 섹션의 크기인 경우만 처리
                                self.logger.info(f"Application size: {self.total_size} bytes")
                        except:
                            pass
                    
                    # Writing at 주소 처리
                    elif "Writing at" in line:
                        try:
                            addr = line.split("Writing at ")[1].split("...")[0]
                            
                            # 0x00010000 이전은 preparing으로 표시
                            if int(addr, 16) < self.app_start_address:
                                self.logger.info(f" Writing at {addr}... (preparing)")
                            else:
                                progress = self._calculate_progress(addr)
                                self.progress_updated.emit(progress)
                                self.logger.info(f" Writing at {addr}... ({progress}%)")
                            
                            self.status_updated.emit(f"Writing at {addr}...")
                        except Exception as e:
                            self.logger.error(f"Address parsing error: {str(e)}")
                    
                    # 기타 로그 처리
                    else:
                        self.logger.info(f" {line}")
                        
                        # 앱 섹션의 검증 완료 시 100% 설정
                        if "Hash of data verified" in line and self.is_app_section:
                            self.progress_updated.emit(100)
                            self.status_updated.emit("Download completed")
            
            # 프로세스 완료 대기
            self.process.wait()
            
            # 종료 코드 확인
            if self.process.returncode == 0:
                self.logger.info("\n Download completed successfully")
                self.download_completed.emit(True)
            else:
                self.logger.error("\n Download failed")
                self.download_completed.emit(False)
                
        except Exception as e:
            self.logger.error(f" Download failed: {str(e)}")
            self.download_completed.emit(False)
