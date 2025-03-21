from pathlib import Path

class ESPSettings:
    # 메모리 맵 주소
    BOOTLOADER_ADDR = "0x1000"
    PARTITION_ADDR = "0x8000"
    OTA_DATA_ADDR = "0xd000"
    APP_ADDR = "0x10000"

    # 플래시 설정
    FLASH_MODE = "dio"
    FLASH_FREQ = "40m"
    FLASH_SIZE = "detect"

    # 통신 설정
    BAUD_RATE_FLASH = 921600
    BAUD_RATE_MONITOR = 115200

    def __init__(self):
        self.port = None
        base_path = Path(__file__).parent.parent.parent / 'config' / 'esp'
        self.bootloader_path = str(base_path / 'bootloader.bin')
        self.partition_path = str(base_path / 'partition-table.bin')
        self.ota_path = str(base_path / 'ota_data_initial.bin')
        self.app_path = str(base_path / 'esp32.bin')
