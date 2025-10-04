"""
Konfiguration und Konstanten für den Save Game Editor
"""
import os

# App-Informationen
APP_TITLE = "Into The Deep – Savegame Editor"
APP_VERSION = "1.0.0"

# Standard-Verzeichnisse
DEFAULT_OPEN_DIR = os.path.expandvars(r"%LOCALAPPDATA%\..\LocalLow\tobar_io\Into The Deep\saves")

# Enums aus C#-Scripten
LEVEL_STATUS_ENUM = {
    0: "Hidden",
    1: "Revealed",
    2: "Unlocked",
    3: "Locked",
    4: "Completed"
}

QUEST_STATUS_ENUM = {
    0: "NotStarted",
    1: "InProgress",
    2: "Completed",
    3: "Failed"
}

# Asset-Kategorien
ASSET_CATEGORIES = [
    "Characters",
    "Weapons",
    "Levels",
    "Quests",
    "Actions",
    "Wearables",
    "QuestGoals",
    "Equipment"
]