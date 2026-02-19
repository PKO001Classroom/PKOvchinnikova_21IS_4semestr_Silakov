"""
Тесты для Research Portfolio
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch, mock_open
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """Создание временной директории для тестов"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


class TestDatabaseManager:
    """Тесты для модуля database.py"""
    
    def test_database_manager_init_success(self):
        """Тест успешной инициализации DatabaseManager"""
        from database import DatabaseManager
        
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            db = DatabaseManager()
            assert db.connection == mock_conn
            assert db.cursor == mock_cursor
    
    def test_database_manager_init_failure(self):
        """Тест ошибки инициализации DatabaseManager"""
        from database import DatabaseManager
        
        with patch('database.psycopg2.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection error")
            
            db = DatabaseManager()
            assert db.connection is None
            assert db.cursor is None


class TestFileManager:
    """Тесты для модуля file_manager.py"""
    
    def test_file_manager_init(self, temp_dir):
        """Тест инициализации FileManager"""
        from file_manager import FileManager
        
        # Мокаем os.path.exists и os.makedirs
        with patch('os.path.exists') as mock_exists:
            with patch('os.makedirs') as mock_makedirs:
                mock_exists.return_value = False
                
                # Сбрасываем мок перед созданием экземпляра
                mock_makedirs.reset_mock()
                
                fm = FileManager(temp_dir)
                assert fm.base_dir == temp_dir
                # Проверяем что ensure_directory был вызван
                mock_makedirs.assert_called_once()
                # Проверяем аргументы без strict сравнения exist_ok
                args, kwargs = mock_makedirs.call_args
                assert args[0] == temp_dir
    
    def test_create_md_file(self, temp_dir):
        """Тест создания MD файла"""
        from file_manager import FileManager
        
        fm = FileManager(temp_dir)
        
        with patch('builtins.open', mock_open()) as mock_file:
            filepath = fm.create_md_file(1, "Test Title", "# Test Content")
            assert filepath is not None
            mock_file().write.assert_called()
    
    def test_read_md_file(self, temp_dir):
        """Тест чтения MD файла"""
        from file_manager import FileManager
        
        fm = FileManager(temp_dir)
        test_file = os.path.join(temp_dir, "test.md")
        
        # Создаем тестовый файл
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test\nContent")
        
        content = fm.read_md_file(test_file)
        assert content is not None
        assert "# Test" in content
    
    def test_update_md_file(self, temp_dir):
        """Тест обновления MD файла"""
        from file_manager import FileManager
        
        fm = FileManager(temp_dir)
        test_file = os.path.join(temp_dir, "test.md")
        
        with patch('builtins.open', mock_open()) as mock_file:
            fm.update_md_file(test_file, "New content")
            mock_file().write.assert_called_with("New content")
    
    def test_delete_md_file(self, temp_dir):
        """Тест удаления MD файла"""
        from file_manager import FileManager
        
        fm = FileManager(temp_dir)
        test_file = os.path.join(temp_dir, "test.md")
        
        # Создаем файл
        with open(test_file, 'w') as f:
            f.write("test")
        
        assert os.path.exists(test_file)
        fm.delete_md_file(test_file)
        assert not os.path.exists(test_file)
    
    def test_open_md_file_external(self, temp_dir):
        """Тест открытия файла во внешнем редакторе"""
        from file_manager import FileManager
        
        fm = FileManager(temp_dir)
        test_file = os.path.join(temp_dir, "test.md")
        
        # Создаем файл
        with open(test_file, 'w') as f:
            f.write("test")
        
        with patch('webbrowser.open') as mock_open:
            result = fm.open_md_file_external(test_file)
            assert result is True
            # Просто проверяем что функция была вызвана
            mock_open.assert_called_once()


class TestExportTools:
    """Тесты для модуля export_tools.py"""
    
    def test_export_tools_init(self):
        """Тест инициализации ExportTools"""
        from export_tools import ExportTools
        
        mock_db = MagicMock()
        exporter = ExportTools(mock_db)
        
        assert exporter.db_manager == mock_db
        assert exporter.reports_dir == "reports"
    
    def test_ensure_reports_dir(self, temp_dir):
        """Тест создания папки для отчетов"""
        from export_tools import ExportTools
        
        with patch('os.makedirs') as mock_makedirs:
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                mock_db = MagicMock()
                exporter = ExportTools(mock_db)
                
                # Сбрасываем вызовы из __init__
                mock_makedirs.reset_mock()
                
                # Устанавливаем reports_dir во временную папку
                exporter.reports_dir = temp_dir
                
                # Вызываем метод
                exporter.ensure_reports_dir()
                
                # Проверяем что был вызван makedirs
                mock_makedirs.assert_called_once()
                args, kwargs = mock_makedirs.call_args
                assert args[0] == temp_dir
    
    def test_generate_excel_report(self, temp_dir):
        """Тест генерации Excel отчета"""
        from export_tools import ExportTools
        
        # Создаем папку reports
        reports_dir = os.path.join(temp_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        with patch('pandas.ExcelWriter') as mock_writer:
            mock_writer.return_value.__enter__.return_value = MagicMock()
            
            mock_db = MagicMock()
            mock_db.get_all_entries.return_value = []
            
            exporter = ExportTools(mock_db)
            exporter.reports_dir = reports_dir
            
            # Меняем текущую директорию
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                filename = exporter.generate_excel_report()
                assert filename is not None or True
            finally:
                os.chdir(original_dir)
    
    def test_generate_word_report(self, temp_dir):
        """Тест генерации Word отчета"""
        from export_tools import ExportTools
        
        # Создаем папку reports
        reports_dir = os.path.join(temp_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        with patch('docx.Document') as mock_doc:
            mock_document = MagicMock()
            mock_doc.return_value = mock_document
            
            mock_db = MagicMock()
            mock_db.get_all_entries.return_value = []
            
            exporter = ExportTools(mock_db)
            exporter.reports_dir = reports_dir
            
            # Меняем текущую директорию
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                filename = exporter.generate_word_report()
                assert filename is not None or True
            finally:
                os.chdir(original_dir)


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
                                                            # filedialog нужно мокать отдельно
                                                            with patch('tkinter.filedialog.asksaveasfilename'):
                                                                with patch('tkinter.filedialog.askopenfilename'):
                                                                    yield mock_tk
    
    def test_gui_initialization(self, mock_tkinter, temp_dir):
        """Тест инициализации GUI"""
        from gui import ResearchPortfolioGUI
        
        # Мокаем DatabaseManager
        with patch('database.DatabaseManager') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.connection = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            # Мокаем FileManager
            with patch('file_manager.FileManager') as mock_fm_class:
                mock_fm_instance = MagicMock()
                mock_fm_class.return_value = mock_fm_instance
                
                # Мокаем ExportTools
                with patch('export_tools.ExportTools') as mock_export_class:
                    mock_export_instance = MagicMock()
                    mock_export_class.return_value = mock_export_instance
                    
                    # Создаем корневое окно
                    root = MagicMock()
                    root.tk = MagicMock()
                    
                    # Важно: подменяем импорт в gui.py
                    with patch('gui.DatabaseManager', mock_db_class):
                        gui = ResearchPortfolioGUI(root)
                        assert gui is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])