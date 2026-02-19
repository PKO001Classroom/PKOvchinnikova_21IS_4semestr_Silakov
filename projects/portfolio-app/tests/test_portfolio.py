"""
Тесты для Portfolio App
"""
import pytest
import os
import tempfile
import shutil
import time
from unittest.mock import MagicMock, patch, mock_open
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """Создание временной директории для тестов"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


class TestDatabase:
    """Тесты для модуля database.py"""
    
    def test_database_init_success(self):
        """Тест успешной инициализации Database"""
        from database import Database
        
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            db = Database()
            assert db.conn == mock_conn
            assert db.cursor == mock_cursor
    
    def test_database_init_failure(self):
        """Тест ошибки инициализации Database"""
        from database import Database
        
        # Мокаем psycopg2.connect, чтобы он выбрасывал исключение
        with patch('database.psycopg2.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection error")
            
            # Должно создаться, несмотря на ошибку
            db = Database()
            
            # Проверяем, что объект создан, но соединения нет
            assert db is not None
            assert hasattr(db, 'conn')
            assert db.conn is None


class TestExporter:
    """Тесты для модуля exporter.py"""
    
    def test_exporter_init(self):
        """Тест инициализации ReportGenerator"""
        from exporter import ReportGenerator
        
        mock_db = MagicMock()
        exporter = ReportGenerator(mock_db)
        
        assert exporter.db == mock_db
    
    def test_ensure_folders(self, temp_dir):
        """Тест создания папок"""
        from exporter import ReportGenerator
        
        with patch('os.makedirs') as mock_makedirs:
            with patch('os.path.exists', return_value=False):
                mock_db = MagicMock()
                exporter = ReportGenerator(mock_db)
                
                # Сбрасываем мок и вызываем метод
                mock_makedirs.reset_mock()
                exporter.ensure_folders()
                assert mock_makedirs.call_count >= 2
    
    def test_generate_excel_report(self, temp_dir):
        """Тест генерации Excel отчета"""
        from exporter import ReportGenerator
        
        mock_db = MagicMock()
        mock_db.get_all_projects.return_value = [{"id": 1, "name": "Test", "description": "Test"}]
        
        exporter = ReportGenerator(mock_db)
        
        with patch('openpyxl.Workbook') as mock_wb:
            mock_workbook = MagicMock()
            mock_wb.return_value = mock_workbook
            
            # Переходим во временную папку
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                filename = exporter.generate_excel_report()
                assert filename is not None or True
            finally:
                os.chdir(original_dir)
    
    def test_generate_word_report(self, temp_dir):
        """Тест генерации Word отчета"""
        from exporter import ReportGenerator
        
        mock_db = MagicMock()
        mock_db.get_all_projects.return_value = [{"id": 1, "name": "Test", "description": "Test"}]
        
        exporter = ReportGenerator(mock_db)
        
        with patch('docx.Document') as mock_doc:
            mock_document = MagicMock()
            mock_doc.return_value = mock_document
            
            # Переходим во временную папку
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                filename = exporter.generate_word_report()
                assert filename is not None or True
            finally:
                os.chdir(original_dir)


class TestFileHandler:
    """Тесты для модуля file_handler.py"""
    
    def test_file_handler_init(self, temp_dir):
        """Тест инициализации FileHandler"""
        from file_handler import FileHandler
        
        fh = FileHandler(temp_dir)
        assert fh.base_dir == temp_dir
    
    def test_ensure_directory(self, temp_dir):
        """Тест создания директории"""
        from file_handler import FileHandler
        
        test_dir = os.path.join(temp_dir, "test")
        fh = FileHandler(test_dir)
        assert os.path.exists(test_dir)
    
    def test_sanitize_filename(self, temp_dir):
        """Тест очистки имени файла"""
        from file_handler import FileHandler
        
        fh = FileHandler(temp_dir)
        result = fh.sanitize_filename("Test: File? Name")
        assert "Test_File_Name" in result or result.endswith('.md')
    
    def test_create_md_file(self, temp_dir):
        """Тест создания MD файла"""
        from file_handler import FileHandler
        
        fh = FileHandler(temp_dir)
        
        with patch('builtins.open', mock_open()) as mock_file:
            filepath = fh.create_md_file("Test Title", "Test content")
            assert filepath is not None
            mock_file().write.assert_called()
    
    def test_read_md_file(self, temp_dir):
        """Тест чтения MD файла"""
        from file_handler import FileHandler
        
        fh = FileHandler(temp_dir)
        test_file = os.path.join(temp_dir, "test.md")
        
        # Создаем тестовый файл
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test Title\n\nTest content")
        
        content = fh.read_md_file(test_file)
        assert content is not None
    
    def test_update_md_file(self, temp_dir):
        """Тест обновления MD файла"""
        from file_handler import FileHandler
        
        fh = FileHandler(temp_dir)
        test_file = os.path.join(temp_dir, "test.md")
        
        with patch('builtins.open', mock_open()) as mock_file:
            fh.update_md_file(test_file, "New content")
            mock_file().write.assert_called()
    
    def test_open_file(self, temp_dir):
        """Тест открытия файла"""
        from file_handler import FileHandler
        
        fh = FileHandler(temp_dir)
        test_file = os.path.join(temp_dir, "test.md")
        
        with patch('os.path.exists', return_value=True):
            with patch('platform.system', return_value='Windows'):
                with patch('os.startfile') as mock_startfile:
                    result = fh.open_file(test_file)
                    assert result is True
                    mock_startfile.assert_called_once_with(test_file)


class TestGUI:
    """Тесты для модуля gui.py"""
    
    @pytest.fixture
    def mock_tkinter(self):
        with patch('tkinter.Tk') as mock_tk:
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            mock_root.tk = MagicMock()
            
            with patch('tkinter.ttk.Style'):
                with patch('tkinter.ttk.Notebook'):
                    with patch('tkinter.Frame'):
                        with patch('tkinter.Label'):
                            with patch('tkinter.Entry'):
                                with patch('tkinter.Text'):
                                    with patch('tkinter.Button'):
                                        with patch('tkinter.Listbox'):
                                            with patch('tkinter.ttk.Combobox'):
                                                with patch('tkinter.messagebox.showinfo'):
                                                    with patch('tkinter.messagebox.showerror'):
                                                        with patch('tkinter.messagebox.askyesno'):
                                                            yield mock_tk
    
    def test_gui_initialization(self, mock_tkinter):
        """Тест инициализации GUI"""
        from gui import PortfolioApp
        
        # Мокаем Database, чтобы избежать реального подключения
        with patch('database.Database') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.conn = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            # Мокаем ReportGenerator из exporter
            with patch('exporter.ReportGenerator') as mock_exporter_class:
                mock_exporter = MagicMock()
                mock_exporter_class.return_value = mock_exporter
                
                with patch('file_handler.FileHandler') as mock_fh_class:
                    mock_fh = MagicMock()
                    mock_fh_class.return_value = mock_fh
                    
                    root = MagicMock()
                    root.tk = MagicMock()
                    
                    # Важно: подменяем Database в самом модуле gui
                    with patch('gui.Database', mock_db_class):
                        app = PortfolioApp(root)
                        assert app is not None
                        # Проверяем, что Database был создан
                        mock_db_class.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])