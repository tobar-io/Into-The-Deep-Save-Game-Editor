"""
Datei-Handler für das Laden und Speichern von Savegames
"""
import json
import os
import datetime
import shutil
from pathlib import Path
from typing import Dict, Optional
from tkinter import filedialog, messagebox

from .savegame_data import SaveGameData, now_timestamp_str
from .config import DEFAULT_OPEN_DIR


class FileHandler:
    """Verwaltet Datei-Operationen für Savegames"""
    
    def __init__(self, savegame_data: SaveGameData):
        self.savegame_data = savegame_data
        self.initialdir = self._get_initial_directory()
    
    def _get_initial_directory(self) -> str:
        """Bestimmt das Standard-Verzeichnis für Datei-Dialoge"""
        try:
            if os.path.isdir(DEFAULT_OPEN_DIR):
                return DEFAULT_OPEN_DIR
            else:
                return os.path.expanduser("~")
        except Exception:
            return os.path.expanduser("~")
    
    def open_file(self) -> bool:
        """Öffnet eine Savegame-Datei über einen Dialog"""
        path = filedialog.askopenfilename(
            title="Savegame öffnen",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")],
            initialdir=self.initialdir
        )
        
        if not path:
            return False
        
        return self.load_from_path(path)
    
    def load_from_path(self, path: str) -> bool:
        """Lädt eine Savegame-Datei von einem bestimmten Pfad"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.savegame_data.set_data(data)
            self.savegame_data.set_file_path(path)
            return True
            
        except Exception as e:
            messagebox.showerror("Fehler beim Öffnen", str(e))
            return False
    
    def save_file(self) -> bool:
        """Speichert die aktuelle Datei"""
        if not self.savegame_data.get_file_path():
            return self.save_file_as()
        
        return self._write_to_path(self.savegame_data.get_file_path())
    
    def save_file_as(self) -> bool:
        """Speichert die Datei unter einem neuen Namen"""
        path = filedialog.asksaveasfilename(
            title="Speichern unter",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")],
            initialdir=self.initialdir
        )
        
        if not path:
            return False
        
        return self._write_to_path(path)
    
    def _write_to_path(self, path: str) -> bool:
        """Schreibt die Savegame-Daten in eine Datei"""
        try:
            # Aktuellen Timestamp setzen
            self.savegame_data.data["lastSaveTimestamp"] = now_timestamp_str()
            
            # Schön formatieren und speichern
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.savegame_data.data, f, indent=4, ensure_ascii=False)
            
            self.savegame_data.set_file_path(path)
            self.savegame_data.set_modified(False)
            return True
            
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))
            return False
    
    def create_backup(self) -> bool:
        """Erstellt ein Backup der aktuellen Datei"""
        file_path = self.savegame_data.get_file_path()
        
        if not file_path or not os.path.isfile(file_path):
            messagebox.showinfo("Backup", "Speichere die Datei zuerst, dann Backup erneut versuchen.")
            return False
        
        try:
            base = os.path.splitext(file_path)[0]
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_path = f"{base}.bak.{stamp}.json"
            
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(self.savegame_data.data, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Backup fehlgeschlagen", str(e))
            return False
    
    def get_backup_filename(self) -> Optional[str]:
        """Generiert einen Backup-Dateinamen"""
        file_path = self.savegame_data.get_file_path()
        
        if not file_path:
            return None
        
        base = os.path.splitext(file_path)[0]
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{os.path.basename(base)}.bak.{stamp}.json"