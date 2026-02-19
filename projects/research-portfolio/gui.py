"""
GUI для Research Portfolio
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from datetime import datetime

from database import DatabaseManager
from file_manager import FileManager
from export_tools import ExportTools


class ResearchPortfolioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Research Portfolio")
        self.root.geometry("1200x700")
        
        # Инициализация компонентов
        self.db = DatabaseManager()
        self.fm = FileManager()
        self.exporter = ExportTools(self.db)
        
        # Загрузка данных
        self.entries = []
        self.load_entries()
        
        # Создание интерфейса
        self.create_widgets()
    
    def load_entries(self):
        """Загрузка записей из БД"""
        if self.db.connection:
            self.entries = self.db.get_all_entries() or []
        print(f"Загружено записей: {len(self.entries)}")
    
    def create_widgets(self):
        """Создание виджетов"""
        # Заголовок
        title = ttk.Label(self.root, text="Research Portfolio", 
                          font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка записей
        self.create_entries_tab(notebook)
        
        # Вкладка файлов
        self.create_files_tab(notebook)
        
        # Вкладка отчетов
        self.create_reports_tab(notebook)
    
    def create_entries_tab(self, notebook):
        """Вкладка с записями"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Записи")
        
        # Панель инструментов
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="➕ Добавить", 
                  command=self.add_entry).pack(side='left', padx=2)
        ttk.Button(toolbar, text="✏️ Редактировать", 
                  command=self.edit_entry).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🗑️ Удалить", 
                  command=self.delete_entry).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🔄 Обновить", 
                  command=self.refresh_entries).pack(side='left', padx=2)
        
        # Таблица записей
        columns = ('id', 'title', 'entry_type', 'year', 'created_at')
        self.tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Название')
        self.tree.heading('entry_type', text='Тип')
        self.tree.heading('year', text='Год')
        self.tree.heading('created_at', text='Дата создания')
        
        self.tree.column('id', width=50)
        self.tree.column('title', width=300)
        self.tree.column('entry_type', width=150)
        self.tree.column('year', width=80)
        self.tree.column('created_at', width=150)
        
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        self.refresh_entries()
    
    def create_files_tab(self, notebook):
        """Вкладка с файлами"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Файлы")
        
        # Панель инструментов
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="📁 Создать файл", 
                  command=self.create_file).pack(side='left', padx=2)
        ttk.Button(toolbar, text="📂 Открыть файл", 
                  command=self.open_file).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🔄 Обновить", 
                  command=self.refresh_files).pack(side='left', padx=2)
        
        # Список файлов
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.files_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=('Consolas', 10), height=15)
        self.files_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=self.files_listbox.yview)
        
        self.refresh_files()
    
    def create_reports_tab(self, notebook):
        """Вкладка с отчетами"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Отчеты")
        
        # Заголовок
        ttk.Label(tab, text="Генерация отчетов", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        # Кнопки
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="📊 Excel отчет", 
                  command=self.generate_excel,
                  width=25).pack(pady=5)
        
        ttk.Button(btn_frame, text="📝 Word отчет", 
                  command=self.generate_word,
                  width=25).pack(pady=5)
        
        ttk.Button(btn_frame, text="📄 PDF отчет", 
                  command=self.generate_pdf,
                  width=25).pack(pady=5)
    
    def refresh_entries(self):
        """Обновление списка записей"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.load_entries()
        for entry in self.entries:
            self.tree.insert('', 'end', values=(
                entry.get('id'),
                entry.get('title'),
                entry.get('entry_type'),
                entry.get('year'),
                str(entry.get('created_at', ''))[:10]
            ))
    
    def refresh_files(self):
        """Обновление списка файлов"""
        self.files_listbox.delete(0, tk.END)
        
        if os.path.exists('reports'):
            files = os.listdir('reports')
            for f in sorted(files, reverse=True):
                self.files_listbox.insert(tk.END, f)
    
    def add_entry(self):
        """Добавление новой записи"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить запись")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Название:").pack(pady=5)
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Тип:").pack(pady=5)
        type_combo = ttk.Combobox(dialog, 
                                  values=['article', 'book', 'thesis', 'conference', 'other'],
                                  state='readonly')
        type_combo.set('article')
        type_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Год:").pack(pady=5)
        year_spinbox = ttk.Spinbox(dialog, from_=2000, to=datetime.now().year, width=10)
        year_spinbox.set(datetime.now().year)
        year_spinbox.pack(pady=5)
        
        ttk.Label(dialog, text="Описание:").pack(pady=5)
        desc_text = scrolledtext.ScrolledText(dialog, width=50, height=10)
        desc_text.pack(pady=5)
        
        def save():
            title = title_entry.get().strip()
            entry_type = type_combo.get()
            year = int(year_spinbox.get())
            description = desc_text.get('1.0', tk.END).strip()
            
            if not title:
                messagebox.showwarning("Ошибка", "Введите название")
                return
            
            entry_id = self.db.create_entry(title, entry_type, year, "")
            if entry_id:
                messagebox.showinfo("Успех", "Запись добавлена")
                dialog.destroy()
                self.refresh_entries()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить запись")
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def edit_entry(self):
        """Редактирование записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись")
            return
        
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]
        
        # Найти запись
        entry = None
        for e in self.entries:
            if e['id'] == entry_id:
                entry = e
                break
        
        if not entry:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать запись")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Название:").pack(pady=5)
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.insert(0, entry['title'])
        title_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Тип:").pack(pady=5)
        type_combo = ttk.Combobox(dialog, 
                                  values=['article', 'book', 'thesis', 'conference', 'other'],
                                  state='readonly')
        type_combo.set(entry['entry_type'])
        type_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Год:").pack(pady=5)
        year_spinbox = ttk.Spinbox(dialog, from_=2000, to=datetime.now().year, width=10)
        year_spinbox.set(entry['year'])
        year_spinbox.pack(pady=5)
        
        ttk.Label(dialog, text="Описание:").pack(pady=5)
        desc_text = scrolledtext.ScrolledText(dialog, width=50, height=10)
        desc_text.insert('1.0', entry.get('description', ''))
        desc_text.pack(pady=5)
        
        def save():
            title = title_entry.get().strip()
            entry_type = type_combo.get()
            year = int(year_spinbox.get())
            description = desc_text.get('1.0', tk.END).strip()
            
            if not title:
                messagebox.showwarning("Ошибка", "Введите название")
                return
            
            success = self.db.update_entry(entry_id, title, entry_type, year)
            if success:
                messagebox.showinfo("Успех", "Запись обновлена")
                dialog.destroy()
                self.refresh_entries()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить запись")
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=20)
    
    def delete_entry(self):
        """Удаление записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись")
            return
        
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]
        entry_title = item['values'][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить запись '{entry_title}'?"):
            if self.db.delete_entry(entry_id):
                messagebox.showinfo("Успех", "Запись удалена")
                self.refresh_entries()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить запись")
    
    def create_file(self):
        """Создание файла для выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись")
            return
        
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]
        title = item['values'][1]
        
        filepath = self.fm.create_md_file(entry_id, title)
        if filepath:
            messagebox.showinfo("Успех", f"Создан файл: {os.path.basename(filepath)}")
            self.refresh_files()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать файл")
    
    def open_file(self):
        """Открытие выбранного файла"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите файл")
            return
        
        filename = self.files_listbox.get(selection[0])
        filepath = os.path.join('reports', filename)
        
        self.fm.open_md_file_external(filepath)
    
    def generate_excel(self):
        """Генерация Excel отчета"""
        filename = self.exporter.generate_excel_report()
        if filename:
            messagebox.showinfo("Успех", f"Отчет сохранен: {filename}")
            self.refresh_files()
    
    def generate_word(self):
        """Генерация Word отчета"""
        filename = self.exporter.generate_word_report()
        if filename:
            messagebox.showinfo("Успех", f"Отчет сохранен: {filename}")
            self.refresh_files()
    
    def generate_pdf(self):
        """Генерация PDF отчета"""
        filename = self.exporter.generate_pdf_report()
        if filename:
            messagebox.showinfo("Успех", f"Отчет сохранен: {filename}")
            self.refresh_files()