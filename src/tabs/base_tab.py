"""
Basis-Klasse für alle Tab-Module
"""
from abc import ABC, abstractmethod
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..savegame_data import SaveGameData
    from ..asset_manager import AssetManager


class BaseTab(ABC):
    """Basis-Klasse für alle Tab-Implementierungen"""
    
    def __init__(self, parent: ttk.Widget, savegame_data: 'SaveGameData', 
                 asset_manager: 'AssetManager', status_callback=None):
        self.parent = parent
        self.savegame_data = savegame_data
        self.asset_manager = asset_manager
        self.status_callback = status_callback
        
        # Tab-Frame erstellen
        self.frame = ttk.Frame(parent)
        
        # UI aufbauen
        self.build_ui()
    
    @abstractmethod
    def build_ui(self) -> None:
        """Baut die Benutzeroberfläche des Tabs auf"""
        pass
    
    @abstractmethod
    def populate_data(self) -> None:
        """Lädt Daten in die UI-Komponenten"""
        pass
    
    def set_status(self, message: str) -> None:
        """Setzt eine Statusnachricht"""
        if self.status_callback:
            self.status_callback(message)
    
    def set_modified(self, modified: bool = True) -> None:
        """Markiert die Daten als geändert"""
        self.savegame_data.set_modified(modified)
    
    def get_frame(self) -> ttk.Frame:
        """Gibt den Tab-Frame zurück"""
        return self.frame