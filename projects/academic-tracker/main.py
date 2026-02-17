import tkinter as tk
from gui import AcademicTrackerApp

def main():
    try:
        print("Запуск Личного трекера академической школы...")
        root = tk.Tk()
        app = AcademicTrackerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()