from pathlib import Path
import os
import shutil

class STMSettings:
    def __init__(self):
        self.firmware_path = None
        self.flash_start = 0x08000000  # STM32G4 시리즈의 플래시 시작 주소
        self.verify = True             # 기본적으로 검증 활성화
        
        # 기본 경로 설정
        self.base_path = Path(__file__).parent.parent.parent / 'config' / 'stm'
        
        # AC/DC 모드 디렉토리 생성
        self.ac_path = self.base_path / 'AC'
        self.dc_path = self.base_path / 'DC'
        
        # 디렉토리 생성
        self.ac_path.mkdir(parents=True, exist_ok=True)
        self.dc_path.mkdir(parents=True, exist_ok=True)
        
        # 기본 AC 모드 펌웨어 파일 설정
        self.ac_firmware = self.ac_path / 'stm32AC.bin'
        self.dc_firmware = self.dc_path / 'stm32DC.bin'
        
        # 이전 경로의 파일이 있다면 새 경로로 복사
        old_firmware = self.base_path / 'stm32.bin'
        if old_firmware.exists():
            # 이전 파일을 AC와 DC 모드 모두에 복사
            shutil.copy2(old_firmware, self.ac_firmware)
            shutil.copy2(old_firmware, self.dc_firmware)
            # 이전 파일 삭제 (선택사항)
            # old_firmware.unlink()
        
        # 기본적으로 AC 모드 펌웨어 설정
        if self.ac_firmware.exists():
            self.firmware_path = str(self.ac_firmware.resolve()) 