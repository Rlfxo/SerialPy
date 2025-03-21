class ButtonStyles:
    DEFAULT_STYLE = """
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
            color: #757575;
        }
    """
    
    DOWNLOAD_STYLE = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #388E3C;
        }
        QPushButton:pressed {
            background-color: #1B5E20;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
            color: #757575;
        }
    """
    
    REFRESH_STYLE = """
        QPushButton {
            background-color: #FF9800;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #F57C00;
        }
        QPushButton:pressed {
            background-color: #E65100;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
            color: #757575;
        }
    """

    @staticmethod
    def get_main_button_style(r, g, b):
        return """
            QPushButton {{
                background-color: rgba({}, {}, {}, 0.8);
                color: black;
                border-radius: 10px;
                border: 2px solid rgba({}, {}, {}, 0.8);
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba({}, {}, {}, 0.9);
            }}
            QPushButton:pressed {{
                background-color: rgba({}, {}, {}, 1.0);
            }}
        """.format(r, g, b, r*0.8, g*0.8, b*0.8, r, g, b, r, g, b)

    @staticmethod
    def get_exit_button_style():
        return """
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border-radius: 10px;
                border: 2px solid #FF5252;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
            QPushButton:pressed {
                background-color: #FF4444;
            }
        """

    @staticmethod
    def get_download_button_style():
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
