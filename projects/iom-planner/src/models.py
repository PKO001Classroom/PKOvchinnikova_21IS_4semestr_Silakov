"""
Модуль с моделями данных (датаклассы)
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Goal:
    """Модель цели"""
    id: Optional[int]
    title: str
    type: str
    status: str
    plan_date: Optional[str]
    fact_date: Optional[str]
    temp: Optional[str]
    description: Optional[str]
    skills: List[str] = None
    competencies: List[tuple] = None

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Goal':
        """Создание объекта из строки БД (полная строка из SELECT * FROM цели)"""
        return cls(
            id=row[0],
            title=row[1],
            type=row[2],
            status=row[3],
            plan_date=row[4],
            fact_date=row[5],
            temp=row[6],
            description=row[7],
            skills=[],
            competencies=[]
        )

    @classmethod
    def from_tree_row(cls, row: tuple) -> 'Goal':
        """Создание объекта из строки дерева (id, название, тип, статус)"""
        return cls(
            id=row[0],
            title=row[1],
            type=row[2],
            status=row[3],
            plan_date=None,
            fact_date=None,
            temp=None,
            description=None
        )

    def display_string(self) -> str:
        """Строка для отображения в списке"""
        return f"[{self.id}] {self.title} ({self.type}) - {self.status}"


@dataclass
class Skill:
    """Модель навыка"""
    id: Optional[int]
    name: str
    goals_count: int = 0

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Skill':
        """Создание объекта из строки БД"""
        return cls(
            id=row[0],
            name=row[1]
        )


@dataclass
class Competency:
    """Модель компетенции"""
    id: Optional[int]
    name: str
    category: str
    average_level: float = 0.0

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Competency':
        """Создание объекта из строки БД (id, название, категория)"""
        return cls(
            id=row[0],
            name=row[1],
            category=row[2]
        )

    @classmethod
    def from_stats_row(cls, row: tuple) -> 'Competency':
        """Создание объекта из строки со статистикой (название, категория, средний уровень)"""
        return cls(
            id=None,
            name=row[0],
            category=row[1],
            average_level=row[2] if row[2] else 0.0
        )


@dataclass
class Achievement:
    """Модель достижения"""
    code: str
    name: str
    description: str
    obtained: bool

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Achievement':
        """Создание объекта из строки БД"""
        return cls(
            code=row[0],
            name=row[1],
            description=row[2],
            obtained=bool(row[3])
        )

    def status_display(self) -> str:
        """Строка статуса для отображения"""
        return "✓ Получено" if self.obtained else "✗ Не получено"


@dataclass
class SemesterGoal:
    """Модель цели на семестр"""
    id: Optional[int]
    text: str
    goal_type: str
    param: Optional[str]
    current_progress: int
    target_progress: int

    @classmethod
    def from_db_row(cls, row: tuple) -> 'SemesterGoal':
        """Создание объекта из строки БД"""
        return cls(
            id=row[0],
            text=row[1],
            goal_type=row[2],
            param=row[3],
            current_progress=row[4],
            target_progress=row[5]
        )

    def progress_display(self) -> str:
        """Строка прогресса для отображения"""
        return f"{self.current_progress} из {self.target_progress}"

    def is_completed(self) -> bool:
        """Проверка, достигнута ли цель"""
        return self.current_progress >= self.target_progress