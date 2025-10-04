"""
Asset-Manager für das Laden und Verwalten von Spiel-Assets
"""
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from tkinter import filedialog, messagebox
from .config import ASSET_CATEGORIES


class AssetManager:
    """Verwaltet Spiel-Assets aus der GameAssetSummary.json"""
    
    def __init__(self):
        self.assets = {category: [] for category in ASSET_CATEGORIES}
        self.loaded = False
        # Lokale Asset-Datei im Projektverzeichnis
        self.local_asset_file = Path(__file__).parent.parent / "GameAssetSummary.json"
    
    def load_assets(self) -> bool:
        """Lädt die lokale GameAssetSummary.json"""
        if not self.local_asset_file.exists():
            self.loaded = False
            return False
        
        try:
            # utf-8-sig unterstützt UTF-8 mit und ohne BOM
            with open(self.local_asset_file, "r", encoding="utf-8-sig") as f:
                loaded = json.load(f)
                # Asset-Listen aktualisieren
                for key in self.assets.keys():
                    if key in loaded:
                        self.assets[key] = [x for x in loaded[key] if x]  # Leere Strings filtern
                self.loaded = True
                return True
        except Exception as e:
            print(f"Fehler beim Laden der Asset-Datei: {e}")
            self.loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Prüft ob Assets geladen wurden"""
        return self.loaded
    
    def get_assets(self, category: str) -> List[str]:
        """Gibt Assets einer bestimmten Kategorie zurück"""
        return self.assets.get(category, [])
    
    def get_all_assets(self) -> Dict[str, List[str]]:
        """Gibt alle Assets zurück"""
        return self.assets.copy()
    
    def get_asset_count(self) -> int:
        """Gibt die Gesamtzahl der Assets zurück"""
        return sum(len(assets) for assets in self.assets.values())
    
    def reload_assets(self) -> bool:
        """Lädt Assets neu"""
        return self.load_assets()
    
    def get_local_asset_file_path(self) -> Path:
        """Gibt den Pfad zur lokalen Asset-Datei zurück"""
        return self.local_asset_file
    
    def has_local_asset_file(self) -> bool:
        """Prüft ob die lokale Asset-Datei existiert"""
        return self.local_asset_file.exists()
    
    def import_asset_file(self, source_path: Optional[str] = None) -> bool:
        """Importiert eine neue Asset-Datei ins Projekt"""
        if source_path is None:
            # File-Dialog öffnen
            source_path = filedialog.askopenfilename(
                title="Asset-Datei importieren",
                filetypes=[
                    ("JSON Dateien", "*.json"),
                    ("Alle Dateien", "*.*")
                ],
                initialdir=str(Path.home())
            )
        
        if not source_path:
            return False
        
        source_file = Path(source_path)
        if not source_file.exists():
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {source_file}")
            return False
        
        try:
            # Erst testen ob die Datei gültig ist
            with open(source_file, "r", encoding="utf-8-sig") as f:
                test_data = json.load(f)
                
            # Prüfen ob es eine gültige Asset-Datei ist
            if not isinstance(test_data, dict):
                messagebox.showerror("Fehler", "Ungültiges Dateiformat: JSON-Objekt erwartet")
                return False
            
            # Backup der aktuellen Datei erstellen falls sie existiert
            if self.local_asset_file.exists():
                backup_path = self.local_asset_file.with_suffix('.json.backup')
                shutil.copy2(self.local_asset_file, backup_path)
            
            # Neue Datei kopieren
            shutil.copy2(source_file, self.local_asset_file)
            
            # Assets neu laden
            if self.load_assets():
                messagebox.showinfo("Erfolg", 
                    f"Asset-Datei erfolgreich importiert!\n"
                    f"Quelle: {source_file.name}\n"
                    f"Assets geladen: {self.get_asset_count()}")
                return True
            else:
                messagebox.showerror("Fehler", "Asset-Datei konnte nicht geladen werden")
                return False
                
        except json.JSONDecodeError as e:
            messagebox.showerror("Fehler", f"Ungültige JSON-Datei: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Importieren: {e}")
            return False
    
    def export_asset_file(self, target_path: Optional[str] = None) -> bool:
        """Exportiert die aktuelle Asset-Datei"""
        if not self.has_local_asset_file():
            messagebox.showerror("Fehler", "Keine Asset-Datei zum Exportieren vorhanden")
            return False
        
        if target_path is None:
            # File-Dialog öffnen
            target_path = filedialog.asksaveasfilename(
                title="Asset-Datei exportieren",
                defaultextension=".json",
                filetypes=[
                    ("JSON Dateien", "*.json"),
                    ("Alle Dateien", "*.*")
                ],
                initialfile="GameAssetSummary.json"
            )
        
        if not target_path:
            return False
        
        try:
            shutil.copy2(self.local_asset_file, target_path)
            messagebox.showinfo("Erfolg", f"Asset-Datei exportiert nach:\n{target_path}")
            return True
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Exportieren: {e}")
            return False
    
    def create_empty_asset_file(self) -> bool:
        """Erstellt eine leere Asset-Datei mit allen Kategorien"""
        empty_assets = {category: [] for category in ASSET_CATEGORIES}
        
        try:
            with open(self.local_asset_file, "w", encoding="utf-8") as f:
                json.dump(empty_assets, f, indent=2, ensure_ascii=False)
            
            self.load_assets()
            return True
        except Exception as e:
            print(f"Fehler beim Erstellen der leeren Asset-Datei: {e}")
            return False