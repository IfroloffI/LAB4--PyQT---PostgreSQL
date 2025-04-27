from typing import Optional, List
from app.core.database.connection import DatabaseConnection
from app.core.database.models import Client, Account, Transaction


class DataService:
    def __init__(self):
        self.db = DatabaseConnection()

    def client_exists(self, client_id: int) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("SELECT 1 FROM clients WHERE id = %s", (client_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Ошибка проверки клиента: {e}")
            return False

    def account_exists(self, account_id: int) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("SELECT 1 FROM accounts WHERE id = %s", (account_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Ошибка проверки счета: {e}")
            return False

    def get_all_clients(self) -> List[Client]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, first_name, last_name, passport_number, 
                           phone_number, email, created_at, updated_at 
                    FROM clients 
                    ORDER BY last_name, first_name
                """
                )
                return [Client(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении клиентов: {e}")
            return []

    def get_client_by_id(self, client_id: int) -> Optional[Client]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, first_name, last_name, passport_number, 
                           phone_number, email, created_at, updated_at 
                    FROM clients 
                    WHERE id = %s
                """,
                    (client_id,),
                )
                result = cursor.fetchone()
                return Client(*result) if result else None
        except Exception as e:
            print(f"Ошибка при получении клиента {client_id}: {e}")
            return None

    def add_client(self, **data) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM clients WHERE passport_number = %s",
                    (data["passport_number"],),
                )
                if cursor.fetchone():
                    raise Exception("Клиент с таким паспортом уже существует")

                cursor.execute(
                    """
                    INSERT INTO clients 
                    (first_name, last_name, passport_number, phone_number, email) 
                    VALUES (%s, %s, %s, %s, %s) 
                    RETURNING id
                    """,
                    (
                        data["first_name"],
                        data["last_name"],
                        data["passport_number"],
                        data.get("phone_number"),
                        data.get("email"),
                    ),
                )
                self.db.connection.commit()
                return True
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Ошибка добавления клиента: {str(e)}")

    def update_client(
        self,
        client_id: int,
        first_name: str,
        last_name: str,
        passport_number: str,
        phone_number: str = None,
        email: str = None,
    ) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE clients 
                    SET first_name = %s, last_name = %s, passport_number = %s, 
                        phone_number = %s, email = %s, updated_at = NOW() 
                    WHERE id = %s
                """,
                    (
                        first_name,
                        last_name,
                        passport_number,
                        phone_number,
                        email,
                        client_id,
                    ),
                )
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении клиента {client_id}: {e}")
            self.db.connection.rollback()
            return False

    def delete_client(self, client_id: int) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при удалении клиента {client_id}: {e}")
            self.db.connection.rollback()
            return False

    def get_client_accounts(self, client_id: int) -> List[Account]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, client_id, account_number, account_type, 
                           balance, currency, opened_date, is_active, created_at, updated_at 
                    FROM accounts 
                    WHERE client_id = %s
                    ORDER BY opened_date DESC
                """,
                    (client_id,),
                )
                return [Account(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении счетов клиента {client_id}: {e}")
            return []

    def add_account(self, client_id: int, **data) -> bool:
        try:
            if not self.client_exists(client_id):
                raise Exception("Клиент не существует")

            with self.db.get_cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM accounts WHERE account_number = %s",
                    (data["account_number"],),
                )
                if cursor.fetchone():
                    raise Exception("Счет с таким номером уже существует")

                cursor.execute(
                    """
                    INSERT INTO accounts 
                    (client_id, account_number, account_type, 
                     balance, currency, is_active, opened_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
                    RETURNING id
                    """,
                    (
                        client_id,
                        data["account_number"],
                        data["account_type"],
                        data["balance"],
                        data["currency"],
                        data["is_active"],
                    ),
                )
                self.db.connection.commit()
                return True
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Ошибка добавления счета: {str(e)}")

    def update_account(
        self,
        account_id: int,
        account_number: str,
        account_type: str,
        balance: float,
        currency: str,
        is_active: bool,
    ) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE accounts 
                    SET account_number = %s, account_type = %s, balance = %s, 
                        currency = %s, is_active = %s, updated_at = NOW() 
                    WHERE id = %s
                """,
                    (
                        account_number,
                        account_type,
                        balance,
                        currency,
                        is_active,
                        account_id,
                    ),
                )
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении счета {account_id}: {e}")
            self.db.connection.rollback()
            return False

    def delete_account(self, account_id: int) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("DELETE FROM accounts WHERE id = %s", (account_id,))
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при удалении счета {account_id}: {e}")
            self.db.connection.rollback()
            return False

    def get_account_transactions(self, account_id: int) -> List[Transaction]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, from_account_id, to_account_id, amount, 
                           transaction_type, description, transaction_date, status, created_at 
                    FROM transactions 
                    WHERE from_account_id = %s OR to_account_id = %s
                    ORDER BY transaction_date DESC
                """,
                    (account_id, account_id),
                )
                return [Transaction(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении транзакций счета {account_id}: {e}")
            return []

    def get_client_transactions(self, client_id: int) -> List[Transaction]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT t.id, t.from_account_id, t.to_account_id, t.amount, 
                           t.transaction_type, t.description, t.transaction_date, t.status, t.created_at 
                    FROM transactions t
                    JOIN accounts a ON a.id = t.from_account_id OR a.id = t.to_account_id
                    WHERE a.client_id = %s
                    ORDER BY t.transaction_date DESC
                """,
                    (client_id,),
                )
                return [Transaction(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении транзакций клиента {client_id}: {e}")
            return []

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, client_id, account_number, account_type, 
                           balance, currency, opened_date, is_active, created_at, updated_at 
                    FROM accounts 
                    WHERE id = %s
                """,
                    (account_id,),
                )
                result = cursor.fetchone()
                return Account(*result) if result else None
        except Exception as e:
            print(f"Ошибка при получении счета {account_id}: {e}")
            return None

    def add_transaction(self, **data) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO transactions 
                    (from_account_id, to_account_id, amount, transaction_type, description)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        data["from_account_id"],
                        data["to_account_id"],
                        data["amount"],
                        data["transaction_type"],
                        data["description"],
                    ),
                )
                self.db.connection.commit()
                return True
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Ошибка при добавлении транзакции: {str(e)}")

    def update_transaction(self, transaction_id: int, **data) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE transactions SET
                    from_account_id = %s,
                    to_account_id = %s,
                    amount = %s,
                    transaction_type = %s,
                    description = %s
                    WHERE id = %s
                    """,
                    (
                        data["from_account_id"],
                        data["to_account_id"],
                        data["amount"],
                        data["transaction_type"],
                        data["description"],
                        transaction_id,
                    ),
                )
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Ошибка при обновлении транзакции: {str(e)}")

    def delete_transaction(self, transaction_id: int) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    "DELETE FROM transactions WHERE id = %s",
                    (transaction_id,),
                )
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.db.connection.rollback()
            raise Exception(f"Ошибка при удалении транзакции: {str(e)}")

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, from_account_id, to_account_id, amount,
                           transaction_type, description, transaction_date, status, created_at
                    FROM transactions
                    WHERE id = %s
                    """,
                    (transaction_id,),
                )
                result = cursor.fetchone()
                return Transaction(*result) if result else None
        except Exception as e:
            raise Exception(f"Ошибка при получении транзакции: {str(e)}")

    def get_all_transactions(self) -> List[Transaction]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, from_account_id, to_account_id, amount, 
                        transaction_type, description, transaction_date, status, created_at 
                    FROM transactions 
                    ORDER BY transaction_date DESC
                    """
                )
                return [Transaction(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении всех транзакций: {e}")
            return []
