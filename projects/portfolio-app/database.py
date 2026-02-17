# database.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime


class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="research_portfolio",
                user="postgres",
                password="1111"  # ЗАМЕНИТЕ НА СВОЙ ПАРОЛЬ!
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ База данных подключена!")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            raise

    def create_entry(self, title, entry_type, year, file_path):
        """Создание новой записи"""
        query = """
        INSERT INTO entries (title, entry_type, year, file_path) 
        VALUES (%s, %s, %s, %s) RETURNING id
        """
        self.cursor.execute(query, (title, entry_type, year, file_path))
        entry_id = self.cursor.fetchone()['id']
        self.conn.commit()

        # Логируем создание
        log_query = "INSERT INTO activity_log (entry_id, event_type) VALUES (%s, 'CREATE')"
        self.cursor.execute(log_query, (entry_id,))
        self.conn.commit()

        return entry_id

    def get_all_entries(self):
        """Получение всех записей"""
        query = "SELECT * FROM entries ORDER BY created_at DESC"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_entry(self, entry_id, title, entry_type, year):
        """Обновление записи"""
        query = """
        UPDATE entries 
        SET title=%s, entry_type=%s, year=%s, updated_at=NOW() 
        WHERE id=%s
        """
        self.cursor.execute(query, (title, entry_type, year, entry_id))
        self.conn.commit()

        # Логируем обновление
        log_query = "INSERT INTO activity_log (entry_id, event_type) VALUES (%s, 'UPDATE')"
        self.cursor.execute(log_query, (entry_id,))
        self.conn.commit()

    def delete_entry(self, entry_id):
        """Удаление записи"""
        query = "DELETE FROM entries WHERE id=%s"
        self.cursor.execute(query, (entry_id,))
        self.conn.commit()

        print(f"Запись {entry_id} удалена из БД")

    def add_coauthor(self, entry_id, name):
        """Добавление соавтора"""
        try:
            # 1. Проверяем есть ли соавтор
            query = "SELECT id FROM coauthors WHERE name=%s"
            self.cursor.execute(query, (name,))
            result = self.cursor.fetchone()

            if result:
                coauthor_id = result['id']
            else:
                # 2. Если нет - создаем
                query = "INSERT INTO coauthors (name) VALUES (%s) RETURNING id"
                self.cursor.execute(query, (name,))
                coauthor_id = self.cursor.fetchone()['id']

            # 3. Связываем с записью
            query = """
            INSERT INTO entry_coauthors (entry_id, coauthor_id) 
            VALUES (%s, %s)
            ON CONFLICT (entry_id, coauthor_id) DO NOTHING
            """
            self.cursor.execute(query, (entry_id, coauthor_id))
            self.conn.commit()

            print(f"Соавтор '{name}' добавлен к записи {entry_id}")

        except Exception as e:
            print(f"Ошибка добавления соавтора: {e}")
            raise

    def get_coauthors(self, entry_id):
        """Получение соавторов записи"""
        query = """
        SELECT c.name FROM coauthors c
        JOIN entry_coauthors ec ON c.id = ec.coauthor_id
        WHERE ec.entry_id = %s
        """
        self.cursor.execute(query, (entry_id,))
        results = self.cursor.fetchall()
        return [row['name'] for row in results]

    def get_statistics(self):
        """Получение статистики для отчетов"""
        try:
            # Статистика по типам
            query = "SELECT entry_type, COUNT(*) as count FROM entries GROUP BY entry_type"
            self.cursor.execute(query)
            by_type = self.cursor.fetchall()

            # Общее количество
            query = "SELECT COUNT(*) as total FROM entries"
            self.cursor.execute(query)
            total_result = self.cursor.fetchone()
            total = total_result['total'] if total_result else 0

            # По годам
            query = """
            SELECT year, COUNT(*) as count 
            FROM entries 
            WHERE year IS NOT NULL 
            GROUP BY year ORDER BY year
            """
            self.cursor.execute(query)
            by_year = self.cursor.fetchall()

            # Последние записи
            query = """
            SELECT id, title, entry_type, year, created_at 
            FROM entries 
            ORDER BY created_at DESC 
            LIMIT 5
            """
            self.cursor.execute(query)
            recent_entries = self.cursor.fetchall()

            # Уникальные соавторы
            query = "SELECT COUNT(DISTINCT name) as count FROM coauthors"
            self.cursor.execute(query)
            coauthors_result = self.cursor.fetchone()
            unique_coauthors = coauthors_result['count'] if coauthors_result else 0

            return {
                'by_type': by_type,
                'by_year': by_year,
                'recent_entries': recent_entries,
                'total': total,
                'unique_coauthors': unique_coauthors
            }

        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {
                'by_type': [],
                'by_year': [],
                'recent_entries': [],
                'total': 0,
                'unique_coauthors': 0
            }

    def close(self):
        """Закрытие соединения"""
        self.cursor.close()
        self.conn.close()
        print("Соединение с БД закрыто")


# Для тестирования
if __name__ == "__main__":
    db = Database()
    print("Тест БД: OK")
    db.close()