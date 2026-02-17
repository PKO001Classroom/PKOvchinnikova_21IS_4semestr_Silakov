"""
Модуль с моделями данных
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Achievement:
    """Модель достижения"""
    id: Optional[int]
    title: str
    date: str
    type: str
    level: str
    description: str
    
    @classmethod
    def from_db_row(cls, row: tuple) -> 'Achievement':
        """Создание объекта из строки БД"""
        return cls(
            id=row[0],
            title=row[1],
            date=row[2],
            type=row[3],
            level=row[4],
            description=row[5]
        )
    
    def display_string(self) -> str:
        """Строка для отображения в списке"""
        short_title = self.title[:50] + ('...' if len(self.title) > 50 else '')
        return f"{self.date} | {short_title} | {self.type} | {self.level}"