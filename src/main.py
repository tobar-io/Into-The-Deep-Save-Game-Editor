"""
Modulare Haupt-Anwendung für den Save Game Editor
"""
import os
from tkinter import Tk, StringVar, Menu, messagebox, N, S, E, W
from tkinter import ttk

from .config import APP_TITLE, DEFAULT_OPEN_DIR
from .savegame_data import SaveGameData
from .asset_manager import AssetManager
from .file_handler import FileHandler
from .tabs.overview_tab import OverviewTab
from .tabs.crew_tab import CrewTab
from .tabs.inventory_tab import InventoryTab
from .tabs.weapons_tab import WeaponsTab
from .tabs.quests_tab import QuestsTab
from .tabs.levels_tab import LevelsTab
from .tabs.assets_tab import AssetsTab


class SaveGameEditorApp(Tk):
    """Hauptanwendung des Save Game Editors"""
    
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x700")
        self.minsize(1000, 650)
        
        # Core-Komponenten initialisieren
        self.savegame_data = SaveGameData()
        self.asset_manager = AssetManager()
        self.file_handler = FileHandler(self.savegame_data)
        
        # Status-Variable
        self.status_var = StringVar(value="Bereit")
        
        # Assets laden
        assets_loaded = self.asset_manager.load_assets()
        
        # UI aufbauen
        self._build_menu()
        self._build_content()
        
        # Status setzen basierend auf Asset-Verfügbarkeit
        if not self.asset_manager.has_local_asset_file():
            self._set_status("Info: Noch keine Asset-Datei vorhanden - verwenden Sie 'Asset-DB importieren' im Assets-Tab")
        elif not assets_loaded:
            self._set_status("Warnung: Asset-Datei konnte nicht geladen werden")
        else:
            asset_count = self.asset_manager.get_asset_count()
            self._set_status(f"Bereit - Asset-Datei geladen: {asset_count} Assets")
        
        # Leeres Savegame starten
        self._refresh_all_tabs()
        
        # Title-Update-Loop starten
        self.after(250, self._tick_title)
    
    def _build_menu(self):
        """Erstellt die Menüleiste"""
        menubar = Menu(self)
        
        # Datei-Menü
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Öffnen…", command=self.on_open)
        file_menu.add_command(label="Speichern", command=self.on_save)
        file_menu.add_command(label="Speichern unter…", command=self.on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Backup anlegen", command=self.on_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.on_exit)
        menubar.add_cascade(label="Datei", menu=file_menu)
        
        # Bearbeiten-Menü
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Max Geld (999999)", command=self.action_max_money)
        edit_menu.add_command(label="Alle Crew heilen", command=self.action_heal_all)
        edit_menu.add_command(label="AP auffüllen", command=self.action_refill_ap_all)
        edit_menu.add_command(label="Munition auffüllen", command=self.action_refill_ammo_all)
        edit_menu.add_command(label="Godmode umschalten (alle)", command=self.action_toggle_god_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Alle Level freischalten", command=self.action_unlock_all_levels)
        menubar.add_cascade(label="Bearbeiten", menu=edit_menu)
        
        # Assets-Menü
        assets_menu = Menu(menubar, tearoff=0)
        assets_menu.add_command(label="Asset-DB importieren…", command=self.import_asset_database)
        assets_menu.add_command(label="Asset-DB exportieren…", command=self.export_asset_database)
        assets_menu.add_separator()
        assets_menu.add_command(label="Asset-DB neu laden", command=self.reload_asset_database)
        menubar.add_cascade(label="Assets", menu=assets_menu)
        
        # Hilfe-Menü
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Über", command=lambda: messagebox.showinfo(
            "Über", f"{APP_TITLE}\n\nEin modularer Editor für JSON-Savegames.\nMade with Tkinter."
        ))
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        
        self.config(menu=menubar)
    
    def _build_content(self):
        """Erstellt den Hauptinhalt"""
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Tab-Container
        self.tabs = ttk.Notebook(root)
        self.tabs.grid(row=0, column=0, sticky=N+S+E+W)
        
        # Tabs erstellen
        self._create_tabs()
        
        # Statusleiste
        status = ttk.Label(root, textvariable=self.status_var, anchor="w")
        status.grid(row=1, column=0, sticky=E+W)
    
    def _create_tabs(self):
        """Erstellt alle Tab-Instanzen"""
        self.tab_instances = {}
        
        # Übersicht
        overview_tab = OverviewTab(self.tabs, self.savegame_data, self.asset_manager, self._set_status)
        self.tabs.add(overview_tab.get_frame(), text="Übersicht")
        self.tab_instances['overview'] = overview_tab
        
        # Crew
        crew_tab = CrewTab(self.tabs, self.savegame_data, self.asset_manager, self._set_status)
        self.tabs.add(crew_tab.get_frame(), text="Crew")
        self.tab_instances['crew'] = crew_tab
        
        # Inventar
        inventory_tab = InventoryTab(self.tabs, self.savegame_data, self.asset_manager, self._set_status)
        self.tabs.add(inventory_tab.get_frame(), text="Inventar")
        self.tab_instances['inventory'] = inventory_tab
        
        # Waffen
        weapons_tab = WeaponsTab(self.tabs, self.savegame_data, self.asset_manager, self._set_status)
        self.tabs.add(weapons_tab.get_frame(), text="Waffen")
        self.tab_instances['weapons'] = weapons_tab
        
        # Quests
        quests_tab = QuestsTab(self.tabs, self.savegame_data, self.asset_manager, self._set_status)
        self.tabs.add(quests_tab.get_frame(), text="Quests")
        self.tab_instances['quests'] = quests_tab
        
        # Level
        levels_tab = LevelsTab(self.tabs, self.savegame_data, self.asset_manager, self._set_status)
        self.tabs.add(levels_tab.get_frame(), text="Level")
        self.tab_instances['levels'] = levels_tab
        
        # Asset-Browser (nur wenn Assets geladen)
        if self.asset_manager.is_loaded():
            assets_tab = AssetsTab(self.tabs, self.savegame_data, self.asset_manager, self._set_status)
            self.tabs.add(assets_tab.get_frame(), text="Asset-Browser")
            self.tab_instances['assets'] = assets_tab
    
    def _refresh_all_tabs(self):
        """Aktualisiert alle Tabs mit aktuellen Daten"""
        for tab in self.tab_instances.values():
            tab.populate_data()
    
    def _set_status(self, text):
        """Setzt eine Statusnachricht"""
        self.status_var.set(text)
    
    def _tick_title(self):
        """Aktualisiert den Fenstertitel periodisch"""
        base = APP_TITLE
        file_path = self.savegame_data.get_file_path()
        
        if file_path:
            base += f" – {os.path.basename(file_path)}"
        
        if self.savegame_data.is_modified():
            base += " *"
        
        self.title(base)
        self.after(500, self._tick_title)
    
    # Datei-Operationen
    def on_open(self):
        """Öffnet eine Savegame-Datei"""
        if self.file_handler.open_file():
            self._set_status(f"Geladen: {os.path.basename(self.savegame_data.get_file_path())}")
            self._refresh_all_tabs()
    
    def on_save(self):
        """Speichert die aktuelle Datei"""
        if self.file_handler.save_file():
            self._set_status(f"Gespeichert: {os.path.basename(self.savegame_data.get_file_path())}")
    
    def on_save_as(self):
        """Speichert die Datei unter einem neuen Namen"""
        if self.file_handler.save_file_as():
            self._set_status(f"Gespeichert: {os.path.basename(self.savegame_data.get_file_path())}")
    
    def on_backup(self):
        """Erstellt ein Backup der aktuellen Datei"""
        if self.file_handler.create_backup():
            backup_name = self.file_handler.get_backup_filename()
            self._set_status(f"Backup erstellt: {backup_name}")
    
    def on_exit(self):
        """Beendet die Anwendung"""
        if self.savegame_data.is_modified():
            if not messagebox.askyesno("Beenden", "Es gibt ungespeicherte Änderungen. Wirklich beenden?"):
                return
        self.destroy()
    
    # Quick Actions (vereinfacht)
    def action_max_money(self):
        """Setzt Geld auf Maximum"""
        self.savegame_data.data["currency"] = 999999
        self.savegame_data.set_modified(True)
        self.tab_instances['overview'].populate_data()  # Übersicht aktualisieren
        self._set_status("Geld auf 999999 gesetzt.")
    
    def action_heal_all(self):
        """Heilt alle Crew-Mitglieder"""
        crew_list = self.savegame_data.data.get("crewStates", []) or []
        for c in crew_list:
            c["currentHP"] = float(c.get("maxHP", c.get("currentHP", 0.0)))
            c["isDead"] = False
        
        if crew_list:
            self.savegame_data.set_modified(True)
            self.tab_instances['crew'].populate_data()
            self._set_status("Alle Crew-Mitglieder geheilt.")
    
    def action_refill_ap_all(self):
        """Füllt AP für alle Crew-Mitglieder auf"""
        crew_list = self.savegame_data.data.get("crewStates", []) or []
        for c in crew_list:
            c["currentActionPoints"] = int(c.get("maxActionPoints", c.get("currentActionPoints", 0)))
        
        if crew_list:
            self.savegame_data.set_modified(True)
            self.tab_instances['crew'].populate_data()
            self._set_status("AP für alle aufgefüllt.")
    
    def action_refill_ammo_all(self):
        """Füllt Munition für alle Crew-Mitglieder auf"""
        crew_list = self.savegame_data.data.get("crewStates", []) or []
        for c in crew_list:
            w = c.get("equippedWeaponState", {}) or {}
            w["currentAmmo"] = int(w.get("maxAmmo", w.get("currentAmmo", 0)))
            w["durability"] = float(w.get("maxDurability", w.get("durability", 0.0)))
            c["equippedWeaponState"] = w
        
        if crew_list:
            self.savegame_data.set_modified(True)
            self.tab_instances['crew'].populate_data()
            self._set_status("Munition/Haltbarkeit für alle aufgefüllt.")
    
    def action_toggle_god_all(self):
        """Schaltet Godmode für alle Crew-Mitglieder um"""
        crew_list = self.savegame_data.data.get("crewStates", []) or []
        for c in crew_list:
            c["godMode"] = not bool(c.get("godMode", False))
        
        if crew_list:
            self.savegame_data.set_modified(True)
            self.tab_instances['crew'].populate_data()
            self._set_status("Godmode für alle umgeschaltet.")
    
    def action_unlock_all_levels(self):
        """Schaltet alle Level frei"""
        level_ids = [lv.get("levelID") for lv in self.savegame_data.data.get("levelStates", []) or [] 
                    if lv.get("levelID")]
        unlocked = self.savegame_data.data.setdefault("unlockedLevelIDs", [])
        
        changed = False
        for lid in level_ids:
            if lid not in unlocked:
                unlocked.append(lid)
                changed = True
        
        if changed:
            self.savegame_data.set_modified(True)
        
        self._set_status("Alle Level freigeschaltet (basierend auf levelStates).")
    
    def import_asset_database(self):
        """Importiert eine neue Asset-Datei"""
        if self.asset_manager.import_asset_file():
            # Assets-Tab aktualisieren falls vorhanden
            if hasattr(self, 'assets_tab'):
                self.assets_tab.refresh_assets()
            self._refresh_all_tabs()  # Alle Tabs aktualisieren für neue Asset-Daten
    
    def export_asset_database(self):
        """Exportiert die aktuelle Asset-Datei"""
        if self.asset_manager.export_asset_file():
            self._set_status("Asset-Datei erfolgreich exportiert.")
    
    def reload_asset_database(self):
        """Lädt die Asset-Datenbank neu"""
        if not self.asset_manager.has_local_asset_file():
            messagebox.showwarning("Keine Datei", 
                "Keine lokale Asset-Datei vorhanden.\n\n"
                "Verwenden Sie 'Asset-DB importieren' um eine Datei zu laden.")
            return
        
        # Neu laden
        if self.asset_manager.reload_assets():
            asset_count = self.asset_manager.get_asset_count()
            self._set_status(f"Asset-Datenbank neu geladen: {asset_count} Assets")
            
            # Assets-Tab aktualisieren falls vorhanden
            if hasattr(self, 'assets_tab'):
                self.assets_tab.refresh_assets()
        else:
            self._set_status("Fehler beim Neu-Laden der Asset-Datei.")


if __name__ == "__main__":
    app = SaveGameEditorApp()
    app.mainloop()