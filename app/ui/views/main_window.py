from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTableView,
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QComboBox,
)
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt
from design.generated.ui_main_window import Ui_MainWindow
from app.ui.controllers.main_controller import MainController, BaseTableModel


class ClientDialog(QDialog):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Добавить клиента" if client is None else "Редактировать клиента"
        )
        self.client = client
        layout = QVBoxLayout()
        form = QFormLayout()
        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.passport_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        form.addRow("Имя:", self.first_name_edit)
        form.addRow("Фамилия:", self.last_name_edit)
        form.addRow("Паспорт:", self.passport_edit)
        form.addRow("Телефон:", self.phone_edit)
        form.addRow("Email:", self.email_edit)
        if client:
            self.first_name_edit.setText(client.first_name)
            self.last_name_edit.setText(client.last_name)
            self.passport_edit.setText(client.passport_number)
            self.phone_edit.setText(client.phone_number or "")
            self.email_edit.setText(client.email or "")
        buttons = QPushButton("Сохранить")
        buttons.clicked.connect(self.accept)
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return {
            "first_name": self.first_name_edit.text(),
            "last_name": self.last_name_edit.text(),
            "passport_number": self.passport_edit.text(),
            "phone_number": self.phone_edit.text() or None,
            "email": self.email_edit.text() or None,
        }


class AccountDialog(QDialog):
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Добавить счет" if account is None else "Редактировать счет"
        )
        self.account = account
        layout = QVBoxLayout()
        form = QFormLayout()

        self.number_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["checking", "savings", "credit"])
        self.balance_edit = QLineEdit()
        self.balance_edit.setValidator(QtGui.QDoubleValidator())
        self.currency_edit = QLineEdit()
        self.currency_edit.setText("RUB")
        self.active_check = QComboBox()
        self.active_check.addItems(["Активен", "Неактивен"])

        form.addRow("Номер счета*:", self.number_edit)
        form.addRow("Тип счета*:", self.type_combo)
        form.addRow("Баланс*:", self.balance_edit)
        form.addRow("Валюта*:", self.currency_edit)
        form.addRow("Статус:", self.active_check)

        if account:
            self.number_edit.setText(account.account_number)
            self.type_combo.setCurrentText(account.account_type)
            self.balance_edit.setText(f"{account.balance:.2f}")
            self.currency_edit.setText(account.currency)
            self.active_check.setCurrentIndex(0 if account.is_active else 1)

        buttons = QPushButton("Сохранить")
        buttons.clicked.connect(self._validate_and_accept)
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _validate_and_accept(self):
        try:
            balance = float(self.balance_edit.text())
            if balance < 0:
                raise ValueError("Баланс не может быть отрицательным")
            if not self.number_edit.text().strip():
                raise ValueError("Номер счета обязателен")
            if not self.currency_edit.text().strip():
                raise ValueError("Валюта обязательна")

            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def get_data(self):
        return {
            "account_number": self.number_edit.text().strip(),
            "account_type": self.type_combo.currentText(),
            "balance": float(self.balance_edit.text()),
            "currency": self.currency_edit.text().strip(),
            "is_active": self.active_check.currentIndex() == 0,
        }


class TransactionDialog(QDialog):
    def __init__(self, parent=None, transaction=None, accounts=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Добавить транзакцию" if transaction is None else "Редактировать транзакцию"
        )
        self.transaction = transaction
        self.accounts = accounts or []

        layout = QVBoxLayout()
        form = QFormLayout()

        self.from_account_combo = QComboBox()
        self.to_account_combo = QComboBox()
        self.amount_edit = QLineEdit()
        self.amount_edit.setValidator(QtGui.QDoubleValidator(0, 999999999, 2))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["transfer", "deposit", "withdrawal"])
        self.description_edit = QLineEdit()

        self._populate_accounts()

        form.addRow("Отправитель:", self.from_account_combo)
        form.addRow("Получатель*:", self.to_account_combo)
        form.addRow("Сумма*:", self.amount_edit)
        form.addRow("Тип операции*:", self.type_combo)
        form.addRow("Описание:", self.description_edit)

        if transaction:
            if transaction.from_account_id:
                idx = next(
                    (
                        i
                        for i, acc in enumerate(self.accounts)
                        if acc.id == transaction.from_account_id
                    ),
                    0,
                )
                self.from_account_combo.setCurrentIndex(idx)

            idx = next(
                (
                    i
                    for i, acc in enumerate(self.accounts)
                    if acc.id == transaction.to_account_id
                ),
                0,
            )
            self.to_account_combo.setCurrentIndex(idx)

            self.amount_edit.setText(f"{transaction.amount:.2f}")
            self.type_combo.setCurrentText(transaction.transaction_type)
            self.description_edit.setText(transaction.description or "")

        buttons = QPushButton("Сохранить")
        buttons.clicked.connect(self._validate_and_accept)
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _populate_accounts(self):
        self.from_account_combo.addItem("Внесение средств", None)
        self.to_account_combo.addItem("Выберите счет", None)

        for acc in self.accounts:
            self.from_account_combo.addItem(
                f"{acc.account_number} ({acc.account_type})", acc.id
            )
            self.to_account_combo.addItem(
                f"{acc.account_number} ({acc.account_type})", acc.id
            )

    def _validate_and_accept(self):
        try:
            amount = float(self.amount_edit.text())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")

            to_account = self.to_account_combo.currentData()
            if not to_account:
                raise ValueError("Получатель обязателен")

            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def get_data(self):
        return {
            "from_account_id": self.from_account_combo.currentData(),
            "to_account_id": self.to_account_combo.currentData(),
            "amount": float(self.amount_edit.text()),
            "transaction_type": self.type_combo.currentText(),
            "description": self.description_edit.text().strip() or None,
        }


class MainWindow(QMainWindow):
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._setup_ui()
        self._connect_signals()
        self._load_initial_data()

    def _setup_ui(self):
        for table in [
            self.ui.clientsTableView,
            self.ui.accountsTableView,
            self.ui.transactionsTableView,
        ]:
            table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            table.hideColumn(0)

    def _connect_signals(self):
        self.ui.addClientButton.clicked.connect(self._add_client_dialog)
        self.ui.editClientButton.clicked.connect(self._edit_client_dialog)
        self.ui.deleteClientButton.clicked.connect(self._delete_client)
        self.ui.refreshClientsButton.clicked.connect(
            lambda: self._refresh_clients(True)
        )

        self.ui.addAccountButton.clicked.connect(self._add_account_dialog)
        self.ui.editAccountButton.clicked.connect(self._edit_account_dialog)
        self.ui.deleteAccountButton.clicked.connect(self._delete_account)
        self.ui.refreshAccountsButton.clicked.connect(
            lambda: self._refresh_accounts(True)
        )

        self.ui.addTransactionButton.clicked.connect(self._add_transaction_dialog)
        self.ui.editTransactionButton.clicked.connect(self._edit_transaction_dialog)
        self.ui.deleteTransactionButton.clicked.connect(self._delete_transaction)
        self.ui.refreshTransactionsButton.clicked.connect(
            lambda: self._refresh_transactions(True)
        )

        self.ui.showTransactionsButton.clicked.connect(self._show_transactions)
        self.ui.backToClientsButton.clicked.connect(self._back_to_clients)

        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self._show_about)

    def _load_initial_data(self):
        self._refresh_clients(True)
        if (model := self.ui.clientsTableView.model()) and model.rowCount() > 0:
            self.ui.clientsTableView.selectRow(0)
            self._on_client_selected()

    def _on_client_selected(self):
        selected = self.ui.clientsTableView.selectionModel().selectedRows()
        if not selected:
            self.controller.current_client = None
            self.controller.current_account = None
            self.ui.accountsGroup.setTitle("Счета клиента")
            self._refresh_accounts(True)
            return

        client_id = selected[0].data()
        client = self.controller.select_client(client_id)

        if client:
            self.ui.accountsGroup.setTitle(f"Счета клиента: {client.last_name}")
            self._refresh_accounts(True)
            # Подключаем сигнал только после загрузки данных
            if self.ui.accountsTableView.model():
                self.ui.accountsTableView.selectionModel().selectionChanged.connect(
                    self._on_account_selected
                )

    def _on_account_selected(self):
        selected = self.ui.accountsTableView.selectionModel().selectedRows()
        if not selected:
            self.controller.current_account = None
            return

        account_id = selected[0].data()
        self.controller.select_account(account_id)
        self._refresh_transactions(True)

    def _refresh_clients(self, emit_signal=True):
        self.controller.load_clients(self.ui.clientsTableView)
        if emit_signal:
            self.controller.data_updated.emit()
        # Подключаем сигнал только после загрузки данных
        if self.ui.clientsTableView.model():
            self.ui.clientsTableView.selectionModel().selectionChanged.connect(
                self._on_client_selected
            )

    def _refresh_accounts(self, emit_signal=True):
        if self.controller.current_client:
            self.controller.load_client_accounts(
                self.controller.current_client.id, self.ui.accountsTableView
            )
        else:
            self.controller.current_account = None
            self.ui.accountsTableView.setModel(None)

        if emit_signal:
            self.controller.data_updated.emit()

    def _refresh_transactions(self, emit_signal=True):
        if self.controller.current_client:
            accounts = self.controller.data_service.get_client_accounts(
                self.controller.current_client.id
            )
            if self.controller.current_account:
                transactions = self.controller.data_service.get_account_transactions(
                    self.controller.current_account.id
                )
            else:
                transactions = self.controller.data_service.get_client_transactions(
                    self.controller.current_client.id
                )
        else:
            transactions = self.controller.data_service.get_all_transactions()
            accounts = []

        data = []
        for t in transactions:
            from_acc = (
                next((a for a in accounts if a and a.id == t.from_account_id), None)
                if accounts
                else None
            )
            to_acc = (
                next((a for a in accounts if a and a.id == t.to_account_id), None)
                if accounts
                else None
            )

            data.append(
                [
                    t.id,
                    from_acc.account_number if from_acc else "Внесение",
                    to_acc.account_number if to_acc else "",
                    f"{t.amount:.2f}",
                    t.transaction_type,
                    t.description or "",
                    t.transaction_date.strftime("%Y-%m-%d %H:%M"),
                    t.status,
                    t.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        headers = [
            "ID",
            "Отправитель",
            "Получатель",
            "Сумма",
            "Тип",
            "Описание",
            "Дата",
            "Статус",
            "Создана",
        ]
        model = BaseTableModel(data, headers)
        self.ui.transactionsTableView.setModel(model)

        if emit_signal:
            self.controller.data_updated.emit()

    def _show_transactions(self):
        if self.controller.current_client:
            self.ui.tabWidget.setCurrentIndex(1)
            self._refresh_transactions(True)

    def _back_to_clients(self):
        self.ui.tabWidget.setCurrentIndex(0)

    def _delete_client(self):
        selected = self.ui.clientsTableView.selectionModel().selectedRows()
        if not selected:
            self.controller.show_error("Выберите клиента для удаления")
            return
        client_id = selected[0].data()
        if self.controller.delete_client(client_id):
            self._refresh_clients(True)

    def _delete_account(self):
        if not self.controller.current_account:
            self.controller.show_error("Выберите счет для удаления")
            return
        if self.controller.delete_account(self.controller.current_account.id):
            self._refresh_accounts(True)

    def _show_about(self):
        QMessageBox.about(self, "О программе", "Банковское приложение v1.0")

    def _add_client_dialog(self):
        dialog = ClientDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if self.controller.add_client(**data):
                    self._refresh_clients(True)
            except Exception as e:
                self.controller.show_error(f"Ошибка при добавлении клиента: {str(e)}")

    def _edit_client_dialog(self):
        selected = self.ui.clientsTableView.selectionModel().selectedRows()
        if not selected:
            self.controller.show_error("Выберите клиента для редактирования")
            return

        client_id = selected[0].data()
        client = self.controller.get_client_by_id(client_id)
        if not client:
            return

        dialog = ClientDialog(self, client)
        if dialog.exec():
            data = dialog.get_data()
            if self.controller.update_client(client_id, **data):
                self._refresh_clients(True)

    def _add_account_dialog(self):
        if not self.controller.current_client:
            self.controller.show_error("Выберите клиента для добавления счета")
            return

        dialog = AccountDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if self.controller.add_account(
                    self.controller.current_client.id, **data
                ):
                    self._refresh_accounts(True)
            except Exception as e:
                self.controller.show_error(f"Ошибка при добавлении счета: {str(e)}")

    def _edit_account_dialog(self):
        if not self.controller.current_account:
            self.controller.show_error("Выберите счет для редактирования")
            return

        dialog = AccountDialog(self, self.controller.current_account)
        if dialog.exec():
            data = dialog.get_data()
            if self.controller.update_account(
                self.controller.current_account.id, **data
            ):
                self._refresh_accounts(True)

    def _add_transaction_dialog(self):
        if not self.controller.current_client:
            self.controller.show_error("Выберите клиента для добавления транзакции")
            return

        accounts = self.controller.data_service.get_client_accounts(
            self.controller.current_client.id
        )
        dialog = TransactionDialog(self, accounts=accounts)
        if dialog.exec():
            data = dialog.get_data()
            try:
                if self.controller.add_transaction(**data):
                    self._refresh_transactions(True)
            except Exception as e:
                self.controller.show_error(
                    f"Ошибка при добавлении транзакции: {str(e)}"
                )

    def _edit_transaction_dialog(self):
        selected = self.ui.transactionsTableView.selectionModel().selectedRows()
        if not selected:
            self.controller.show_error("Выберите транзакцию для редактирования")
            return

        transaction_id = selected[0].data()
        transaction = self.controller.get_transaction_by_id(transaction_id)
        if not transaction:
            return

        accounts = self.controller.data_service.get_client_accounts(
            self.controller.current_client.id
        )
        dialog = TransactionDialog(self, transaction, accounts)
        if dialog.exec():
            data = dialog.get_data()
            if self.controller.update_transaction(transaction_id, **data):
                self._refresh_transactions(True)

    def _delete_transaction(self):
        selected = self.ui.transactionsTableView.selectionModel().selectedRows()
        if not selected:
            self.controller.show_error("Выберите транзакцию для удаления")
            return

        transaction_id = selected[0].data()
        if self.controller.delete_transaction(transaction_id):
            self._refresh_transactions(True)
