from pathlib import Path
import sys
from PyQt6.QtWidgets import QApplication
from app.core.config import AppConfig
from app.ui.views.main_window import MainWindow
from app.ui.controllers.main_controller import MainController


def main():
    try:
        AppConfig.validate()

        app = QApplication(sys.argv)
        window = MainWindow(MainController())
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌❌❌ Error of running: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
