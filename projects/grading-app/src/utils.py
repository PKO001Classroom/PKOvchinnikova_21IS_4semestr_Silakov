from datetime import datetime
from typing import List

def validate_date(date_str: str) -> bool:
    """Проверка формата даты ГГГГ-ММ-ДД."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_grade(grade: int) -> bool:
    """Проверка, что оценка от 2 до 5."""
    return 2 <= grade <= 5

def get_current_date() -> str:
    """Текущая дата в формате ГГГГ-ММ-ДД."""
    return datetime.now().strftime("%Y-%m-%d")

def calculate_average(grades: List[int]) -> float:
    """Расчет среднего арифметического списка оценок."""
    if not grades:
        return 0.0
    return round(sum(grades) / len(grades), 2)