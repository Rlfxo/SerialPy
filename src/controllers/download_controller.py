class DownloadController:
    def __init__(self):
        self.current_progress = 0

    def esp_download(self, file_path):
        print(f"ESP32 다운로드 시작: {file_path}")
        # TODO: ESP32 다운로드 로직 구현
        return True

    def nrf_download(self, file_path, use_openocd):
        print(f"nRF52 다운로드 시작: {file_path}")
        print(f"OpenOCD 모드: {use_openocd}")
        # TODO: nRF52 다운로드 로직 구현
        return True

    def full_download(self, esp_path, nrf_path, use_openocd):
        print("전체 다운로드 시작")
        if self.esp_download(esp_path) and self.nrf_download(nrf_path, use_openocd):
            return True
        return False
