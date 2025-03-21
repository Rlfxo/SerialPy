import subprocess
import sys
import os
import time
from ..models.stm_settings import STMSettings
from PyQt5.QtCore import QProcess
import logging
from PyQt5.QtWidgets import QMessageBox
from pathlib import Path
import tempfile
import shutil

# 로거 설정
logger = logging.getLogger(__name__)

class STMController:
    def __init__(self):
        self.settings = STMSettings()
        self.process = None
        self.logger = logging.getLogger('STM32')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[STM32] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # 기본 펌웨어 파일 로드 상태 로깅
        if self.settings.firmware_path:
            self.logger.info(f"Default firmware loaded: {self.settings.firmware_path}")
        
        # OpenOCD 설치 확인
        if not self._check_openocd_installed():
            self.logger.error("OpenOCD is not installed!")
            self._show_installation_guide()

        # 기본 펌웨어 경로 설정
        base_path = Path(__file__).parent.parent.parent / 'config' / 'stm'
        default_firmware = base_path / 'stm32.bin'
        
        # 파일이 존재하면 기본 경로로 설정
        if default_firmware.exists():
            # 절대 경로로 변환 - 문자열로 변환하기 전에 resolve() 호출
            self.settings.firmware_path = str(default_firmware.resolve())
            print(f"STM32 firmware path: {self.settings.firmware_path}")

    def _check_openocd_installed(self):
        try:
            subprocess.run(["openocd", "--version"], 
                         capture_output=True, 
                         text=True)
            return True
        except FileNotFoundError:
            return False

    def _show_installation_guide(self):
        msg = """
OpenOCD is not installed on this system. Please install it:

For Windows:
1. Download OpenOCD from: http://openocd.org/
2. Add it to your system PATH

For macOS:
    brew install open-ocd

For Ubuntu/Debian:
    sudo apt-get install openocd

For other Linux:
    Check your package manager for 'openocd' package
"""
        QMessageBox.warning(None, "OpenOCD Not Found", msg)

    def _get_openocd_script(self):
        """OpenOCD 스크립트 경로 반환"""
        script_paths = [
            "/usr/local/share/openocd/scripts/interface/stlink.cfg",
            "/usr/share/openocd/scripts/interface/stlink.cfg",
            "C:\\OpenOCD\\share\\openocd\\scripts\\interface\\stlink.cfg"
        ]
        
        for path in script_paths:
            if os.path.exists(path):
                return path
        return None

    def set_firmware(self, firmware_path):
        """펌웨어 파일 경로 설정"""
        self.settings.firmware_path = firmware_path

    def create_download_command(self):
        # 경로 처리 개선
        firmware_path = self.settings.firmware_path
        
        # Windows 환경에서 경로 처리
        if os.name == 'nt':
            # 경로에 공백이 있으면 따옴표로 감싸기
            if ' ' in firmware_path:
                firmware_path = f'"{firmware_path}"'
            # 백슬래시를 포워드 슬래시로 변환 (OpenOCD 호환성)
            firmware_path = firmware_path.replace('\\', '/')
        
        cmd = [
            "openocd",
            "-d2",
            "-f", "interface/stlink.cfg",
            "-f", "target/stm32g4x.cfg",
            "-c", "init",
            "-c", "reset init",
            "-c", "halt",
            "-c", f"flash write_image erase {firmware_path} 0x08000000",
            "-c", f"verify_image {firmware_path}",
            "-c", "reset run",
            "-c", "shutdown"
        ]
        self.logger.info(f"Command: {' '.join(cmd)}")  # 실행 명령어 로깅
        return cmd

    def check_stlink(self):
        """ST-Link 연결 확인"""
        try:
            # ST-Link 확인 명령어 (예: ST-Link Utility CLI 또는 OpenOCD)
            # 실제 환경에 맞게 수정 필요
            cmd = ["st-info", "--probe"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return "ST-LINK" in result.stdout
        except:
            return False

    def download(self, progress_callback):
        try:
            self.logger.info("Starting STM32 firmware download...")
            self.logger.info(f"Using firmware file: {self.settings.firmware_path}")
            
            # 다운로드 시작 시 진행률 표시
            progress_callback(10, "Initializing OpenOCD...")
            
            # Windows에서는 배치 파일 방식 사용
            if os.name == 'nt':
                return self._download_windows(progress_callback)
            else:
                return self._download_unix(progress_callback)
            
        except Exception as e:
            self.logger.error(f"Download error: {str(e)}")
            return False, f"Download failed: {str(e)}"

    def _download_windows(self, progress_callback):
        """Windows 환경에서 다운로드 실행"""
        try:
            # 펌웨어 파일 경로 확인
            if not os.path.exists(self.settings.firmware_path):
                self.logger.error(f"Firmware file not found: {self.settings.firmware_path}")
                return False, f"Firmware file not found: {self.settings.firmware_path}"
            
            # 현재 작업 디렉토리에 파일 복사
            import shutil
            
            # 간단한 이름으로 현재 디렉토리에 복사
            firmware_copy = "firmware_temp.bin"
            shutil.copy2(self.settings.firmware_path, firmware_copy)
            self.logger.info(f"Copied firmware to current directory: {firmware_copy}")
            
            # 명령어 생성 - 상대 경로 사용
            cmd = [
                "openocd",
                "-d2",
                "-f", "interface/stlink.cfg",
                "-f", "target/stm32g4x.cfg",
                "-c", "init",
                "-c", "reset init",
                "-c", "halt",
                "-c", f"flash write_image erase firmware_temp.bin 0x08000000",
                "-c", f"verify_image firmware_temp.bin",
                "-c", "reset run",
                "-c", "shutdown"
            ]
            
            self.logger.info(f"Command: {' '.join(cmd)}")
            progress_callback(30, "Connecting to STM32...")
            
            # 프로세스 실행
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # 출력 처리
            output_lines = []
            while True:
                line = self.process.stdout.readline()
                if not line and self.process.poll() is not None:
                    break
                
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    self.logger.info(f"OpenOCD: {line}")
                    
                    # 진행 상태 업데이트
                    if "auto-selecting first available session" in line:
                        progress_callback(40, "Detecting STM32...")
                    elif "Target voltage" in line:
                        progress_callback(50, "Target detected...")
                    elif "flash size" in line:
                        progress_callback(60, "Preparing to flash...")
                    elif "Adding extra erase range" in line or "auto erase enabled" in line:
                        progress_callback(70, "Erasing flash...")
                    elif "wrote" in line:
                        progress_callback(80, "Writing firmware...")
                    elif "verified" in line:
                        progress_callback(90, "Verifying firmware...")
                    elif "shutdown command invoked" in line:
                        progress_callback(95, "Finalizing...")
            
            # 임시 파일 정리
            try:
                os.remove(firmware_copy)
            except:
                pass
            
            # 프로세스 종료 코드 확인
            returncode = self.process.poll()
            self.logger.info(f"OpenOCD process exited with code: {returncode}")
            
            if returncode == 0:
                progress_callback(100, "Download completed")
                self.logger.info("Download completed successfully")
                return True, "Download completed successfully"
            else:
                error_msg = "\n".join(output_lines[-5:]) if output_lines else "Unknown error"
                self.logger.error(f"Download failed: {error_msg}")
                return False, f"Download failed: {error_msg}"
            
        except Exception as e:
            self.logger.error(f"Windows download failed: {str(e)}")
            return False, f"Download failed: {str(e)}"

    def _download_unix(self, progress_callback):
        """Unix 환경에서 다운로드 실행"""
        try:
            # 명령어 생성
            cmd = [
                "openocd",
                "-d2",
                "-f", "interface/stlink.cfg",
                "-f", "target/stm32g4x.cfg",
                "-c", "init",
                "-c", "reset init",
                "-c", "halt",
                "-c", f"flash write_image erase {self.settings.firmware_path} 0x08000000",
                "-c", f"verify_image {self.settings.firmware_path}",
                "-c", "reset run",
                "-c", "shutdown"
            ]
            
            self.logger.info(f"Command: {' '.join(cmd)}")
            progress_callback(30, "Connecting to STM32...")
            
            # 프로세스 실행
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # 출력 처리
            output_lines = []
            while True:
                line = self.process.stdout.readline()
                if not line and self.process.poll() is not None:
                    break
                
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    self.logger.info(f"OpenOCD: {line}")
                    
                    # 진행 상태 업데이트
                    if "auto-selecting first available session" in line:
                        progress_callback(40, "Detecting STM32...")
                    elif "Target voltage" in line:
                        progress_callback(50, "Target detected...")
                    elif "flash size" in line:
                        progress_callback(60, "Preparing to flash...")
                    elif "Adding extra erase range" in line or "auto erase enabled" in line:
                        progress_callback(70, "Erasing flash...")
                    elif "wrote" in line:
                        progress_callback(80, "Writing firmware...")
                    elif "verified" in line:
                        progress_callback(90, "Verifying firmware...")
                    elif "shutdown command invoked" in line:
                        progress_callback(95, "Finalizing...")
            
            # 프로세스 종료 코드 확인
            returncode = self.process.poll()
            self.logger.info(f"OpenOCD process exited with code: {returncode}")
            
            if returncode == 0:
                progress_callback(100, "Download completed")
                self.logger.info("Download completed successfully")
                return True, "Download completed successfully"
            else:
                error_msg = "\n".join(output_lines[-5:]) if output_lines else "Unknown error"
                self.logger.error(f"Download failed: {error_msg}")
                return False, f"Download failed: {error_msg}"
            
        except Exception as e:
            self.logger.error(f"Unix download failed: {str(e)}")
            return False, f"Download failed: {str(e)}"
