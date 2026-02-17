try:
    import tkinter
    print("✓ tkinter доступен")
except ImportError:
    print("✗ tkinter не доступен")

try:
    import psycopg2
    print("✓ psycopg2 доступен")
except ImportError:
    print("✗ psycopg2 не доступен")

try:
    import openpyxl
    print("✓ openpyxl доступен")
except ImportError:
    print("✗ openpyxl не доступен")

try:
    import docx
    print("✓ python-docx доступен")
except ImportError:
    print("✗ python-docx не доступен")

try:
    import matplotlib
    print("✓ matplotlib доступен")
except ImportError:
    print("✗ matplotlib не доступен")