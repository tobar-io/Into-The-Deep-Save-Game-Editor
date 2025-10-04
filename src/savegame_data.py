"""
Datenmodell und Hilfsfunktionen für Save Game Daten
"""
import datetime
from typing import Any, Dict, List, Union


def now_timestamp_str() -> str:
    """Erstellt einen Timestamp-String im Format des Savegames"""
    # Beispiel-Format im Save: "10/01/2025 22:13:48"
    return datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def ensure_list(x: Any) -> List:
    """Stellt sicher, dass das Ergebnis eine Liste ist"""
    return x if isinstance(x, list) else []


def safe_get(dct: Dict, key: str, default: Any = None) -> Any:
    """Sicherer Dictionary-Zugriff"""
    return dct.get(key, default)


def deep_get(dct: Dict, path: List[str], default: Any = None) -> Any:
    """Verschachtelter Dictionary-Zugriff über einen Pfad"""
    cur = dct
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def deep_set(dct: Dict, path: List[str], value: Any) -> None:
    """Setzt einen Wert in einem verschachtelten Dictionary"""
    cur = dct
    for p in path[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[path[-1]] = value


def create_empty_savegame() -> Dict:
    """Erstellt eine leere Savegame-Datenstruktur"""
    return {
        "saveSlotName": "Neuer Speicherstand",
        "lastSaveTimestamp": now_timestamp_str(),
        "currency": 0,
        "rescuedDwarvesCount": 0,
        "lastSceneID": "",
        "crewStates": [],
        "activeSquadMemberIDs": [],
        "inventoryItemIDs": [],
        "inventoryHatIDs": [],
        "inventoryWeaponStates": [],
        "questStates": [],
        "unlockedLevelIDs": [],
        "completedLevelIDs": [],
        "levelStates": [],
        "bannerConfig": {
            "bannerIconID": "",
            "bannerBackgroundID": ""
        },
        "id": 0
    }


def create_weapon_state(weapon_id: str) -> Dict:
    """Erstellt einen neuen WeaponState mit Standardwerten"""
    return {
        "weaponSoTemplateID": weapon_id,
        "currentAmmo": 100,
        "maxAmmo": 100,
        "isReloading": False,
        "currentCooldown": 0,
        "appliedModifierIDs": [],
        "isEquipped": False,
        "isDrawn": False,
        "isBlocked": False,
        "damageMultiplier": 1.0,
        "firingRateMultiplier": 1.0,
        "spreadMultiplier": 1.0,
        "bulletsPerShotBonus": 0,
        "penetrationBonus": 0,
        "durability": 100.0,
        "maxDurability": 100.0
    }


class SaveGameData:
    """Zentrale Klasse für Savegame-Daten-Management"""
    
    def __init__(self):
        self.data = create_empty_savegame()
        self.modified = False
        self.file_path = None
    
    def set_data(self, data: Dict) -> None:
        """Setzt neue Savegame-Daten"""
        self.data = data
        self.modified = False
    
    def set_modified(self, modified: bool = True) -> None:
        """Markiert die Daten als geändert"""
        self.modified = modified
    
    def is_modified(self) -> bool:
        """Prüft ob die Daten geändert wurden"""
        return self.modified
    
    def get_file_path(self) -> str:
        """Gibt den aktuellen Dateipfad zurück"""
        return self.file_path
    
    def set_file_path(self, path: str) -> None:
        """Setzt den Dateipfad"""
        self.file_path = path