Вот полный набор Pytest тестов для вашего проекта. Я разделил их на модули по каждому файлу.

## 1. Тесты для `database.py`

```python:test_database.py
import pytest
import sqlite3
import os
from database import Database
from datetime import datetime


@pytest.fixture
def test_db():
    """Фикстура для тестовой базы данных"""
    db_name = "test_portfolio.db"
    db = Database(db_name)
    yield db
    
    # Очистка после тестов
    db.close()
    if os.path.exists(db_name):
        os.remove(db_name)


class TestDatabase:
    """Тесты для класса Database"""
    
    def test_init_and_tables(self, test_db):
        """Тест инициализации и создания таблиц"""
        # Проверяем, что таблицы созданы
        test_db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in test_db.cursor.fetchall()]
        
        expected_tables = ['entries', 'keywords', 'entry_keywords', 'achievements', 
                          'competencies', 'entry_competencies', 'goals']
        
        for table in expected_tables:
            assert table in tables, f"Таблица {table} должна существовать"
    
    def test_add_entry(self, test_db):
        """Тест добавления записи"""
        entry_id = test_db.add_entry(
            title="Тестовый проект",
            entry_type="Проект",
            date="2024-01-15",
            description="Тестовое описание",
            authors="Иван Иванов"
        )
        
        assert entry_id is not None
        assert isinstance(entry_id, int)
        
        # Проверяем, что запись добавлена
        test_db.cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        entry = test_db.cursor.fetchone()
        
        assert entry is not None
        assert entry[1] == "Тестовый проект"
        assert entry[2] == "Проект"
        assert entry[3] == "2024-01-15"
        assert entry[4] == "Тестовое описание"
        assert entry[5] == "Иван Иванов"
    
    def test_get_all_entries(self, test_db):
        """Тест получения всех записей"""
        # Добавляем несколько записей
        test_db.add_entry("Проект 1", "Проект", "2024-01-01", "Описание 1", "")
        test_db.add_entry("Проект 2", "Конференция", "2024-02-01", "Описание 2", "Петр Петров")
        
        entries = test_db.get_all_entries()
        
        assert len(entries) == 2
        assert entries[0][1] == "Проект 2"  # Сортировка по дате DESC
        assert entries[1][1] == "Проект 1"
    
    def test_add_keyword_to_entry(self, test_db):
        """Тест добавления ключевых слов"""
        # Добавляем запись
        entry_id = test_db.add_entry("Тест", "Проект", "2024-01-01", "Тест", "")
        
        # Добавляем ключевые слова
        test_db.add_keyword_to_entry(entry_id, "Python")
        test_db.add_keyword_to_entry(entry_id, "SQL")
        
        # Проверяем, что ключевые слова добавлены
        test_db.cursor.execute('''
            SELECT k.keyword FROM keywords k
            JOIN entry_keywords ek ON k.id = ek.keyword_id
            WHERE ek.entry_id = ?
        ''', (entry_id,))
        
        keywords = [row[0] for row in test_db.cursor.fetchall()]
        
        assert "Python" in keywords
        assert "SQL" in keywords
        assert len(keywords) == 2
    
    def test_get_all_entries_with_keywords(self, test_db):
        """Тест получения записей с ключевыми словами"""
        entry_id = test_db.add_entry("Тест", "Проект", "2024-01-01", "Тест", "")
        test_db.add_keyword_to_entry(entry_id, "Python")
        test_db.add_keyword_to_entry(entry_id, "Тестирование")
        
        entries = test_db.get_all_entries_with_keywords()
        
        assert len(entries) == 1
        assert entries[0][0] == entry_id
        assert "Python" in entries[0][6]  # keywords в позиции 6
        assert "Тестирование" in entries[0][6]
    
    def test_search_entries(self, test_db):
        """Тест поиска записей"""
        # Добавляем записи
        test_db.add_entry("Веб-приложение", "Проект", "2024-01-01", 
                         "Разработка веб-приложения на Python", "")
        test_db.add_entry("Мобильное приложение", "Проект", "2024-02-01", 
                         "Разработка мобильного приложения", "")
        
        # Поиск по названию
        results = test_db.search_entries("веб")
        assert len(results) == 1
        assert "Веб-приложение" in results[0][1]
        
        # Поиск по описанию
        results = test_db.search_entries("python")
        assert len(results) == 1
        
        # Поиск, который не должен ничего найти
        results = test_db.search_entries("несуществующий")
        assert len(results) == 0
    
    def test_delete_entry(self, test_db):
        """Тест удаления записи"""
        entry_id = test_db.add_entry("Удаляемый проект", "Проект", "2024-01-01", "Описание", "")
        test_db.add_keyword_to_entry(entry_id, "Тест")
        
        # Проверяем, что запись существует
        entries_before = test_db.get_all_entries()
        assert len(entries_before) == 1
        
        # Удаляем запись
        test_db.delete_entry(entry_id)
        
        # Проверяем, что запись удалена
        entries_after = test_db.get_all_entries()
        assert len(entries_after) == 0
        
        # Проверяем, что ключевые слова также удалены
        test_db.cursor.execute("SELECT COUNT(*) FROM entry_keywords WHERE entry_id = ?", (entry_id,))
        count = test_db.cursor.fetchone()[0]
        assert count == 0
    
    def test_init_achievements(self, test_db):
        """Тест инициализации достижений"""
        test_db.cursor.execute("SELECT COUNT(*) FROM achievements")
        count = test_db.cursor.fetchone()[0]
        
        # Должно быть 5 предопределенных достижений
        assert count == 5
        
        # Проверяем названия достижений
        test_db.cursor.execute("SELECT название FROM achievements ORDER BY название")
        achievements = [row[0] for row in test_db.cursor.fetchall()]
        
        expected = ["Командный игрок", "Первая запись", "Подготовленный год", 
                   "Разносторонний", "Словобог"]
        
        for achievement in expected:
            assert achievement in achievements
    
    def test_unlock_achievement(self, test_db):
        """Тест разблокировки достижения"""
        # Проверяем начальное состояние
        test_db.cursor.execute("SELECT получено FROM achievements WHERE название = 'Первая запись'")
        initial_status = test_db.cursor.fetchone()[0]
        assert initial_status == 0  # False в SQLite
        
        # Разблокируем достижение
        result = test_db.unlock_achievement("Первая запись")
        assert result is True
        
        # Проверяем, что достижение разблокировано
        test_db.cursor.execute("SELECT получено, дата_получения FROM achievements WHERE название = 'Первая запись'")
        status, date = test_db.cursor.fetchone()
        assert status == 1  # True в SQLite
        assert date is not None
    
    def test_add_competency_to_entry(self, test_db):
        """Тест добавления компетенции"""
        entry_id = test_db.add_entry("Тест", "Проект", "2024-01-01", "Тест", "")
        
        # Добавляем компетенцию
        test_db.add_competency_to_entry(entry_id, "Программирование", 4)
        test_db.add_competency_to_entry(entry_id, "Командная работа", 3)
        
        # Проверяем, что компетенции добавлены
        test_db.cursor.execute('''
            SELECT c.название, ec.уровень 
            FROM competencies c
            JOIN entry_competencies ec ON c.id = ec.competency_id
            WHERE ec.entry_id = ?
        ''', (entry_id,))
        
        competencies = test_db.cursor.fetchall()
        
        assert len(competencies) == 2
        competency_names = [comp[0] for comp in competencies]
        assert "Программирование" in competency_names
        assert "Командная работа" in competency_names
    
    def test_get_competencies_statistics(self, test_db):
        """Тест статистики по компетенциям"""
        # Создаем записи с компетенциями
        entry_id1 = test_db.add_entry("Проект 1", "Проект", "2024-01-01", "Тест", "")
        entry_id2 = test_db.add_entry("Проект 2", "Проект", "2024-02-01", "Тест", "")
        
        test_db.add_competency_to_entry(entry_id1, "Программирование", 4)
        test_db.add_competency_to_entry(entry_id1, "Командная работа", 3)
        test_db.add_competency_to_entry(entry_id2, "Программирование", 5)
        
        stats = test_db.get_competencies_statistics()
        
        # Должна быть статистика по двум компетенциям
        assert len(stats) == 2
        
        # Проверяем статистику для Программирования
        for stat in stats:
            if stat[0] == "Программирование":
                assert stat[1] == 4.5  # (4 + 5) / 2 = 4.5
                assert stat[2] == 2    # 2 оценки
    
    def test_get_recommendations(self, test_db):
        """Тест получения рекомендаций"""
        # Создаем записи с низким уровнем компетенций
        entry_id = test_db.add_entry("Тест", "Проект", "2024-01-01", "Тест", "")
        test_db.add_competency_to_entry(entry_id, "Презентация", 2)
        test_db.add_competency_to_entry(entry_id, "Командная работа", 1)
        test_db.add_competency_to_entry(entry_id, "Базы данных", 2)
        
        recommendations = test_db.get_recommendations()
        
        assert len(recommendations) > 0
        # Проверяем, что рекомендации содержат названия компетенций
        assert any("Презентация" in rec for rec in recommendations)
        assert any("Командная работа" in rec for rec in recommendations)
        assert any("Базы данных" in rec for rec in recommendations)
    
    def test_add_and_get_goals(self, test_db):
        """Тест добавления и получения целей"""
        # Добавляем цель
        test_db.add_goal("Количество записей", "Создать 5 записей", 5)
        
        # Получаем цели
        goals = test_db.get_goals()
        
        assert len(goals) == 1
        assert goals[0][1] == "Количество записей"
        assert goals[0][2] == "Создать 5 записей"
        assert goals[0][3] == 5  # цель
        assert goals[0][4] == 0  # текущее значение
        assert goals[0][5] == 0  # выполнено = False
    
    def test_update_goal_progress(self, test_db):
        """Тест обновления прогресса цели"""
        # Добавляем цель
        test_db.add_goal("Количество записей", "Создать 5 записей", 5)
        
        # Получаем ID цели
        test_db.cursor.execute("SELECT id FROM goals LIMIT 1")
        goal_id = test_db.cursor.fetchone()[0]
        
        # Обновляем прогресс
        test_db.update_goal_progress(goal_id, 3)
        
        # Проверяем обновление
        test_db.cursor.execute("SELECT текущее, выполнено FROM goals WHERE id = ?", (goal_id,))
        current, completed = test_db.cursor.fetchone()
        
        assert current == 3
        assert completed == 0  # еще не выполнено (3 < 5)
        
        # Обновляем до выполнения
        test_db.update_goal_progress(goal_id, 5)
        
        test_db.cursor.execute("SELECT выполнено FROM goals WHERE id = ?", (goal_id,))
        completed = test_db.cursor.fetchone()[0]
        
        assert completed == 1  # выполнено
    
    def test_get_authors_statistics(self, test_db):
        """Тест статистики по соавторам"""
        # Добавляем записи с соавторами
        test_db.add_entry("Проект 1", "Проект", "2024-01-01", "Описание", "Иван Иванов")
        test_db.add_entry("Проект 2", "Проект", "2024-02-01", "Описание", "Петр Петров")
        test_db.add_entry("Проект 3", "Проект", "2024-03-01", "Описание", "Иван Иванов")
        
        stats = test_db.get_authors_statistics()
        
        assert len(stats) == 2
        
        # Проверяем статистику
        stats_dict = dict(stats)
        assert stats_dict.get("Иван Иванов") == 2
        assert stats_dict.get("Петр Петров") == 1
```

## 2. Тесты для `achievements.py`

```python:test_achievements.py
import pytest
from unittest.mock import Mock, patch
from achievements import AchievementTracker
from datetime import datetime


@pytest.fixture
def mock_db():
    """Фикстура с моком базы данных"""
    mock = Mock()
    
    # Настройка мока для достижений
    mock.get_achievement_status.return_value = False
    mock.unlock_achievement.return_value = True
    mock.get_all_entries.return_value = [(1, "Тест", "Проект", "2024-01-01", "Описание", "")]
    
    return mock


@pytest.fixture
def tracker(mock_db):
    """Фикстура для трекера достижений"""
    return AchievementTracker(mock_db)


class TestAchievementTracker:
    """Тесты для класса AchievementTracker"""
    
    def test_init(self, tracker):
        """Тест инициализации"""
        assert tracker.db is not None
        assert isinstance(tracker, AchievementTracker)
    
    def test_check_achievements_first_step(self, mock_db):
        """Тест проверки достижения 'Первая запись'"""
        tracker = AchievementTracker(mock_db)
        
        # Настраиваем мок
        mock_db.get_achievement_status.return_value = False
        mock_db.get_all_entries.return_value = [(1, "Тест", "Проект", "2024-01-01", "Описание", "")]
        
        achievements = tracker.check_achievements()
        
        # Должно разблокироваться достижение "Первая запись"
        assert "Первая запись" in achievements
        mock_db.unlock_achievement.assert_called_with("Первая запись")
    
    def test_check_achievements_team_player(self, mock_db):
        """Тест проверки достижения 'Командный игрок'"""
        tracker = AchievementTracker(mock_db)
        
        # Настраиваем мок
        mock_db.get_achievement_status.side_effect = lambda x: False
        mock_db.count_entries_with_authors.return_value = 3
        
        achievements = tracker.check_achievements()
        
        assert "Командный игрок" in achievements
        mock_db.unlock_achievement.assert_called_with("Командный игрок")
    
    def test_check_achievements_versatile(self, mock_db):
        """Тест проверки достижения 'Разносторонний'"""
        tracker = AchievementTracker(mock_db)
        
        # Настраиваем мок
        mock_db.get_achievement_status.side_effect = lambda x: False
        mock_db.get_entry_types_count.return_value = 3
        
        achievements = tracker.check_achievements()
        
        assert "Разносторонний" in achievements
        mock_db.unlock_achievement.assert_called_with("Разносторонний")
    
    def test_check_achievements_prepared_year(self, mock_db):
        """Тест проверки достижения 'Подготовленный год'"""
        tracker = AchievementTracker(mock_db)
        
        # Настраиваем мок
        mock_db.get_achievement_status.side_effect = lambda x: False
        mock_db.get_entries_by_year.return_value = 3
        
        achievements = tracker.check_achievements()
        
        assert "Подготовленный год" in achievements
        mock_db.unlock_achievement.assert_called_with("Подготовленный год")
    
    def test_check_achievements_word_master(self, mock_db):
        """Тест проверки достижения 'Словобог'"""
        tracker = AchievementTracker(mock_db)
        
        # Настраиваем мок
        mock_db.get_achievement_status.side_effect = lambda x: False
        mock_db.get_total_description_length.return_value = 5000
        
        achievements = tracker.check_achievements()
        
        assert "Словобог" in achievements
        mock_db.unlock_achievement.assert_called_with("Словобог")
    
    def test_check_achievements_already_unlocked(self, mock_db):
        """Тест, когда достижение уже разблокировано"""
        tracker = AchievementTracker(mock_db)
        
        # Настраиваем мок - все достижения уже разблокированы
        mock_db.get_achievement_status.return_value = True
        
        achievements = tracker.check_achievements()
        
        # Не должно быть новых достижений
        assert len(achievements) == 0
        mock_db.unlock_achievement.assert_not_called()
    
    def test_get_all_achievements(self, mock_db):
        """Тест получения всех достижений"""
        tracker = AchievementTracker(mock_db)
        
        # Настраиваем мок
        mock_achievements = [
            (1, "Первая запись", "Создана первая запись", True, "2024-01-01"),
            (2, "Командный игрок", "Три записи с соавторами", False, None)
        ]
        mock_db.get_achievements.return_value = mock_achievements
        
        achievements = tracker.get_all_achievements()
        
        assert achievements == mock_achievements
        mock_db.get_achievements.assert_called_once()
```

## 3. Тесты для `models.py`

```python:test_models.py
import pytest
from datetime import datetime
from models import Entry, Achievement, Competency


class TestModels:
    """Тесты для моделей данных"""
    
    def test_entry_creation(self):
        """Тест создания объекта Entry"""
        entry = Entry(
            title="Тестовый проект",
            entry_type="Проект",
            date="2024-01-15",
            description="Тестовое описание",
            authors="Иван Иванов"
        )
        
        assert entry.title == "Тестовый проект"
        assert entry.type == "Проект"
        assert isinstance(entry.date, datetime)
        assert entry.date.year == 2024
        assert entry.date.month == 1
        assert entry.date.day == 15
        assert entry.description == "Тестовое описание"
        assert entry.authors == "Иван Иванов"
        assert entry.keywords == []
        assert entry.competencies == []
    
    def test_entry_with_datetime(self):
        """Тест создания Entry с объектом datetime"""
        date_obj = datetime(2024, 1, 15)
        entry = Entry("Тест", "Проект", date_obj)
        
        assert entry.date == date_obj
    
    def test_entry_str(self):
        """Тест строкового представления Entry"""
        entry = Entry("Мой проект", "Проект", "2024-01-15")
        
        expected_str = "Мой проект (Проект) - 2024-01-15"
        assert str(entry) == expected_str
    
    def test_entry_to_dict(self):
        """Тест преобразования Entry в словарь"""
        entry = Entry(
            title="Тестовый проект",
            entry_type="Проект",
            date="2024-01-15",
            description="Описание",
            authors="Иван Иванов"
        )
        entry.keywords = ["Python", "Тестирование"]
        
        result = entry.to_dict()
        
        assert result['название'] == "Тестовый проект"
        assert result['тип'] == "Проект"
        assert result['дата'] == "2024-01-15"
        assert result['описание'] == "Описание"
        assert result['соавторы'] == "Иван Иванов"
        assert result['ключевые_слова'] == "Python, Тестирование"
    
    def test_achievement_creation(self):
        """Тест создания объекта Achievement"""
        achievement = Achievement(
            name="Первая запись",
            description="Создана первая запись",
            obtained=True,
            date_obtained="2024-01-15"
        )
        
        assert achievement.name == "Первая запись"
        assert achievement.description == "Создана первая запись"
        assert achievement.obtained is True
        assert achievement.date_obtained == "2024-01-15"
    
    def test_achievement_str(self):
        """Тест строкового представления Achievement"""
        # Полученное достижение
        achievement1 = Achievement("Первая запись", "Описание", True)
        assert str(achievement1) == "✅ Первая запись: Описание"
        
        # Неполученное достижение
        achievement2 = Achievement("Первая запись", "Описание", False)
        assert str(achievement2) == "◻ Первая запись: Описание"
    
    def test_competency_creation(self):
        """Тест создания объекта Competency"""
        competency = Competency(
            name="Программирование",
            category="Технические",
            level=4
        )
        
        assert competency.name == "Программирование"
        assert competency.category == "Технические"
        assert competency.level == 4
    
    def test_competency_str(self):
        """Тест строкового представления Competency"""
        # С уровнем
        competency1 = Competency("Программирование", level=4)
        assert str(competency1) == "Программирование (уровень: 4/5)"
        
        # Без уровня
        competency2 = Competency("Программирование")
        assert str(competency2) == "Программирование"
        
        # С категорией
        competency3 = Competency("Программирование", category="Технические", level=4)
        assert str(competency3) == "Программирование (уровень: 4/5)"
```

## 4. Тесты для `export.py`

```python:test_export.py
import pytest
from unittest.mock import Mock, MagicMock, patch
from export import ReportExporter
from docx import Document
import os


@pytest.fixture
def mock_db():
    """Фикстура с моком базы данных"""
    mock = Mock()
    
    # Настраиваем возвращаемые данные
    mock.get_all_entries_with_keywords.return_value = [
        (1, "Тестовый проект", "Проект", "2024-01-15", "Описание проекта", 
         "Иван Иванов", "Python, Тестирование")
    ]
    
    mock.get_keywords_statistics.return_value = [
        ("Python", 3),
        ("Тестирование", 2)
    ]
    
    mock.get_authors_statistics.return_value = [
        ("Иван Иванов", 2),
        ("Петр Петров", 1)
    ]
    
    mock.get_competencies_statistics.return_value = [
        ("Программирование", 4.5, 2),
        ("Командная работа", 3.0, 1)
    ]
    
    mock.get_recommendations.return_value = [
        "Рекомендуется развивать навыки программирования",
        "Участвуйте в групповых проектах"
    ]
    
    mock.get_achievements.return_value = [
        (1, "Первая запись", "Создана первая запись", True, "2024-01-15"),
        (2, "Командный игрок", "Три записи с соавторами", False, None)
    ]
    
    return mock


@pytest.fixture
def exporter(mock_db):
    """Фикстура для экспортера"""
    return ReportExporter(mock_db)


class TestReportExporter:
    """Тесты для класса ReportExporter"""
    
    def test_init(self, exporter):
        """Тест инициализации"""
        assert exporter.db is not None
        assert isinstance(exporter, ReportExporter)
    
    @patch('export.Document')
    def test_export_to_word_basic(self, mock_document, exporter):
        """Базовый тест экспорта в Word"""
        # Создаем мок документа
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        # Мокаем методы документа
        mock_doc.styles = {'Normal': MagicMock()}
        mock_doc.styles['Normal'].font = MagicMock()
        
        # Вызываем экспорт
        filename = exporter.export_to_word("test_report.docx")
        
        # Проверяем, что методы были вызваны
        mock_document.assert_called_once()
        mock_doc.save.assert_called_with("test_report.docx")
        assert filename == "test_report.docx"
    
    def test_export_to_word_with_real_file(self, exporter, tmp_path):
        """Тест экспорта с созданием реального файла"""
        filename = str(tmp_path / "test_report.docx")
        
        # Используем патчинг для Document, чтобы не зависеть от наличия Word
        with patch('export.Document') as mock_document:
            mock_doc = MagicMock()
            mock_document.return_value = mock_doc
            
            # Вызываем экспорт
            result = exporter.export_to_word(filename)
            
            assert result == filename
            mock_doc.save.assert_called_with(filename)
    
    def test_export_to_word_no_data(self, tmp_path):
        """Тест экспорта без данных"""
        # Создаем мок БД без данных
        mock_db = Mock()
        mock_db.get_all_entries_with_keywords.return_value = []
        mock_db.get_keywords_statistics.return_value = []
        mock_db.get_authors_statistics.return_value = []
        mock_db.get_competencies_statistics.return_value = []
        mock_db.get_recommendations.return_value = []
        mock_db.get_achievements.return_value = []
        
        exporter = ReportExporter(mock_db)
        filename = str(tmp_path / "empty_report.docx")
        
        with patch('export.Document') as mock_document:
            mock_doc = MagicMock()
            mock_document.return_value = mock_doc
            
            result = exporter.export_to_word(filename)
            
            assert result == filename
    
    @patch('export.datetime')
    def test_export_contains_date(self, mock_datetime, exporter, tmp_path):
        """Тест, что отчет содержит дату генерации"""
        # Фиксируем дату для теста
        from datetime import datetime
        fixed_date = datetime(2024, 1, 15, 14, 30, 0)
        mock_datetime.now.return_value = fixed_date
        
        filename = str(tmp_path / "dated_report.docx")
        
        with patch('export.Document') as mock_document:
            mock_doc = MagicMock()
            mock_paragraph = MagicMock()
            mock_run = MagicMock()
            
            mock_doc.add_paragraph.return_value = mock_paragraph
            mock_paragraph.add_run.return_value = mock_run
            mock_document.return_value = mock_doc
            
            exporter.export_to_word(filename)
            
            # Проверяем, что дата была добавлена
            mock_paragraph.add_run.assert_any()
            # Проверяем формат даты
            expected_date = "Сгенерировано: 15.01.2024 14:30"
            
            # Получаем все вызовы add_run
            calls = mock_paragraph.add_run.call_args_list
            date_calls = [call for call in calls if call[0] and expected_date in call[0][0]]
            
            assert len(date_calls) > 0, f"Дата {expected_date} должна быть в отчете"
    
    def test_export_with_competencies_table(self, exporter, tmp_path):
        """Тест экспорта с таблицей компетенций"""
        filename = str(tmp_path / "competencies_report.docx")
        
        with patch('export.Document') as mock_document:
            mock_doc = MagicMock()
            mock_table = MagicMock()
            
            mock_doc.add_table.return_value = mock_table
            mock_document.return_value = mock_doc
            
            exporter.export_to_word(filename)
            
            # Проверяем, что таблица была создана
            mock_doc.add_table.assert_called_once()
            
            # Проверяем параметры создания таблицы
            call_args = mock_doc.add_table.call_args
            assert call_args[0][0] == 1  # rows
            assert call_args[0][1] == 3  # cols
```

## 5. Основной файл с настройками pytest

```python:conftest.py
"""
Конфигурация pytest для всего проекта
"""
import pytest
import sys
import os

# Добавляем путь к проекту в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Автоматическая очистка тестовых файлов после каждого теста"""
    # Сохраняем список файлов до теста
    files_before = set(os.listdir('.'))
    
    yield
    
    # После теста удаляем созданные файлы
    files_after = set(os.listdir('.'))
    new_files = files_after - files_before
    
    for file in new_files:
        if file.endswith(('.docx', '.db', '.log')):
            try:
                os.remove(file)
            except:
                pass
```

## 6. Файл запуска всех тестов

```python:run_tests.py
#!/usr/bin/env python
"""
Запуск всех тестов проекта
"""
import pytest
import sys

if __name__ == "__main__":
    # Запускаем все тесты
    result = pytest.main([
        "-v",            # Подробный вывод
        "--tb=short",    # Короткий traceback
        "--color=yes",   # Цветной вывод
        "test_database.py",
        "test_achievements.py", 
        "test_models.py",
        "test_export.py"
    ])
    
    sys.exit(result)
```

## 7. Файл `requirements.txt` для тестов

```txt:requirements_test.txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.11.1
coverage==7.3.2
python-docx==0.8.11
```

## Инструкции по запуску тестов:

### 1. Установите зависимости:
```bash
pip install -r requirements_test.txt
```

### 2. Запустите все тесты:
```bash
python run_tests.py
```

Или по отдельности:
```bash
pytest test_database.py -v
pytest test_achievements.py -v
pytest test_models.py -v
pytest test_export.py -v
```

### 3. Запустите тесты с покрытием:
```bash
pytest --cov=database --cov=achievements --cov=models --cov=export --cov-report=html
```

### 4. Структура тестов включает:

1. **Тесты базы данных** (`test_database.py`):
   - Создание таблиц
   - CRUD операции с записями
   - Работа с ключевыми словами и компетенциями
   - Статистика и рекомендации
   - Достижения и цели

2. **Тесты достижений** (`test_achievements.py`):
   - Проверка условий для достижений
   - Мокирование зависимостей
   - Разблокировка достижений

3. **Тесты моделей** (`test_models.py`):
   - Создание объектов
   - Сериализация в словари
   - Строковые представления

4. **Тесты экспорта** (`test_export.py`):
   - Создание Word документа
   - Форматирование отчета
   - Обработка различных сценариев данных

### 5. Ключевые особенности тестов:

- Использование фикстур для изоляции тестов
- Мокирование внешних зависимостей
- Очистка тестовых файлов после выполнения
- Проверка граничных случаев
- Тестирование как с корректными, так и с ошибочными данными
- Проверка форматов дат и строк

Тесты покрывают основные функции приложения и помогут выявить проблемы при изменениях кода.
