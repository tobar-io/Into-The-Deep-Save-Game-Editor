# Into The Deep – Savegame Editor

GUI-Editor für "Into The Deep" Savegames.

> **📝 Hinweis**: Dieses Projekt wurde komplett durch Vibecoding mit Claude erstellt. Mehr Kontext: [How I vibecoded a Python app with GitHub Copilot without knowing Python](https://www.tobar.io/how-i-vibecoded-a-python-app-with-github-copilot-without-knowing-python/)

## Schnellstart

```powershell
# Windows
"Start Editor.bat"

# Direkt mit Python
python SaveGameEditor.py
```

## Features

- **Crew-Management**: HP, AP, Level, Waffen, Equipment
- **Inventar**: Items, Wearables, Waffen verwalten  
- **Quest-System**: Status und Fortschritt bearbeiten
- **Level-Management**: Freischalten, Sterne, Statistiken
- **Asset-System**: Lokale Asset-Datenbank mit Import/Export

## Beispieldateien

- `sample_savegame.json` - Test-Savegame
- `sample_assets.json` - Asset-Datenbank

## Voraussetzungen

- Python 3.8+
- Keine externen Abhängigkeiten

## Projektstruktur

```
Into The Deep Save Game Editor/
├── src/                        # Modulare Architektur
├── SaveGameEditor.py           # Launcher
├── Start Editor.bat            # Windows Batch-Start
├── GameAssetSummary.json       # Asset-Datenbank
├── sample_*.json               # Beispieldateien
└── README.md                   # Diese Datei
```

## Verwendung

1. Editor starten
2. Savegame öffnen (Datei → Öffnen)
3. Daten bearbeiten
4. Speichern