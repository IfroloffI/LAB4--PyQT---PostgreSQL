from PyQt6.QtCore import QObject
from app.core.services.data_service import DataService


class MainController(QObject):
    def __init__(self):
        super().__init__()
        self.data_service = DataService()

    def on_button_clicked(self):
        self.data_service.add_record("Hello", "world!")
        print("Кнопка нажата! Загружаем данные из БД...")

        records = self.data_service.get_all_records()
        print(f"Получено записей: {len(records)}")

        if isinstance(self.parent(), QObject):
            window = self.parent()
            if hasattr(window, "ui"):
                window.ui.pushButton.setText(f"Нажата! Записей: {len(records)}")
