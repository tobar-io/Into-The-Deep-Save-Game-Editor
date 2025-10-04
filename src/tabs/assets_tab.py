"""
Asset-Browser Tab für die Durchsuchung und Verwaltung von Game-Assets
"""
from tkinter import ttk, StringVar, END
from ..ui_components import tk_listbox, setup_grid_weights, create_section_label
from .base_tab import BaseTab


class AssetsTab(BaseTab):
    """Tab für Asset-Browser"""
    
    def __init__(self, parent, savegame_data, asset_manager, status_callback=None):
        # State
        self.current_asset_category = None
        
        # Variables
        self.var_asset_search = StringVar()
        
        super().__init__(parent, savegame_data, asset_manager, status_callback)
    
    def build_ui(self):
        """Baut die Benutzeroberfläche auf"""
        setup_grid_weights(self.frame, columns=[1, 3], rows=[0, 1])
        
        # Header
        create_section_label(self.frame, "Asset-Kategorien", 0, 1, pady=(8, 4))
        create_section_label(self.frame, "Verfügbare Assets", 0, 1, pady=(8, 4))
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Linke Seite - Kategorien
        left = ttk.Frame(self.frame, padding=8)
        left.grid(row=1, column=0, sticky="NSEW")
        
        # Import/Export Buttons
        button_frame = ttk.Frame(left)
        button_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Button(button_frame, text="Asset-DB importieren", 
                  command=self._import_assets).pack(side="left", padx=(0, 4))
        ttk.Button(button_frame, text="Exportieren", 
                  command=self._export_assets).pack(side="left")
        
        self.lst_asset_categories = tk_listbox(left, height=17)
        self.lst_asset_categories.pack(fill="both", expand=True)
        self.lst_asset_categories.bind("<<ListboxSelect>>", self.on_select_asset_category)
        
        # Rechte Seite - Asset-Liste mit Suche
        right = ttk.Frame(self.frame, padding=8)
        right.grid(row=1, column=1, sticky="NSEW")
        setup_grid_weights(right, columns=[1], rows=[0, 1, 0])
        
        # Suchfeld
        self._build_search_controls(right)
        
        # Asset-Liste
        self.lst_assets = tk_listbox(right, height=25)
        self.lst_assets.grid(row=1, column=0, sticky="NSEW")
        
        # Info-Label
        self.lbl_asset_info = ttk.Label(right, text="", foreground="gray")
        self.lbl_asset_info.grid(row=2, column=0, sticky="W", pady=(6, 0))
        
        # Asset-Statistiken
        self._build_asset_stats(right)
        
        # Kategorien befüllen
        self._populate_asset_categories()
    
    def _build_search_controls(self, parent):
        """Erstellt die Such-Steuerelemente"""
        search_frm = ttk.Frame(parent)
        search_frm.grid(row=0, column=0, sticky="EW", pady=(0, 8))
        setup_grid_weights(search_frm, columns=[0, 1])
        
        ttk.Label(search_frm, text="Filter:").grid(row=0, column=0, sticky="W", padx=(0, 6))
        
        search_entry = ttk.Entry(search_frm, textvariable=self.var_asset_search)
        search_entry.grid(row=0, column=1, sticky="EW")
        self.var_asset_search.trace_add('write', self._filter_assets)
        
        # Clear-Button
        ttk.Button(search_frm, text="✕", width=3, 
                  command=self._clear_search).grid(row=0, column=2, padx=(4, 0))
    
    def _build_asset_stats(self, parent):
        """Erstellt Asset-Statistiken"""
        # Entferne alte Statistiken falls vorhanden
        for widget in parent.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_name().startswith('!frame'):
                if len(widget.winfo_children()) > 0 and 'stats' in str(widget.winfo_children()[0]):
                    widget.destroy()
        
        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=3, column=0, sticky="EW", pady=(12, 0))
        
        if not self.asset_manager.has_local_asset_file():
            status_text = f"Keine Asset-Datei vorhanden | Pfad: {self.asset_manager.get_local_asset_file_path().name}"
            ttk.Label(stats_frame, text=status_text, font=('TkDefaultFont', 8), 
                     foreground="orange").pack(anchor="w")
        elif self.asset_manager.is_loaded():
            total_assets = self.asset_manager.get_asset_count()
            all_assets = self.asset_manager.get_all_assets()
            
            # Statistik-Text erstellen
            stats_text = f"Gesamt: {total_assets} Assets | "
            category_stats = []
            for category, assets in all_assets.items():
                if assets:  # Nur Kategorien mit Assets
                    category_stats.append(f"{category}: {len(assets)}")
            
            stats_text += " | ".join(category_stats)
            
            ttk.Label(stats_frame, text=stats_text, font=('TkDefaultFont', 8), 
                     foreground="gray").pack(anchor="w")
            
            # Pfad-Info
            path_text = f"Quelle: {self.asset_manager.get_local_asset_file_path().name}"
            ttk.Label(stats_frame, text=path_text, font=('TkDefaultFont', 7), 
                     foreground="gray").pack(anchor="w")
        else:
            ttk.Label(stats_frame, text="Asset-Datei konnte nicht geladen werden", 
                     foreground="red").pack(anchor="w")
    
    def _populate_asset_categories(self):
        """Befüllt die Kategorien-Liste"""
        self.lst_asset_categories.delete(0, END)
        
        if not self.asset_manager.has_local_asset_file():
            self.lst_asset_categories.insert(END, "Keine Asset-Datei vorhanden")
            self.lst_asset_categories.insert(END, "(Verwende 'Asset-DB importieren')")
            return
        
        if not self.asset_manager.is_loaded():
            self.asset_manager.load_assets()
        
        if not self.asset_manager.is_loaded():
            self.lst_asset_categories.insert(END, "Asset-Datei konnte nicht geladen werden")
            return
        
        all_assets = self.asset_manager.get_all_assets()
        for category in all_assets.keys():
            count = len(all_assets[category])
            self.lst_asset_categories.insert(END, f"{category} ({count})")
    
    def on_select_asset_category(self, event=None):
        """Handler für Kategorie-Auswahl"""
        sel = self.lst_asset_categories.curselection()
        if not sel:
            return
        
        if not self.asset_manager.has_local_asset_file():
            self.set_status("Keine Asset-Datei vorhanden. Verwenden Sie 'Asset-DB importieren'.")
            return
        
        if not self.asset_manager.is_loaded():
            self.asset_manager.load_assets()
        
        if not self.asset_manager.is_loaded():
            self.set_status("Asset-Datei konnte nicht geladen werden.")
            return
        
        idx = sel[0]
        categories = list(self.asset_manager.get_all_assets().keys())
        
        if idx < len(categories):
            self.current_asset_category = categories[idx]
            self._update_asset_list()
            self.set_status(f"Kategorie ausgewählt: {self.current_asset_category}")
    
    def _update_asset_list(self):
        """Aktualisiert die Asset-Liste"""
        if not hasattr(self, 'current_asset_category') or not self.current_asset_category:
            return
        
        self.lst_assets.delete(0, END)
        
        if not self.asset_manager.is_loaded():
            self.lst_assets.insert(END, "Asset-Datenbank nicht verfügbar")
            self.lbl_asset_info.config(text="Keine Assets verfügbar")
            return
        
        assets = self.asset_manager.get_assets(self.current_asset_category)
        search = self.var_asset_search.get().lower()
        
        # Filtern falls Suchtext vorhanden
        if search:
            filtered = [a for a in assets if search in a.lower()]
        else:
            filtered = assets[:]
        
        # Assets zur Liste hinzufügen
        for asset in sorted(filtered):
            self.lst_assets.insert(END, asset)
        
        # Info-Text aktualisieren
        if search:
            self.lbl_asset_info.config(
                text=f"{len(filtered)} von {len(assets)} Assets angezeigt (gefiltert nach: '{search}')")
        else:
            self.lbl_asset_info.config(text=f"{len(assets)} Assets angezeigt")
    
    def _filter_assets(self, *args):
        """Filtert Assets basierend auf Suchtext"""
        self._update_asset_list()
    
    def _clear_search(self):
        """Löscht den Suchtext"""
        self.var_asset_search.set("")
    
    def populate_data(self):
        """Lädt Daten in die UI-Komponenten (Tab-Interface)"""
        # Asset-Browser lädt seine Daten automatisch bei der Initialisierung
        pass
    
    def refresh_assets(self):
        """Aktualisiert die Asset-Anzeige (für externe Aufrufe)"""
        # Asset-Manager neu laden falls nötig
        if self.asset_manager.has_local_asset_file() and not self.asset_manager.is_loaded():
            self.asset_manager.load_assets()
        
        self._populate_asset_categories()
        if hasattr(self, 'current_asset_category') and self.current_asset_category:
            self._update_asset_list()
        
        # Statistiken aktualisieren
        right_frame = None
        for child in self.frame.winfo_children():
            if isinstance(child, ttk.Frame) and child.grid_info().get('column') == 1:
                right_frame = child
                break
        if right_frame:
            self._build_asset_stats(right_frame)
    
    def get_selected_asset(self):
        """Gibt das aktuell ausgewählte Asset zurück"""
        sel = self.lst_assets.curselection()
        if not sel:
            return None
        
        idx = sel[0]
        asset_text = self.lst_assets.get(idx)
        return asset_text
    
    def search_assets(self, search_term):
        """Sucht nach Assets mit dem gegebenen Begriff"""
        self.var_asset_search.set(search_term)
        # Filter wird automatisch durch trace_add ausgelöst
    
    def select_category(self, category_name):
        """Wählt eine Kategorie programmgesteuert aus"""
        if not self.asset_manager.has_local_asset_file():
            self.set_status("Keine Asset-Datei vorhanden.")
            return False
        
        if not self.asset_manager.is_loaded():
            self.asset_manager.load_assets()
        
        if not self.asset_manager.is_loaded():
            self.set_status("Asset-Datei konnte nicht geladen werden.")
            return False
        
        categories = list(self.asset_manager.get_all_assets().keys())
        
        try:
            idx = categories.index(category_name)
            self.lst_asset_categories.selection_clear(0, END)
            self.lst_asset_categories.selection_set(idx)
            self.on_select_asset_category()
            return True
        except ValueError:
            self.set_status(f"Kategorie nicht gefunden: {category_name}")
            return False
    
    def get_asset_categories(self):
        """Gibt alle verfügbaren Asset-Kategorien zurück"""
        if not self.asset_manager.has_local_asset_file():
            return []
        
        if not self.asset_manager.is_loaded():
            self.asset_manager.load_assets()
        
        if not self.asset_manager.is_loaded():
            return []
        
        return list(self.asset_manager.get_all_assets().keys())
    
    def get_assets_by_category(self, category):
        """Gibt alle Assets einer Kategorie zurück"""
        if not self.asset_manager.has_local_asset_file():
            return []
        
        if not self.asset_manager.is_loaded():
            self.asset_manager.load_assets()
        
        if not self.asset_manager.is_loaded():
            return []
        
        return self.asset_manager.get_assets(category)
    
    def _import_assets(self):
        """Importiert eine neue Asset-Datei"""
        if self.asset_manager.import_asset_file():
            self._populate_asset_categories()
            self._build_asset_stats(self.frame.nametowidget(self.frame.winfo_children()[1]))
            self.set_status("Asset-Datei erfolgreich importiert und geladen.")
    
    def _export_assets(self):
        """Exportiert die aktuelle Asset-Datei"""
        if self.asset_manager.export_asset_file():
            self.set_status("Asset-Datei erfolgreich exportiert.")
    
    def export_assets_to_clipboard(self):
        """Exportiert die aktuell angezeigten Assets in die Zwischenablage"""
        if not hasattr(self, 'current_asset_category') or not self.current_asset_category:
            self.set_status("Keine Kategorie ausgewählt.")
            return
        
        # Alle aktuell angezeigten Assets sammeln
        assets = []
        for i in range(self.lst_assets.size()):
            assets.append(self.lst_assets.get(i))
        
        if not assets:
            self.set_status("Keine Assets zum Exportieren.")
            return
        
        # Text für Zwischenablage vorbereiten
        export_text = f"# {self.current_asset_category} Assets ({len(assets)} items)\n"
        export_text += "\n".join(assets)
        
        try:
            # In Zwischenablage kopieren
            self.frame.clipboard_clear()
            self.frame.clipboard_append(export_text)
            self.set_status(f"{len(assets)} Assets in Zwischenablage kopiert.")
        except Exception as e:
            self.set_status(f"Fehler beim Kopieren: {e}")