class NRFSettings:
    def __init__(self):
        self.firmware_path = None
        self.use_jlink = False  # True: J-Link, False: OpenOCD
        self.device = "nRF52840_xxAA"
        self.interface = "swd"
        self.speed = "4000" 