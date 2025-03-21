from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, 
                           QHBoxLayout)

class CLIInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        
        # 명령어 입력창
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText('명령어 입력...')
        layout.addWidget(self.command_input)
        
        # 실행 버튼
        send_btn = QPushButton('실행')
        send_btn.clicked.connect(self.execute_command)
        layout.addWidget(send_btn)
        
        self.setLayout(layout)

    def execute_command(self):
        """명령어 실행"""
        command = self.command_input.text()
        if command:
            # TODO: 명령어 실행 로직 구현
            self.command_input.clear() 