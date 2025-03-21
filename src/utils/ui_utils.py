from PyQt5.QtWidgets import QApplication

class UIUtils:
    @staticmethod
    def center_window(window):
        qr = window.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        window.move(qr.topLeft())
