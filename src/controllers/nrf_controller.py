import subprocess
import os
import time
from pathlib import Path
from ..models.nrf_settings import NRFSettings

class NRFController:
    def __init__(self):
        self.settings = NRFSettings()
        self.firmware_path = None
        self.retry_count = 3
        self.retry_delay = 1
        
        # OpenOCD 설정
        self.openocd_path = "openocd"
        self.openocd_script = self._get_openocd_script()
        
        # J-Link 설정
        self.jlink_path = "JLinkExe"
        self.jlink_device = "nRF52840_xxAA"

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

    def _create_jlink_script(self, firmware_path):
        """J-Link 커맨드 스크립트 생성"""
        script_content = f"""si 1
speed 4000
r
h
loadfile {firmware_path}
r
g
exit"""
        script_path = "temp_jlink_script.jlink"
        with open(script_path, "w") as f:
            f.write(script_content)
        return script_path

    def download_with_openocd(self, progress_callback=None):
        """OpenOCD를 사용한 다운로드"""
        if not self.openocd_script:
            print("Error: OpenOCD script not found")
            return False

        cmd = [
            self.openocd_path,
            "-f", self.openocd_script,
            "-c", "init",
            "-c", "reset halt",
            "-c", f"program {self.firmware_path} verify",
            "-c", "reset",
            "-c", "exit"
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    if progress_callback:
                        if "Programming Started" in output:
                            progress_callback(20)
                        elif "Programming Finished" in output:
                            progress_callback(60)
                        elif "Verified OK" in output:
                            progress_callback(100)

            return process.returncode == 0

        except Exception as e:
            print(f"Error during OpenOCD download: {str(e)}")
            return False

    def download_with_jlink(self, progress_callback=None):
        """J-Link를 사용한 다운로드"""
        script_path = self._create_jlink_script(self.firmware_path)
        
        cmd = [
            self.jlink_path,
            "-device", self.jlink_device,
            "-if", "SWD",
            "-speed", "4000",
            "-autoconnect", "1",
            "-CommanderScript", script_path
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    if progress_callback:
                        if "Connecting to target" in output:
                            progress_callback(20)
                        elif "Loading program" in output:
                            progress_callback(50)
                        elif "Verifying" in output:
                            progress_callback(80)
                        elif "Download complete" in output:
                            progress_callback(100)

            os.remove(script_path)
            return process.returncode == 0

        except Exception as e:
            print(f"Error during J-Link download: {str(e)}")
            if os.path.exists(script_path):
                os.remove(script_path)
            return False

    def download(self, use_openocd, progress_callback=None):
        """펌웨어 다운로드 실행"""
        if not self.firmware_path:
            print("Error: No firmware file selected")
            return False

        for attempt in range(self.retry_count):
            try:
                if use_openocd:
                    success = self.download_with_openocd(progress_callback)
                else:
                    success = self.download_with_jlink(progress_callback)
                
                if success:
                    return True
                
            except Exception as e:
                print(f"Error during download (attempt {attempt + 1}): {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                continue

        return False

    def set_firmware(self, firmware_path):
        self.settings.firmware_path = firmware_path

    def download_firmware(self, progress_callback=None):
        if not self.settings.firmware_path:
            raise ValueError("Firmware path not set")
            
        # 다운로드 로직 구현
        # progress_callback을 사용하여 진행 상황 업데이트
        pass
