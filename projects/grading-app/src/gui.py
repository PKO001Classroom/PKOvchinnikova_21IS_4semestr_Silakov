"""
Модуль графического интерфейса для приложения "Оценивание"
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple

from . import database
from . import models
from . import utils


class GradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт оценок студентов")
        self.root.geometry("1000x700")

        # Инициализация базы данных
        database.init_db("grades.db")

        # Данные для хранения
        self.current_students: List[Tuple] = []
        self.current_subjects: List[Tuple] = []

        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Создаем вкладки
        self.tab_students = tk.Frame(self.notebook)
        self.tab_subjects = tk.Frame(self.notebook)
        self.tab_grades = tk.Frame(self.notebook)
        self.tab_stats = tk.Frame(self.notebook)

        self.notebook.add(self.tab_students, text="👥 Студенты")
        self.notebook.add(self.tab_subjects, text="📚 Предметы")
        self.notebook.add(self.tab_grades, text="📊 Оценки")
        self.notebook.add(self.tab_stats, text="📈 Статистика")

        # Создаем содержимое вкладок
        self._create_students_tab()
        self._create_subjects_tab()
        self._create_grades_tab()
        self._create_stats_tab()

        # Статус бар
        self.status_bar = tk.Label(root, text="Готово", bd=1, relief=tk.SUNKEN,
                                   anchor=tk.W, padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Обновляем данные при запуске
        self.refresh_students()
        self.refresh_subjects()

    def _create_students_tab(self):
        """Создание вкладки для управления студентами"""
        # Заголовок
        tk.Label(self.tab_students, text="Управление студентами",
                 font=("Arial", 14, "bold"), fg="#2196F3").pack(pady=(10, 20))

        # Фрейм для формы добавления
        form_frame = tk.Frame(self.tab_students)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="ФИО студента:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.student_name_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.student_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Номер зачётки:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.student_id_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.student_id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="➕ Добавить студента",
                 command=self._add_student,
                 bg="#4CAF50", fg="white",
                 font=("Arial", 10, "bold"), padx=20).grid(row=2, column=0, columnspan=2, pady=15)

        # Фрейм для списка студентов
        list_frame = tk.Frame(self.tab_students)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.students_listbox = tk.Listbox(list_frame, height=15,
                                           yscrollcommand=scrollbar.set,
                                           font=("Consolas", 10))
        self.students_listbox.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar.config(command=self.students_listbox.yview)

        # Кнопка обновления
        tk.Button(self.tab_students, text="🔄 Обновить список",
                 command=self.refresh_students,
                 bg="#FF9800", fg="white").pack(pady=5)

    def _create_subjects_tab(self):
        """Создание вкладки для управления предметами"""
        # Заголовок
        tk.Label(self.tab_subjects, text="Управление предметами",
                 font=("Arial", 14, "bold"), fg="#2196F3").pack(pady=(10, 20))

        # Фрейм для формы добавления
        form_frame = tk.Frame(self.tab_subjects)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Название предмета:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.subject_name_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.subject_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="➕ Добавить предмет",
                 command=self._add_subject,
                 bg="#4CAF50", fg="white",
                 font=("Arial", 10, "bold"), padx=20).grid(row=1, column=0, columnspan=2, pady=15)

        # Фрейм для списка предметов
        list_frame = tk.Frame(self.tab_subjects)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.subjects_listbox = tk.Listbox(list_frame, height=15,
                                           yscrollcommand=scrollbar.set,
                                           font=("Consolas", 10))
        self.subjects_listbox.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar.config(command=self.subjects_listbox.yview)

        # Кнопка обновления
        tk.Button(self.tab_subjects, text="🔄 Обновить список",
                 command=self.refresh_subjects,
                 bg="#FF9800", fg="white").pack(pady=5)

    def _create_grades_tab(self):
        """Создание вкладки для выставления оценок"""
        # Заголовок
        tk.Label(self.tab_grades, text="Выставление оценок",
                 font=("Arial", 14, "bold"), fg="#2196F3").pack(pady=(10, 20))

        # Фрейм для выбора студента и предмета
        select_frame = tk.Frame(self.tab_grades)
        select_frame.pack(pady=10)

        tk.Label(select_frame, text="Студент:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.grade_student_combo = ttk.Combobox(select_frame, width=40, state="readonly", font=("Arial", 10))
        self.grade_student_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(select_frame, text="Предмет:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.grade_subject_combo = ttk.Combobox(select_frame, width=40, state="readonly", font=("Arial", 10))
        self.grade_subject_combo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(select_frame, text="Оценка (2-5):", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.grade_entry = tk.Entry(select_frame, width=10, font=("Arial", 10))
        self.grade_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(select_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.grade_date_entry = tk.Entry(select_frame, width=20, font=("Arial", 10))
        self.grade_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.grade_date_entry.insert(0, utils.get_current_date())

        tk.Button(select_frame, text="💾 Сохранить оценку",
                 command=self._add_grade,
                 bg="#4CAF50", fg="white",
                 font=("Arial", 10, "bold"), padx=20).grid(row=4, column=0, columnspan=2, pady=20)

        # Фрейм для отображения оценок
        grades_frame = tk.LabelFrame(self.tab_grades, text="Последние оценки")
        grades_frame.pack(fill='both', expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(grades_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.grades_listbox = tk.Listbox(grades_frame, height=10,
                                         yscrollcommand=scrollbar.set,
                                         font=("Consolas", 10))
        self.grades_listbox.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar.config(command=self.grades_listbox.yview)

    def _create_stats_tab(self):
        """Создание вкладки для статистики"""
        # Заголовок
        tk.Label(self.tab_stats, text="Статистика успеваемости",
                 font=("Arial", 14, "bold"), fg="#2196F3").pack(pady=(10, 20))

        # Фрейм для выбора студента
        select_frame = tk.Frame(self.tab_stats)
        select_frame.pack(pady=10)

        tk.Label(select_frame, text="Выберите студента:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.stats_student_combo = ttk.Combobox(select_frame, width=40, state="readonly", font=("Arial", 10))
        self.stats_student_combo.pack(side=tk.LEFT, padx=5)
        self.stats_student_combo.bind('<<ComboboxSelected>>', self._show_stats)

        # Фрейм для отображения статистики
        stats_frame = tk.Frame(self.tab_stats)
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Текстовое поле для статистики
        self.stats_text = tk.Text(stats_frame, wrap=tk.WORD, font=("Consolas", 10),
                                   height=20, width=80)
        self.stats_text.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar = tk.Scrollbar(stats_frame, command=self.stats_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.config(yscrollcommand=scrollbar.set)

    def refresh_students(self):
        """Обновление списка студентов"""
        self.current_students = database.get_all_students("grades.db")
        self.students_listbox.delete(0, tk.END)

        student_display_list = []
        for student_row in self.current_students:
            student = models.Student.from_db_row(student_row)
            display = student.display_string()
            student_display_list.append(display)
            self.students_listbox.insert(tk.END, display)

        # Обновляем комбобоксы
        self.grade_student_combo['values'] = student_display_list
        self.stats_student_combo['values'] = student_display_list

        self._update_status(f"Загружено студентов: {len(self.current_students)}")

    def refresh_subjects(self):
        """Обновление списка предметов"""
        self.current_subjects = database.get_all_subjects("grades.db")
        self.subjects_listbox.delete(0, tk.END)

        subject_display_list = []
        for subject_row in self.current_subjects:
            subject = models.Subject.from_db_row(subject_row)
            subject_display_list.append(subject.name)
            self.subjects_listbox.insert(tk.END, subject.name)

        self.grade_subject_combo['values'] = subject_display_list

    def _add_student(self):
        """Добавление нового студента"""
        name = self.student_name_entry.get().strip()
        student_id = self.student_id_entry.get().strip()

        if not name or not student_id:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        result = database.add_student("grades.db", name, student_id)
        if result:
            messagebox.showinfo("Успех", f"Студент {name} добавлен")
            self.student_name_entry.delete(0, tk.END)
            self.student_id_entry.delete(0, tk.END)
            self.refresh_students()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить студента (возможно, такой номер зачётки уже есть)")

    def _add_subject(self):
        """Добавление нового предмета"""
        name = self.subject_name_entry.get().strip()

        if not name:
            messagebox.showwarning("Ошибка", "Введите название предмета")
            return

        result = database.add_subject("grades.db", name)
        if result:
            messagebox.showinfo("Успех", f"Предмет '{name}' добавлен")
            self.subject_name_entry.delete(0, tk.END)
            self.refresh_subjects()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить предмет (возможно, он уже есть)")

    def _add_grade(self):
        """Добавление оценки"""
        student_index = self.grade_student_combo.current()
        subject_index = self.grade_subject_combo.current()
        grade_str = self.grade_entry.get().strip()
        date = self.grade_date_entry.get().strip()

        if student_index == -1 or subject_index == -1:
            messagebox.showwarning("Ошибка", "Выберите студента и предмет")
            return

        if not grade_str or not date:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        try:
            grade = int(grade_str)
            if not utils.validate_grade(grade):
                messagebox.showwarning("Ошибка", "Оценка должна быть от 2 до 5")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Оценка должна быть числом")
            return

        if not utils.validate_date(date):
            messagebox.showwarning("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        student_id = self.current_students[student_index][0]
        subject_id = self.current_subjects[subject_index][0]

        result = database.add_grade("grades.db", student_id, subject_id, grade, date)
        if result:
            messagebox.showinfo("Успех", "Оценка сохранена")
            self.grade_entry.delete(0, tk.END)
            self.grade_date_entry.delete(0, tk.END)
            self.grade_date_entry.insert(0, utils.get_current_date())
            self._update_grades_list(student_id)
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить оценку")

    def _update_grades_list(self, student_id: int):
        """Обновление списка оценок для студента"""
        self.grades_listbox.delete(0, tk.END)
        grades = database.get_grades_for_student("grades.db", student_id)

        if grades:
            for grade in grades:
                self.grades_listbox.insert(tk.END, f"{grade[1]} | {grade[2]} | {grade[3]}")
        else:
            self.grades_listbox.insert(tk.END, "У студента пока нет оценок")

    def _show_stats(self, event=None):
        """Показ статистики для выбранного студента"""
        student_index = self.stats_student_combo.current()
        if student_index == -1:
            return

        student_id = self.current_students[student_index][0]
        student_name = self.current_students[student_index][1]

        # Очищаем текстовое поле
        self.stats_text.delete('1.0', tk.END)

        # Получаем оценки
        grades = database.get_grades_for_student("grades.db", student_id)

        if not grades:
            self.stats_text.insert('1.0', f"У студента {student_name} пока нет оценок")
            return

        # Группируем оценки по предметам
        subjects_grades = {}
        for grade in grades:
            subject = grade[1]
            if subject not in subjects_grades:
                subjects_grades[subject] = []
            subjects_grades[subject].append(grade[2])

        # Выводим статистику
        self.stats_text.insert('end', f"📊 СТАТИСТИКА ДЛЯ СТУДЕНТА: {student_name}\n")
        self.stats_text.insert('end', "=" * 50 + "\n\n")

        all_grades = []
        for subject, subject_grades in subjects_grades.items():
            self.stats_text.insert('end', f"📚 {subject}:\n")
            self.stats_text.insert('end', f"   Оценки: {', '.join(map(str, subject_grades))}\n")
            avg = utils.calculate_average(subject_grades)
            self.stats_text.insert('end', f"   Средний балл: {avg}\n\n")
            all_grades.extend(subject_grades)

        # Общая статистика
        overall_avg = utils.calculate_average(all_grades)
        self.stats_text.insert('end', "=" * 50 + "\n")
        self.stats_text.insert('end', f"📈 ОБЩАЯ СТАТИСТИКА:\n")
        self.stats_text.insert('end', f"   Всего оценок: {len(all_grades)}\n")
        self.stats_text.insert('end', f"   Средний балл по всем предметам: {overall_avg}\n")

        # Обновляем список оценок на вкладке оценок
        self._update_grades_list(student_id)

    def _update_status(self, text: str):
        """Обновление текста в статусной строке"""
        self.status_bar.config(text=text)