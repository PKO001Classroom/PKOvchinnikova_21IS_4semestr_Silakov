#!/usr/bin/env python3
"""
Точка входа в приложение IOM Planner
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from src.gui import IOMApp

def main():
    root = tk.Tk()
    app = IOMApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()