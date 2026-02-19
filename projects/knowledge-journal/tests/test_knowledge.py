"""
Тесты для Knowledge Journal
"""
import pytest
import os
import tempfile
import shutil
import sqlite3
from unittest.mock import MagicMock, patch, mock_open
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_db():
    """Создание временной БД для тестов"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Создаем таблицы
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
    yield path
    
    if os.path.exists(path):
        try:
            os.unlink(path)
        except:
            pass


@pytest.fixture
def temp_dir():
    """Временная директория для файлов"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


class TestDatabase:
    """Тесты для работы с БД"""
    
    def test_add_note(self, temp_db):
        """Тест добавления заметки"""
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute(
            "INSERT INTO notes (title, content, category, created_at) VALUES (?, ?, ?, ?)",
            ("Test Note", "Test Content", "Work", "2024-01-01")
        )
        conn.commit()
        
        c.execute("SELECT * FROM notes")
        notes = c.fetchall()
        conn.close()
        
        assert len(notes) == 1
        assert notes[0][1] == "Test Note"
    
    def test_get_notes(self, temp_db):
        """Тест получения заметок"""
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        
        # Добавляем тестовые данные
        test_data = [
            ("Note 1", "Content 1", "Work", "2024-01-01"),
            ("Note 2", "Content 2", "Study", "2024-01-02")
        ]
        for note in test_data:
            c.execute(
                "INSERT INTO notes (title, content, category, created_at) VALUES (?, ?, ?, ?)",
                note
            )
        conn.commit()
        
        c.execute("SELECT * FROM notes ORDER BY created_at DESC")
        notes = c.fetchall()
        conn.close()
        
        assert len(notes) == 2
        assert notes[0][1] == "Note 2"  # Проверяем сортировку


class TestFileManager:
    """Тесты для работы с файлами"""
    
    def test_file_manager_init(self, temp_dir):
        """Тест инициализации FileManager"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_dir)
        assert fm.notes_dir == Path(temp_dir)
    
    def test_create_md_file(self, temp_dir):
        """Тест создания MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_dir)
        
        with patch('builtins.open', mock_open()) as mock_file:
            filename = fm.create_md_file("Test Title", "# Test Content")
            assert filename is not None
            mock_file().write.assert_called()
    
    def test_read_md_file(self, temp_dir):
        """Тест чтения MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_dir)
        filepath = os.path.join(temp_dir, "test.md")
        
        # Создаем тестовый файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Test\nContent")
        
        content = fm.read_md_file(filepath)
        assert content is not None
        assert "# Test" in content
    
    def test_write_md_file(self, temp_dir):
        """Тест записи MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_dir)
        filepath = os.path.join(temp_dir, "test.md")
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = fm.write_md_file(filepath, "New content")
            assert result is True
            mock_file().write.assert_called_with("New content")
    
    def test_delete_md_file(self, temp_dir):
        """Тест удаления MD файла"""
        from src.file_manager import FileManager
        
        fm = FileManager(temp_dir)
        filepath = os.path.join(temp_dir, "test.md")
        
        # Создаем файл
        with open(filepath, 'w') as f:
            f.write("test")
        
        assert os.path.exists(filepath)
        result = fm.delete_md_file(filepath)
        assert result is True
        assert not os.path.exists(filepath)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])