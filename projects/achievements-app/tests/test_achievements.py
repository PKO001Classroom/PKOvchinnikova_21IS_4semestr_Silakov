import pytest
import sqlite3
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch, mock_open
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_db():
    """Создание временной базы данных для тестов"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "достижения.db")

    def mock_connect(database, *args, **kwargs):
        if database == "достижения.db":
            return sqlite3.connect(db_path, *args, **kwargs)
        return sqlite3.connect(database, *args, **kwargs)

    with patch('src.database.sqlite3.connect', side_effect=mock_connect):
        yield db_path

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_achievement():
    """Возвращает пример достижения для тестов"""
    return {
        "название": "Победа в олимпиаде по математике",
        "дата": "2024-03-15",
        "тип": "Олимпиада",
        "уровень": "Городской",
        "описание": "Занял первое место на городской олимпиаде"
    }


class TestDatabaseFunctions:
    def test_init_db_creates_table(self, temp_db):
        """Тест создания таблицы при инициализации БД"""
        from src.database import init_db

        with patch('src.database.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            init_db()

            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called()
            mock_conn.close.assert_called()

    def test_save_achievement_success(self, temp_db, sample_achievement):
        """Тест успешного сохранения в БД"""
        from src.database import save_achievement

        with patch('src.database.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            result = save_achievement(
                sample_achievement["название"],
                sample_achievement["дата"],
                sample_achievement["тип"],
                sample_achievement["уровень"],
                sample_achievement["описание"]
            )

            assert result is True
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
            mock_conn.close.assert_called_once()

    def test_save_achievement_failure(self, sample_achievement):
        """Тест неудачного сохранения в БД"""
        from src.database import save_achievement

        with patch('src.database.sqlite3.connect', side_effect=Exception("DB error")):
            result = save_achievement(
                sample_achievement["название"],
                sample_achievement["дата"],
                sample_achievement["тип"],
                sample_achievement["уровень"],
                sample_achievement["описание"]
            )

            assert result is False

    def test_load_all_achievements_success(self):
        """Тест успешной загрузки записей из БД"""
        from src.database import load_all_achievements

        mock_data = [
            (1, "Название1", "2024-01-01", "Олимпиада", "Школьный", "Описание1"),
            (2, "Название2", "2024-02-01", "Проект", "Городской", "Описание2")
        ]

        with patch('src.database.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = mock_data

            result = load_all_achievements()

            assert result == mock_data
            mock_cursor.execute.assert_called_once()
            mock_conn.close.assert_called_once()

    def test_load_all_achievements_empty(self):
        """Тест загрузки пустого списка записей"""
        from src.database import load_all_achievements

        with patch('src.database.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []

            result = load_all_achievements()

            assert result == []
            mock_conn.close.assert_called_once()

    def test_delete_achievement_success(self):
        """Тест успешного удаления записи"""
        from src.database import delete_achievement

        with patch('src.database.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            result = delete_achievement(1)

            assert result is True
            mock_cursor.execute.assert_called_once_with(
                "DELETE FROM достижения WHERE id = ?", (1,)
            )
            mock_conn.commit.assert_called_once()
            mock_conn.close.assert_called_once()


class TestFileFunctions:
    def test_load_types_from_file(self):
        """Тест загрузки типов из файла"""
        from src.utils import load_types_from_json

        types_data = ["Олимпиада", "Сертификат", "Проект", "Экзамен", "Конференция"]

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('json.load', return_value=types_data):
                    result = load_types_from_json()

                    assert isinstance(result, list)
                    assert len(result) == 5
                    assert "Олимпиада" in result

    def test_load_types_file_not_exists(self):
        """Тест загрузки типов при отсутствии файла"""
        from src.utils import load_types_from_json

        with patch('os.path.exists', return_value=False):
            result = load_types_from_json()

            assert isinstance(result, list)
            assert len(result) > 0

    def test_export_to_word_success(self):
        """Тест успешного экспорта в Word"""
        from src.utils import export_to_word

        mock_records = [
            (1, "Тестовое достижение", "2024-01-01", "Олимпиада", "Школьный", "Тестовое описание")
        ]

        with patch('src.utils.Document') as mock_doc_class:
            mock_doc = MagicMock()
            mock_doc_class.return_value = mock_doc

            result = export_to_word(mock_records)

            assert result is True
            mock_doc_class.assert_called_once()
            mock_doc.add_heading.assert_called_once()
            mock_doc.save.assert_called_once_with("достижения.docx")

    def test_export_to_word_empty(self):
        """Тест экспорта пустого списка"""
        from src.utils import export_to_word

        with patch('src.utils.Document') as mock_doc_class:
            mock_doc = MagicMock()
            mock_doc_class.return_value = mock_doc

            result = export_to_word([])

            assert result is True
            mock_doc.add_paragraph.assert_called()
            mock_doc.save.assert_called_once()


class TestModels:
    def test_achievement_from_db_row(self):
        """Тест создания модели из строки БД"""
        from src.models import Achievement

        row = (1, "Название", "2024-01-01", "Тип", "Уровень", "Описание")
        achievement = Achievement.from_db_row(row)

        assert achievement.id == 1
        assert achievement.title == "Название"
        assert achievement.date == "2024-01-01"
        assert achievement.type == "Тип"
        assert achievement.level == "Уровень"
        assert achievement.description == "Описание"

    def test_achievement_display_string_short(self):
        """Тест форматирования строки для короткого названия"""
        from src.models import Achievement

        achievement = Achievement(
            id=1,
            title="Короткое название",
            date="2024-01-01",
            type="Тип",
            level="Уровень",
            description=""
        )

        result = achievement.display_string()
        assert "2024-01-01 | Короткое название | Тип | Уровень" in result

    def test_achievement_display_string_long(self):
        """Тест форматирования строки для длинного названия"""
        from src.models import Achievement

        long_title = "Очень длинное название достижения, которое должно быть обрезано"
        achievement = Achievement(
            id=1,
            title=long_title,
            date="2024-01-01",
            type="Тип",
            level="Уровень",
            description=""
        )

        result = achievement.display_string()
        assert len(result.split('|')[1].strip()) <= 53


class TestGUI:
    @pytest.fixture
    def mock_tkinter(self):
        """Мок для tkinter компонентов"""
        with patch('tkinter.Tk') as mock_tk:
            with patch('tkinter.ttk.Notebook'):
                with patch('tkinter.Frame'):
                    with patch('tkinter.Label'):
                        with patch('tkinter.Entry'):
                            with patch('tkinter.Text'):
                                with patch('tkinter.Button'):
                                    with patch('tkinter.Listbox'):
                                        with patch('tkinter.Scrollbar'):
                                            with patch('tkinter.ttk.Combobox'):
                                                yield mock_tk

    def test_app_initialization(self, mock_tkinter):
        """Тест инициализации приложения"""
        from src.gui import AchievementsApp

        with patch('src.database.init_db') as mock_init_db:
            with patch('src.utils.load_types_from_json', return_value=["Тип1", "Тип2"]):
                with patch('src.database.load_all_achievements', return_value=[]):
                    root = MagicMock()
                    app = AchievementsApp(root)

                    mock_init_db.assert_called_once()
                    assert hasattr(app, 'available_types')
                    assert app.available_types == ["Тип1", "Тип2"]

    def test_refresh_list_with_data(self, mock_tkinter):
        """Тест обновления списка с данными"""
        from src.gui import AchievementsApp

        mock_records = [
            (1, "Достижение 1", "2024-01-01", "Тип1", "Уровень1", "Описание1"),
            (2, "Достижение 2", "2024-02-01", "Тип2", "Уровень2", "Описание2")
        ]

        root = MagicMock()
        app = AchievementsApp(root)
        app.listbox = MagicMock()

        with patch('src.database.load_all_achievements', return_value=mock_records):
            app.refresh_list()

            app.listbox.delete.assert_called_once_with(0, tk.END)
            assert app.listbox.insert.call_count == 2
            assert app.current_records == mock_records


class TestIntegration:
    def test_full_flow(self, sample_achievement):
        """Интеграционный тест с реальной БД"""
        import os
        import tempfile
        
        # Создаем временную БД
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db = tmp.name
        
        try:
            from src.database import init_db, save_achievement, load_all_achievements
            
            # Инициализация временной БД
            init_db(test_db)
            
            # Сохранение достижения
            success = save_achievement(
                sample_achievement["название"],
                sample_achievement["дата"],
                sample_achievement["тип"],
                sample_achievement["уровень"],
                sample_achievement["описание"],
                test_db
            )
            
            assert success is True, "Достижение не сохранилось"
            
            # Загрузка всех достижений
            records = load_all_achievements(test_db)
            assert len(records) >= 1, "Нет записей в БД"
            
            # Проверка, что наше достижение есть в списке
            found = False
            for record in records:
                if record[1] == sample_achievement["название"]:
                    found = True
                    break
            assert found, "Достижение не найдено в БД"
            
        finally:
            # Очистка
            if os.path.exists(test_db):
                os.unlink(test_db)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])