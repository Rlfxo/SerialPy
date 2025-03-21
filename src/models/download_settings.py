class DownloadSettings:
    def __init__(self):
        self.esp_firmware_path = None
        self.nrf_firmware_path = None
        self.use_openocd = False
        self.download_progress = 0
        self.window_size = (520, 420)
        self.button_size = (200, 200)
        self.exit_button_size = (100, 20)
