#!/usr/bin/env python3
"""
Точка входа в приложение "Учёт личных достижений"
"""
import sys
import os

# Добавляем путь к проекту в системный путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import messagebox
from src.gui import AchievementsApp


def main():
    """Главная функция запуска приложения"""
    try:
        root = tk.Tk()
        app = AchievementsApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить программу:\n{str(e)}")


if __name__ == "__main__":
    main()