from datetime import datetime


class Entry:
    def __init__(self, title, entry_type, date, description="", authors=""):
        self.title = title
        self.type = entry_type
        self.date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
        self.description = description
        self.authors = authors
        self.keywords = []
        self.competencies = []

    def __str__(self):
        return f"{self.title} ({self.type}) - {self.date.strftime('%Y-%m-%d')}"

    def to_dict(self):
        return {
            'id': getattr(self, 'id', None),
            'название': self.title,
            'тип': self.type,
            'дата': self.date.strftime("%Y-%m-%d"),
            'описание': self.description,
            'соавторы': self.authors,
            'ключевые_слова': ', '.join(self.keywords) if self.keywords else None
        }


class Achievement:
    def __init__(self, name, description, obtained=False, date_obtained=None):
        self.name = name
        self.description = description
        self.obtained = obtained
        self.date_obtained = date_obtained

    def __str__(self):
        status = "✅" if self.obtained else "◻"
        return f"{status} {self.name}: {self.description}"


class Competency:
    def __init__(self, name, category=None, level=None):
        self.name = name
        self.category = category
        self.level = level

    def __str__(self):
        level_str = f" (уровень: {self.level}/5)" if self.level else ""
        return f"{self.name}{level_str}"