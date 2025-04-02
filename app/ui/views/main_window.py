from PyQt6.QtWidgets import QMainWindow
from design.generated.ui_main_window import Ui_MainWindow
from app.ui.controllers.main_controller import MainController


class MainWindow(QMainWindow):
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        from app.core.config import AppConfig

        self.setWindowTitle(f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")

    def _connect_signals(self):
        self.ui.pushButton.clicked.connect(self.controller.on_button_clicked)
