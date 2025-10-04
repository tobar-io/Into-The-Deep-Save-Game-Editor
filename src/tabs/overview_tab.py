"""
Übersicht-Tab für grundlegende Savegame-Informationen
"""
from tkinter import ttk, StringVar, IntVar
from ..ui_components import add_label_entry, add_label_spin
from .base_tab import BaseTab


class OverviewTab(BaseTab):
    """Tab für Übersichtsinformationen des Savegames"""
    
    def __init__(self, parent, savegame_data, asset_manager, status_callback=None):
        # Tk Variables
        self.var_slot_name = StringVar()
        self.var_last_scene = StringVar()
        self.var_currency = IntVar()
        self.var_rescued = IntVar()
        self.var_banner_icon = StringVar()
        self.var_banner_bg = StringVar()
        
        super().__init__(parent, savegame_data, asset_manager, status_callback)
    
    def build_ui(self):
        """Baut die Benutzeroberfläche auf"""
        frm = ttk.Frame(self.frame, padding=10)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)
        
        row = 0
        
        # Save Slot Name
        add_label_entry(frm, "Save Slot Name", self.var_slot_name, row, 0)
        
        row += 1
        # Letzte Szene
        ttk.Label(frm, text="Letzte Szene (lastSceneID)").grid(row=row, column=0, sticky="E", padx=6, pady=4)
        if self.asset_manager.is_loaded() and self.asset_manager.get_assets("Levels"):
            cmb = ttk.Combobox(frm, textvariable=self.var_last_scene, 
                             values=self.asset_manager.get_assets("Levels"))
            cmb.grid(row=row, column=1, sticky="EW", padx=6, pady=4)
        else:
            add_label_entry(frm, "", self.var_last_scene, row, 0)
        
        row += 1
        # Geld
        add_label_spin(frm, "Geld (currency)", self.var_currency, row, 0, 0, 0, 99999999)
        
        row += 1
        # Gerettete Zwerge
        add_label_spin(frm, "Gerettete Zwerge", self.var_rescued, row, 0, 0, 0, 9999)
        
        row += 1
        # Banner Icon
        add_label_entry(frm, "Banner Icon", self.var_banner_icon, row, 0)
        
        row += 1
        # Banner Hintergrund
        add_label_entry(frm, "Banner Hintergrund", self.var_banner_bg, row, 0)
        
        row += 1
        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=row, column=0, columnspan=2, sticky="W", pady=(8, 0))
        ttk.Button(btns, text="Übernehmen", command=self.apply_changes).pack(side="left")
        ttk.Button(btns, text="Max Geld", command=self.action_max_money).pack(side="left", padx=(8, 0))
    
    def populate_data(self):
        """Lädt Daten in die UI-Komponenten"""
        data = self.savegame_data.data
        
        self.var_slot_name.set(data.get("saveSlotName", ""))
        self.var_last_scene.set(data.get("lastSceneID", ""))
        self.var_currency.set(int(data.get("currency", 0) or 0))
        self.var_rescued.set(int(data.get("rescuedDwarvesCount", 0) or 0))
        
        banner = data.get("bannerConfig", {}) or {}
        self.var_banner_icon.set(banner.get("bannerIconID", ""))
        self.var_banner_bg.set(banner.get("bannerBackgroundID", ""))
    
    def apply_changes(self):
        """Übernimmt die Änderungen in die Savegame-Daten"""
        data = self.savegame_data.data
        
        data["saveSlotName"] = self.var_slot_name.get()
        data["lastSceneID"] = self.var_last_scene.get()
        data["currency"] = int(self.var_currency.get())
        data["rescuedDwarvesCount"] = int(self.var_rescued.get())
        
        if "bannerConfig" not in data or not isinstance(data["bannerConfig"], dict):
            data["bannerConfig"] = {}
        
        data["bannerConfig"]["bannerIconID"] = self.var_banner_icon.get()
        data["bannerConfig"]["bannerBackgroundID"] = self.var_banner_bg.get()
        
        self.set_modified(True)
        self.set_status("Übersicht aktualisiert.")
    
    def action_max_money(self):
        """Setzt das Geld auf Maximum"""
        self.var_currency.set(999999)
        self.savegame_data.data["currency"] = 999999
        self.set_modified(True)
        self.set_status("Geld auf 999999 gesetzt.")