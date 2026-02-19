# database.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime


class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="research_portfolio",
                user="postgres",
                password="1111",  # ЗАМЕНИТЕ НА СВОЙ ПАРОЛЬ!
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ База данных подключена!")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            self.conn = None
            self.cursor = None

    def get_all_projects(self):
        """Получение всех проектов"""
        if not self.conn:
            return []
        try:
            self.cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка загрузки проектов: {e}")
            return []

    def add_project(self, name, description, status="active"):
        """Добавление нового проекта"""
        if not self.conn:
            return None
        try:
            self.cursor.execute(
                "INSERT INTO projects (name, description, status) VALUES (%s, %s, %s) RETURNING id",
                (name, description, status)
            )
            self.conn.commit()
            return self.cursor.fetchone()['id']
        except Exception as e:
            print(f"❌ Ошибка добавления проекта: {e}")
            return None

    def update_project(self, project_id, name=None, description=None, status=None):
        """Обновление проекта"""
        if not self.conn:
            return False
        try:
            updates = []
            params = []
            if name:
                updates.append("name = %s")
                params.append(name)
            if description:
                updates.append("description = %s")
                params.append(description)
            if status:
                updates.append("status = %s")
                params.append(status)
            
            if not updates:
                return False
            
            params.append(project_id)
            query = f"UPDATE projects SET {', '.join(updates)} WHERE id = %s"
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Ошибка обновления проекта: {e}")
            return False

    def delete_project(self, project_id):
        """Удаление проекта"""
        if not self.conn:
            return False
        try:
            self.cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления проекта: {e}")
            return False