# SerialPy
```
UI Layer:
MainWindow
  ├─ QCWindow
  │   ├─ SerialPortSelector
  │   ├─ LogViewer (모니터링 + 저장)
  │   ├─ CLIInterface (명령어 입력)
  │   ├─ HeaderEditor (헤더 읽기/수정)
  │   └─ DeviceInfoPanel (model_name, serial_number)
  │
  └─ OCWindow
      ├─ SerialPortSelector
      ├─ SimpleDeviceInfo (model_name, serial_number)
      ├─ EnhancedProgressBar
      └─ ShortcutManager (단축키, 방향키 제어)

Controller Layer:
  ├─ SerialController (공통)
  │   ├─ PortManager
  │   ├─ DownloadManager
  │   └─ DeviceCommManager
  │
  ├─ QCController
  │   ├─ LogManager
  │   ├─ HeaderManager
  │   └─ CLIManager
  │
  ├─ OCController
  │   └─ ShortcutManager
  │
  └─ ESPController (비활성화but유지)

Model Layer:
  ├─ SerialSettings (공통)
  │   ├─ PortConfig
  │   └─ DeviceConfig
  │
  ├─ QCSettings
  │   ├─ LogSettings
  │   ├─ HeaderSettings
  │   └─ CLISettings
  │
  └─ OCSettings
      ├─ UISettings
      └─ ShortcutSettings

Utility Layer:
  ├─ FileUtils
  │   ├─ LogFileHandler
  │   └─ HeaderFileHandler
  │
  └─ UIUtils
      ├─ ProgressBarManager
      └─ ShortcutHandler
```