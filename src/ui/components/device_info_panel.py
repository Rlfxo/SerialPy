from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QLabel)

class DeviceInfoPanel(QWidget):
    def __init__(self, mode='qc', parent=None):
        super().__init__(parent)
        self.mode = mode  # 'qc' 또는 'oc'
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 공통 부분: 모델명
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel('모델명:'))
        if self.mode == 'qc':
            self.model_edit = QLineEdit()
            model_layout.addWidget(self.model_edit)
        else:  # oc mode
            self.model_label = QLabel('')
            model_layout.addWidget(self.model_label)
        
        # 공통 부분: 시리얼 번호
        serial_layout = QHBoxLayout()
        serial_layout.addWidget(QLabel('시리얼 번호:'))
        self.serial_edit = QLineEdit()
        serial_layout.addWidget(self.serial_edit)
        
        if self.mode == 'oc':
            # OC 모드 전용: +/- 버튼
            inc_btn = QPushButton('+')
            dec_btn = QPushButton('-')
            inc_btn.setFixedWidth(30)
            dec_btn.setFixedWidth(30)
            inc_btn.clicked.connect(self.increment_serial)
            dec_btn.clicked.connect(self.decrement_serial)
            serial_layout.addWidget(inc_btn)
            serial_layout.addWidget(dec_btn)
        
        # QC 모드 전용: 추가 버튼들
        if self.mode == 'qc':
            button_layout = QHBoxLayout()
            read_btn = QPushButton('읽기')
            write_btn = QPushButton('쓰기')
            read_btn.clicked.connect(self.read_info)
            write_btn.clicked.connect(self.write_info)
            button_layout.addWidget(read_btn)
            button_layout.addWidget(write_btn)
            button_layout.addStretch()
        
        layout.addLayout(model_layout)
        layout.addLayout(serial_layout)
        if self.mode == 'qc':
            layout.addLayout(button_layout)
        
        self.setLayout(layout)

    # 공통 메서드
    def get_serial(self):
        return self.serial_edit.text()

    def set_serial(self, serial_number):
        self.serial_edit.setText(str(serial_number))

    def get_model(self):
        if self.mode == 'qc':
            return self.model_edit.text()
        return self.model_label.text()

    def set_model(self, model_name):
        if self.mode == 'qc':
            self.model_edit.setText(model_name)
        else:
            self.model_label.setText(model_name)

    # OC 모드 전용 메서드
    def increment_serial(self):
        if self.mode != 'oc':
            return
        try:
            current = int(self.serial_edit.text())
            self.serial_edit.setText(str(current + 1))
        except ValueError:
            pass

    def decrement_serial(self):
        if self.mode != 'oc':
            return
        try:
            current = int(self.serial_edit.text())
            if current > 0:
                self.serial_edit.setText(str(current - 1))
        except ValueError:
            pass

    # QC 모드 전용 메서드
    def read_info(self):
        if self.mode != 'qc':
            return
        # TODO: 정보 읽기 구현
        pass

    def write_info(self):
        if self.mode != 'qc':
            return
        # TODO: 정보 쓰기 구현
        pass