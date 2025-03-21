from .serial_controller import SerialController

class ShortcutManager:
    def __init__(self):
        self.shortcuts = {}
        
    def register_shortcut(self, key, callback):
        self.shortcuts[key] = callback

class OCController:
    def __init__(self):
        self.serial_controller = SerialController()
        self.shortcut_manager = ShortcutManager() 