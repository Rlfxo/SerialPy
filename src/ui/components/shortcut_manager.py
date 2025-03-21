from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QShortcut)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

class ShortcutManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shortcuts = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 단축키 설명 섹션
        shortcut_info = QLabel("단축키 안내:")
        layout.addWidget(shortcut_info)
        
        # 단축키 목록
        shortcuts_layout = QVBoxLayout()
        shortcuts_layout.addWidget(QLabel("F5: 다운로드"))
        shortcuts_layout.addWidget(QLabel("↑: 시리얼 번호 증가"))
        shortcuts_layout.addWidget(QLabel("↓: 시리얼 번호 감소"))
        
        layout.addLayout(shortcuts_layout)
        self.setLayout(layout)

    def register_shortcut(self, key, callback):
        """단축키 등록"""
        shortcut = QShortcut(QKeySequence(key), self)
        shortcut.activated.connect(callback)
        self.shortcuts[key] = shortcut

    def setup_default_shortcuts(self, download_callback=None, 
                              increment_callback=None, 
                              decrement_callback=None):
        """기본 단축키 설정"""
        if download_callback:
            self.register_shortcut("F5", download_callback)
        
        if increment_callback:
            self.register_shortcut("Up", increment_callback)
        
        if decrement_callback:
            self.register_shortcut("Down", decrement_callback)

    def clear_shortcuts(self):
        """모든 단축키 제거"""
        for shortcut in self.shortcuts.values():
            shortcut.setEnabled(False)
        self.shortcuts.clear()