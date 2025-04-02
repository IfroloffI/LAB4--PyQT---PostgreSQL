from typing import Optional
from app.core.database.connection import DatabaseConnection
from app.core.database.models import Record


class DataService:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_records(self) -> list[Record]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, description, created_at, updated_at 
                    FROM records 
                    ORDER BY created_at DESC
                """
                )
                return [Record(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении записей: {e}")
            return []

    def get_record_by_id(self, record_id: int) -> Optional[Record]:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, description, created_at, updated_at 
                    FROM records 
                    WHERE id = %s
                """,
                    (record_id,),
                )
                result = cursor.fetchone()
                return Record(*result) if result else None
        except Exception as e:
            print(f"Ошибка при получении записи {record_id}: {e}")
            return None

    def add_record(self, title: str, description: str) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO records (title, description) 
                    VALUES (%s, %s) 
                    RETURNING id
                """,
                    (title, description),
                )
                self.db.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            self.db.connection.rollback()
            return False

    def update_record(self, record_id: int, title: str, description: str) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE records 
                    SET title = %s, description = %s, updated_at = NOW() 
                    WHERE id = %s
                """,
                    (title, description, record_id),
                )
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении записи {record_id}: {e}")
            self.db.connection.rollback()
            return False

    def delete_record(self, record_id: int) -> bool:
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM records 
                    WHERE id = %s
                """,
                    (record_id,),
                )
                self.db.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при удалении записи {record_id}: {e}")
            self.db.connection.rollback()
            return False
