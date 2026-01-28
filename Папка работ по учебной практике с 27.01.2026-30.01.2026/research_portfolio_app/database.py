# database.py
import psycopg2
from psycopg2 import sql, Error
from datetime import datetime
import os


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="research_portfolio",
                user="postgres",
                password="1111",  # Замените на ваш пароль!
                port="5432"
            )
            print("Успешное подключение к PostgreSQL")
            self.create_tables()

        except Error as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            print("\nРЕШЕНИЕ ПРОБЛЕМ:")
            print("1. Проверьте, запущен ли сервер PostgreSQL")
            print("2. Проверьте пароль (по умолчанию часто 'postgres')")
            print("3. Создайте базу данных: CREATE DATABASE research_portfolio;")

            # Создаем базу данных, если она не существует
            self.create_database_if_not_exists()

            # Пробуем подключиться снова
            try:
                self.connection = psycopg2.connect(
                    host="localhost",
                    database="research_portfolio",
                    user="postgres",
                    password="postgres",
                    port="5432"
                )
                print("Подключение после создания БД успешно!")
                self.create_tables()
            except Error as e2:
                print(f"Критическая ошибка: {e2}")
                raise

    def create_database_if_not_exists(self):
        """Создание базы данных, если она не существует"""
        try:
            # Подключаемся к серверу PostgreSQL без указания базы данных
            conn = psycopg2.connect(
                host="localhost",
                user="postgres",
                password="postgres",
                port="5432"
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Проверяем существование базы данных
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'research_portfolio'")
            exists = cursor.fetchone()

            if not exists:
                print("Создаем базу данных research_portfolio...")
                cursor.execute("CREATE DATABASE research_portfolio")
                print("База данных research_portfolio создана")

            cursor.close()
            conn.close()

        except Error as e:
            print(f"Не удалось создать базу данных: {e}")

    def create_tables(self):
        """Создание таблиц, если они не существуют"""
        try:
            cursor = self.connection.cursor()

            # Таблица entries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    entry_type VARCHAR(50) NOT NULL,
                    file_path VARCHAR(500) UNIQUE NOT NULL,
                    year INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица coauthors
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coauthors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL
                )
            """)

            # Таблица entry_coauthors
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_coauthors (
                    entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE,
                    coauthor_id INTEGER REFERENCES coauthors(id) ON DELETE CASCADE,
                    PRIMARY KEY (entry_id, coauthor_id)
                )
            """)

            # Таблица activity_log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id SERIAL PRIMARY KEY,
                    entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE,
                    event_type VARCHAR(10) NOT NULL,
                    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            cursor.close()
            print("Таблицы созданы или уже существуют")

        except Error as e:
            print(f"Ошибка создания таблиц: {e}")
            self.connection.rollback()

    def create_entry(self, title, entry_type, year, file_path):
        """Создание новой записи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO entries (title, entry_type, year, file_path) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id
            """, (title, entry_type, year, file_path))

            entry_id = cursor.fetchone()[0]

            # Логируем создание
            self.log_activity(entry_id, "CREATE")

            self.connection.commit()
            cursor.close()
            return entry_id

        except Error as e:
            print(f"Ошибка создания записи: {e}")
            self.connection.rollback()
            return None

    def update_entry(self, entry_id, title=None, entry_type=None, year=None):
        """Обновление записи"""
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

            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(entry_id)

                query = sql.SQL("UPDATE entries SET {} WHERE id = %s").format(
                    sql.SQL(", ").join(map(sql.SQL, updates))
                )

                cursor.execute(query, params)

                # Логируем обновление
                self.log_activity(entry_id, "UPDATE")

                self.connection.commit()

            cursor.close()
            return True

        except Error as e:
            print(f"Ошибка обновления записи: {e}")
            self.connection.rollback()
            return False

    def update_entry_file_path(self, entry_id, file_path):
        """Обновление пути к файлу записи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE entries 
                SET file_path = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (file_path, entry_id))

            self.connection.commit()
            cursor.close()
            return True

        except Error as e:
            print(f"Ошибка обновления пути к файлу: {e}")
            self.connection.rollback()
            return False

    def delete_entry(self, entry_id):
        """Удаление записи"""
        try:
            cursor = self.connection.cursor()

            # Получаем путь к файлу перед удалением
            cursor.execute("SELECT file_path FROM entries WHERE id = %s", (entry_id,))
            result = cursor.fetchone()

            if result:
                file_path = result[0]
            else:
                file_path = None

            # Удаляем запись (каскадно удалятся связи и логи)
            cursor.execute("DELETE FROM entries WHERE id = %s", (entry_id,))

            self.connection.commit()
            cursor.close()

            return file_path

        except Error as e:
            print(f"Ошибка удаления записи: {e}")
            self.connection.rollback()
            return None

    def get_all_entries(self):
        """Получение всех записей"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, title, entry_type, year, 
                       TO_CHAR(created_at, 'DD.MM.YYYY HH24:MI') as created_at
                FROM entries 
                ORDER BY created_at DESC
            """)

            entries = cursor.fetchall()
            cursor.close()
            return entries

        except Error as e:
            print(f"Ошибка получения записей: {e}")
            return []

    def get_entry_by_id(self, entry_id):
        """Получение записи по ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, title, entry_type, year, file_path
                FROM entries 
                WHERE id = %s
            """, (entry_id,))

            entry = cursor.fetchone()
            cursor.close()
            return entry

        except Error as e:
            print(f"Ошибка получения записи: {e}")
            return None

    def add_coauthor(self, entry_id, coauthor_name):
        """Добавление соавтора к записи"""
        try:
            cursor = self.connection.cursor()

            # Проверяем, существует ли соавтор
            cursor.execute("SELECT id FROM coauthors WHERE name = %s", (coauthor_name,))
            result = cursor.fetchone()

            if result:
                coauthor_id = result[0]
            else:
                # Создаем нового соавтора
                cursor.execute(
                    "INSERT INTO coauthors (name) VALUES (%s) RETURNING id",
                    (coauthor_name,)
                )
                coauthor_id = cursor.fetchone()[0]

            # Добавляем связь
            cursor.execute("""
                INSERT INTO entry_coauthors (entry_id, coauthor_id)
                VALUES (%s, %s)
                ON CONFLICT (entry_id, coauthor_id) DO NOTHING
            """, (entry_id, coauthor_id))

            self.connection.commit()
            cursor.close()
            return True

        except Error as e:
            print(f"Ошибка добавления соавтора: {e}")
            self.connection.rollback()
            return False

    def get_coauthors_by_entry(self, entry_id):
        """Получение соавторов записи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT c.name 
                FROM coauthors c
                JOIN entry_coauthors ec ON c.id = ec.coauthor_id
                WHERE ec.entry_id = %s
            """, (entry_id,))

            coauthors = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return coauthors

        except Error as e:
            print(f"Ошибка получения соавторов: {e}")
            return []

    def log_activity(self, entry_id, event_type):
        """Логирование активности"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO activity_log (entry_id, event_type)
                VALUES (%s, %s)
            """, (entry_id, event_type))

            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"Ошибка логирования: {e}")
            self.connection.rollback()

    def get_statistics(self):
        """Получение статистики для отчётов"""
        try:
            cursor = self.connection.cursor()
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
            cursor.execute("SELECT COUNT(DISTINCT name) FROM coauthors")
            stats['unique_coauthors'] = cursor.fetchone()[0]

            # Активность за последние 12 месяцев
            cursor.execute("""
                SELECT DATE_TRUNC('month', event_time) as month, 
                       COUNT(*) as count
                FROM activity_log 
                WHERE event_time >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY month 
                ORDER BY month
            """)
            stats['activity_last_12_months'] = cursor.fetchall()

            # Последние 5 записей
            cursor.execute("""
                SELECT title, entry_type, year 
                FROM entries 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            stats['last_5_entries'] = cursor.fetchall()

            cursor.close()
            return stats

        except Error as e:
            print(f"Ошибка получения статистики: {e}")
            return {}

    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            print("Соединение с PostgreSQL закрыто")


# Создаем глобальный экземпляр для использования в приложении
db_manager = DatabaseManager()