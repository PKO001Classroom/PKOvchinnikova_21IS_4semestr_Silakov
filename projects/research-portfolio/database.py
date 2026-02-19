"""
Модуль для работы с базой данных PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=Config.DB_HOST,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                port=Config.DB_PORT
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            self.create_tables()
            print("✅ Успешное подключение к PostgreSQL")
        except Exception as e:
            print(f"❌ Ошибка подключения к PostgreSQL: {e}")
            self.connection = None
            self.cursor = None

    def create_tables(self):
        """Создание таблиц, если они не существуют"""
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()

            # Таблица записей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    entry_type TEXT NOT NULL,
                    year INTEGER,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица соавторов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coauthors (
                    id SERIAL PRIMARY KEY,
                    entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    affiliation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица активности
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id SERIAL PRIMARY KEY,
                    entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE,
                    event_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            print("✅ Таблицы созданы или уже существуют")

        except Exception as e:
            print(f"❌ Ошибка при создании таблиц: {e}")
            if self.connection:
                self.connection.rollback()

    def create_entry(self, title, entry_type, year, file_path):
        """Создание новой записи"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO entries (title, entry_type, year, file_path)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (title, entry_type, year, file_path))

            result = cursor.fetchone()
            entry_id = result['id'] if result else None

            self.connection.commit()
            print(f"✅ Запись создана с ID: {entry_id}")
            return entry_id

        except Exception as e:
            print(f"❌ Ошибка при создании записи: {e}")
            if self.connection:
                self.connection.rollback()
            return None

    def update_entry(self, entry_id, title=None, entry_type=None, year=None):
        """Обновление записи"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return False

        try:
            cursor = self.connection.cursor()
            updates = []
            params = []

            if title:
                updates.append("title = %s")
                params.append(title)
            if entry_type:
                updates.append("entry_type = %s")
                params.append(entry_type)
            if year:
                updates.append("year = %s")
                params.append(year)

            if not updates:
                return True

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(entry_id)

            query = f"UPDATE entries SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.connection.commit()
            print(f"✅ Запись {entry_id} обновлена")
            return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении записи: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def update_entry_file_path(self, entry_id, file_path):
        """Обновление пути к файлу записи"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE entries
                SET file_path = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (file_path, entry_id))
            self.connection.commit()
            print(f"✅ Путь к файлу для записи {entry_id} обновлен")
            return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении пути к файлу: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def delete_entry(self, entry_id):
        """Удаление записи"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM entries WHERE id = %s", (entry_id,))
            self.connection.commit()
            print(f"✅ Запись {entry_id} удалена")
            return True

        except Exception as e:
            print(f"❌ Ошибка при удалении записи: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_all_entries(self):
        """Получение всех записей"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return []

        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM entries
                ORDER BY created_at DESC
            """)
            return cursor.fetchall()

        except Exception as e:
            print(f"❌ Ошибка при получении записей: {e}")
            return []

    def get_entry_by_id(self, entry_id):
        """Получение записи по ID"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return None

        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM entries WHERE id = %s", (entry_id,))
            return cursor.fetchone()

        except Exception as e:
            print(f"❌ Ошибка при получении записи: {e}")
            return None

    def add_coauthor(self, entry_id, coauthor_name):
        """Добавление соавтора к записи"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO coauthors (entry_id, name)
                VALUES (%s, %s)
                RETURNING id
            """, (entry_id, coauthor_name))

            result = cursor.fetchone()
            coauthor_id = result['id'] if result else None

            self.connection.commit()
            print(f"✅ Соавтор добавлен с ID: {coauthor_id}")
            return coauthor_id

        except Exception as e:
            print(f"❌ Ошибка при добавлении соавтора: {e}")
            if self.connection:
                self.connection.rollback()
            return None

    def get_coauthors_by_entry(self, entry_id):
        """Получение соавторов записи"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return []

        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM coauthors
                WHERE entry_id = %s
                ORDER BY created_at
            """, (entry_id,))
            return cursor.fetchall()

        except Exception as e:
            print(f"❌ Ошибка при получении соавторов: {e}")
            return []

    def log_activity(self, entry_id, event_type):
        """Логирование активности"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO activity_log (entry_id, event_type)
                VALUES (%s, %s)
            """, (entry_id, event_type))
            self.connection.commit()
            return True

        except Exception as e:
            print(f"❌ Ошибка при логировании активности: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_statistics(self):
        """Получение статистики для отчётов"""
        if not self.connection:
            print("❌ Нет подключения к БД")
            return {
                'by_type': {},
                'by_year': {},
                'unique_coauthors': 0,
                'activity_last_12_months': []
            }

        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            stats = {}

            # Количество записей по типам
            cursor.execute("""
                SELECT entry_type, COUNT(*)
                FROM entries
                GROUP BY entry_type
            """)
            stats['by_type'] = dict(cursor.fetchall())

            # Количество записей по годам
            cursor.execute("""
                SELECT year, COUNT(*)
                FROM entries
                GROUP BY year
                ORDER BY year
            """)
            stats['by_year'] = dict(cursor.fetchall())

            # Количество уникальных соавторов
            cursor.execute("SELECT COUNT(DISTINCT name) as unique_coauthors FROM coauthors")
            result = cursor.fetchone()
            stats['unique_coauthors'] = result['unique_coauthors'] if result else 0

            # Активность за последние 12 месяцев
            cursor.execute("""
                SELECT TO_CHAR(created_at, 'YYYY-MM') as month, COUNT(*)
                FROM activity_log
                WHERE created_at > CURRENT_DATE - INTERVAL '12 months'
                GROUP BY month
                ORDER BY month
            """)
            stats['activity_last_12_months'] = cursor.fetchall()

            return stats

        except Exception as e:
            print(f"❌ Ошибка при получении статистики: {e}")
            return {
                'by_type': {},
                'by_year': {},
                'unique_coauthors': 0,
                'activity_last_12_months': []
            }

    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            print("✅ Соединение с БД закрыто")