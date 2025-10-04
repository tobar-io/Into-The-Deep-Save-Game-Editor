"""
Launcher für die modulare Version des Save Game Editors
"""
import sys
import os

# Füge das src-Verzeichnis zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Importiere und starte die Anwendung
from src.main import SaveGameEditorApp

if __name__ == "__main__":
    app = SaveGameEditorApp()
    app.mainloop()