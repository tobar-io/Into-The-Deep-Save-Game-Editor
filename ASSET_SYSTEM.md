# Asset-System Dokumentation

## Überblick

Das Asset-System wurde von einem automatischen Multi-Pfad-System zu einem lokalen dateibasierten System umgestellt. Dies bietet bessere Kontrolle und Flexibilität.

## Neue Funktionsweise

### Lokale Asset-Datei
- **Speicherort:** `GameAssetSummary.json` im Hauptverzeichnis
- **Format:** JSON mit Asset-Kategorien als Top-Level-Keys
- **Unterstützte Kategorien:** Characters, Weapons, Levels, Quests, Actions, Wearables, QuestGoals, Equipment

### Asset-Manager Funktionen

#### Laden
```python
asset_manager = AssetManager()
loaded = asset_manager.load_assets()  # Lädt lokale Datei
```

#### Importieren
```python
# Mit File-Dialog
success = asset_manager.import_asset_file()

# Mit spezifischem Pfad
success = asset_manager.import_asset_file("/path/to/new/asset/file.json")
```

#### Exportieren
```python
# Mit File-Dialog
success = asset_manager.export_asset_file()

# Mit spezifischem Pfad
success = asset_manager.export_asset_file("/path/to/export/location.json")
```

#### Status prüfen
```python
has_file = asset_manager.has_local_asset_file()  # True/False
is_loaded = asset_manager.is_loaded()            # True/False
file_path = asset_manager.get_local_asset_file_path()  # Path-Objekt
```

### GUI-Features

#### Assets-Tab
- **Import-Button:** "Asset-DB importieren" - öffnet File-Dialog zum Importieren
- **Export-Button:** "Exportieren" - öffnet File-Dialog zum Exportieren
- **Automatische Aktualisierung:** Nach Import werden alle Anzeigen aktualisiert

#### Hauptmenü
- **Assets-Menü:** Neues Menü mit Import/Export/Reload-Funktionen
- **Import:** Assets → Asset-DB importieren…
- **Export:** Assets → Asset-DB exportieren…
- **Reload:** Assets → Asset-DB neu laden

### Fallback-Verhalten

#### Keine Asset-Datei vorhanden
- Meldung: "Noch keine Asset-Datei vorhanden - verwenden Sie 'Asset-DB importieren'"
- Alle Dropdown-Listen zeigen Hinweise an
- Textfelder bleiben voll funktionsfähig

#### Asset-Datei nicht ladbar
- Meldung: "Asset-Datei konnte nicht geladen werden"
- Backup-Funktionalität beim Import
- Detaillierte Fehlermeldungen

## Migration von altem System

### Vorher (Automatische Suche)
- Suchte in mehreren vordefinierte Pfade
- Automatisches Laden beim Start
- Keine Benutzer-Kontrolle über Asset-Quelle

### Nachher (Lokale Datei)
- Eine lokale `GameAssetSummary.json` im Projekt
- Manueller Import von externen Quellen
- Vollständige Benutzer-Kontrolle
- Backup-Funktionalität

## Workflow für Nutzer

### Erstmalige Einrichtung
1. Editor starten (zeigt "Noch keine Asset-Datei vorhanden")
2. Assets-Tab öffnen
3. "Asset-DB importieren" klicken
4. Gewünschte `GameAssetSummary.json` auswählen
5. Assets werden importiert und geladen

### Aktualisierung der Assets
1. Neue Asset-Datei von der Spielentwicklung erhalten
2. "Asset-DB importieren" verwenden
3. Alte Datei wird automatisch als Backup gespeichert
4. Neue Assets stehen sofort zur Verfügung

### Export für Backup/Sharing
1. "Asset-DB exportieren" verwenden
2. Datei an gewünschtem Ort speichern
3. Kann mit anderen Nutzern geteilt werden

## Technische Details

### Backup-System
- Bei Import wird die existierende Datei als `.json.backup` gesichert
- Automatische Validierung der JSON-Struktur vor Import
- Rollback-Möglichkeit bei Fehlern

### Fehlerbehandlung
- Detaillierte Fehlermeldungen bei Import-Problemen
- Graceful Fallback bei fehlenden/defekten Dateien
- Status-Updates in der GUI

### Performance
- Assets werden nur einmal beim Start/Import geladen
- Keine wiederholten Dateisystem-Zugriffe
- Effiziente Speicher-Nutzung

## Dateiformat

### Erwartete JSON-Struktur
```json
{
  "Characters": ["Character1", "Character2", ...],
  "Weapons": ["Weapon1", "Weapon2", ...],
  "Levels": ["Level1", "Level2", ...],
  "Quests": ["Quest1", "Quest2", ...],
  "Actions": ["Action1", "Action2", ...],
  "Wearables": ["Wearable1", "Wearable2", ...],
  "QuestGoals": ["Goal1", "Goal2", ...],
  "Equipment": ["Equipment1", "Equipment2", ...]
}
```

### Validierung
- JSON-Format wird beim Import geprüft
- Leere Strings werden automatisch gefiltert
- Fehlende Kategorien werden als leere Listen behandelt
- UTF-8 Encoding mit und ohne BOM unterstützt