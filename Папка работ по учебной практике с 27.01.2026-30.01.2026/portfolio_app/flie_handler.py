# file_handler.py
import os
import re
import subprocess
import platform

class FileHandler:
    def __init__(self, base_dir="portfolio_md"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
    
    def create_md_file(self, title, content=""):
        # Очищаем название для файла
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = filename.replace(' ', '_')
        filename = filename[:50] + ".md"
        
        filepath = os.path.join(self.base_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def read_md_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def update_md_file(self, filepath, content):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def open_file(self, filepath):
        if platform.system() == 'Windows':
            os.startfile(filepath)
        else:
            try:
                subprocess.run(['open', filepath] if platform.system() == 'Darwin' 
                             else ['xdg-open', filepath])
            except:
                print(f"Файл: {filepath}")