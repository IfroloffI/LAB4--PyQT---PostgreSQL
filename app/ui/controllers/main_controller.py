from PyQt6.QtCore import QObject, pyqtSignal, QAbstractTableModel, Qt
from PyQt6.QtWidgets import QMessageBox, QTableView
from app.core.services.data_service import DataService
from app.core.database.models import Client, Account, Transaction
from typing import Optional, List


class BaseTableModel(QAbstractTableModel):
    def __init__(self, data: list, headers: list):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        return self._data[index.row()][index.column()]

    def headerData(self, section, orientation, role):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self._headers[section]
        return None


class MainController(QObject):
    data_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.data_service = DataService()
        self.current_client = None
        self.current_account = None

    def load_clients(self, table_view: QTableView):
        clients = self.data_service.get_all_clients()
        data = []
        for client in clients:
            data.append(
                [
                    client.id,
                    client.last_name,
                    client.first_name,
                    client.passport_number,
                    client.phone_number or "",
                    client.email or "",
                    client.created_at.strftime("%Y-%m-%d %H:%M"),
                    client.updated_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )
        headers = [
            "ID",
            "Фамилия",
            "Имя",
            "Паспорт",
            "Телефон",
            "Email",
            "Создан",
            "Обновлен",
        ]
        table_view.setModel(BaseTableModel(data, headers))

    def select_client(self, client_id: int):
        self.current_client = self.data_service.get_client_by_id(client_id)
        self.current_account = None
        return self.current_client

    def add_client(self, **data) -> bool:
        try:
            success = self.data_service.add_client(**data)
            if success:
                self.data_updated.emit()
            return success
        except Exception as e:
            self.show_error(f"Ошибка при добавлении клиента: {str(e)}")
            return False

    def update_client(self, client_id: int, **data) -> bool:
        success = self.data_service.update_client(client_id, **data)
        if success:
            self.data_updated.emit()
        return success

    def delete_client(self, client_id: int) -> bool:
        success = self.data_service.delete_client(client_id)
        if success:
            self.data_updated.emit()
        return success

    def load_client_accounts(self, client_id: int, table_view: QTableView):
        accounts = self.data_service.get_client_accounts(client_id)
        data = []
        for account in accounts:
            data.append(
                [
                    account.id,
                    account.account_number,
                    account.account_type,
                    f"{account.balance:.2f}",
                    account.currency,
                    account.opened_date.strftime("%Y-%m-%d"),
                    "Да" if account.is_active else "Нет",
                    account.created_at.strftime("%Y-%m-%d %H:%M"),
                    account.updated_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )
        headers = [
            "ID",
            "Номер счета",
            "Тип",
            "Баланс",
            "Валюта",
            "Дата открытия",
            "Активен",
            "Создан",
            "Обновлен",
        ]
        table_view.setModel(BaseTableModel(data, headers))

    def select_account(self, account_id: int):
        if not self.current_client:
            return None
        accounts = self.data_service.get_client_accounts(self.current_client.id)
        self.current_account = next((a for a in accounts if a.id == account_id), None)
        return self.current_account

    def add_account(self, client_id: int, **data) -> bool:
        try:
            success = self.data_service.add_account(client_id=client_id, **data)
            if success:
                self.data_updated.emit()
            return success
        except Exception as e:
            self.show_error(f"Ошибка при добавлении счета: {str(e)}")
            return False

    def update_account(self, account_id: int, **data) -> bool:
        success = self.data_service.update_account(account_id, **data)
        if success:
            self.data_updated.emit()
        return success

    def delete_account(self, account_id: int) -> bool:
        success = self.data_service.delete_account(account_id)
        if success:
            self.data_updated.emit()
        return success

    def get_client_by_id(self, client_id: int) -> Optional[Client]:
        return self.data_service.get_client_by_id(client_id)

    def show_error(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Ошибка")
        msg.setInformativeText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec()

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.data_service.get_transaction_by_id(transaction_id)

    def add_transaction(self, **data) -> bool:
        try:
            success = self.data_service.add_transaction(**data)
            if success:
                self.data_updated.emit()
            return success
        except Exception as e:
            self.show_error(f"Ошибка при добавлении транзакции: {str(e)}")
            return False

    def update_transaction(self, transaction_id: int, **data) -> bool:
        success = self.data_service.update_transaction(transaction_id, **data)
        if success:
            self.data_updated.emit()
        return success

    def delete_transaction(self, transaction_id: int) -> bool:
        success = self.data_service.delete_transaction(transaction_id)
        if success:
            self.data_updated.emit()
        return success
