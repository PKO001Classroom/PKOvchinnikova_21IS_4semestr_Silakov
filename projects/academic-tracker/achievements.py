from database import Database
from datetime import datetime


class AchievementTracker:
    def __init__(self, db):
        self.db = db

    def check_achievements(self):
        """Проверка всех достижений"""
        new_achievements = []

        # Проверка "Первый шаг"
        if not self.db.get_achievement_status("Первый шаг"):
            entries = self.db.get_all_entries()
            if len(entries) >= 1:
                if self.db.unlock_achievement("Первый шаг"):
                    new_achievements.append("Первый шаг")

        # Проверка "Командный игрок"
        if not self.db.get_achievement_status("Командный игрок"):
            team_entries = self.db.count_entries_with_authors()
            if team_entries >= 3:
                if self.db.unlock_achievement("Командный игрок"):
                    new_achievements.append("Командный игрок")

        # Проверка "Разносторонний"
        if not self.db.get_achievement_status("Разносторонний"):
            types_count = self.db.get_entry_types_count()
            if types_count >= 3:
                if self.db.unlock_achievement("Разносторонний"):
                    new_achievements.append("Разносторонний")

        # Проверка "Подготовленный год"
        if not self.db.get_achievement_status("Подготовленный год"):
            current_year = datetime.now().year
            entries_this_year = self.db.get_entries_by_year(current_year)
            if entries_this_year >= 3:
                if self.db.unlock_achievement("Подготовленный год"):
                    new_achievements.append("Подготовленный год")

        # Проверка "Словобог"
        if not self.db.get_achievement_status("Словобог"):
            total_length = self.db.get_total_description_length()
            if total_length >= 5000:
                if self.db.unlock_achievement("Словобог"):
                    new_achievements.append("Словобог")

        return new_achievements

    def get_all_achievements(self):
        """Получение всех достижений"""
        return self.db.get_achievements()