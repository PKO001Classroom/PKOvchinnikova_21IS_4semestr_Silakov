#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import messagebox
from src.gui import GradingApp

def main():
    try:
        root = tk.Tk()
        app = GradingApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить программу:\n{str(e)}")

if __name__ == "__main__":
    main()