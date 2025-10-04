"""
Inventar-Tab für die Verwaltung von Items und Hüten
"""
from tkinter import ttk, StringVar, END
from ..ui_components import tk_listbox, setup_grid_weights, create_section_label
from ..savegame_data import ensure_list
from .base_tab import BaseTab


class InventoryTab(BaseTab):
    """Tab für Inventar-Verwaltung"""
    
    def __init__(self, parent, savegame_data, asset_manager, status_callback=None):
        # Variables für neue Items
        self.var_new_item_id = StringVar()
        self.var_new_hat_id = StringVar()
        
        super().__init__(parent, savegame_data, asset_manager, status_callback)
    
    def build_ui(self):
        """Baut die Benutzeroberfläche auf"""
        # Grid-Layout konfigurieren
        setup_grid_weights(self.frame, columns=[1, 1], rows=[0, 1, 0])
        
        # Header
        ttk.Label(self.frame, text="Items").grid(row=0, column=0, sticky="W", padx=8, pady=(8, 0))
        ttk.Label(self.frame, text="Hüte").grid(row=0, column=1, sticky="W", padx=8, pady=(8, 0))
        
        # Listen
        self.lst_items = tk_listbox(self.frame)
        self.lst_items.grid(row=1, column=0, sticky="NSEW", padx=8, pady=8)
        
        self.lst_hats = tk_listbox(self.frame)
        self.lst_hats.grid(row=1, column=1, sticky="NSEW", padx=8, pady=8)
        
        # Controls
        self._build_controls()
    
    def _build_controls(self):
        """Erstellt die Steuerelemente"""
        ctrl = ttk.Frame(self.frame, padding=8)
        ctrl.grid(row=2, column=0, columnspan=2, sticky="EW")
        setup_grid_weights(ctrl, columns=[1, 0, 1, 0], rows=[0, 0, 0])
        
        # Items (Equipment/Actions) - Zeile 0
        ttk.Label(ctrl, text="Item:").grid(row=0, column=0, sticky="E", padx=(0, 6))
        
        if self.asset_manager.is_loaded():
            item_assets = sorted(self.asset_manager.get_assets("Equipment"))
            cmb_items = ttk.Combobox(ctrl, textvariable=self.var_new_item_id, values=item_assets)
            cmb_items.grid(row=0, column=1, sticky="EW")
        else:
            e = ttk.Entry(ctrl, textvariable=self.var_new_item_id)
            e.grid(row=0, column=1, sticky="EW")
        
        ttk.Button(ctrl, text="Hinzufügen", command=self.add_inventory_item).grid(row=0, column=2, padx=6)
        
        # Hüte (Wearables) - Zeile 0 rechts
        ttk.Label(ctrl, text="Hut:").grid(row=0, column=3, sticky="E", padx=(12, 6))
        
        if self.asset_manager.is_loaded():
            cmb_hats = ttk.Combobox(ctrl, textvariable=self.var_new_hat_id, 
                                  values=self.asset_manager.get_assets("Wearables"))
            cmb_hats.grid(row=0, column=4, sticky="EW")
        else:
            e = ttk.Entry(ctrl, textvariable=self.var_new_hat_id)
            e.grid(row=0, column=4, sticky="EW")
        
        ttk.Button(ctrl, text="Hinzufügen", command=self.add_hat_item).grid(row=0, column=5, padx=6)
        
        # Entfernen-Buttons - Zeile 1
        ttk.Button(ctrl, text="Item entfernen", command=self.remove_selected_item).grid(
            row=1, column=0, columnspan=3, sticky="EW", padx=(0, 6), pady=(8, 0))
        ttk.Button(ctrl, text="Hut entfernen", command=self.remove_selected_hat).grid(
            row=1, column=3, columnspan=3, sticky="EW", padx=(6, 0), pady=(8, 0))
        
        # Bulk-Actions - Zeile 2
        bulk_frame = ttk.Frame(ctrl)
        bulk_frame.grid(row=2, column=0, columnspan=6, sticky="EW", pady=(12, 0))
        
        create_section_label(bulk_frame, "Bulk-Aktionen:", 0, 1, pady=(0, 6))
        
        btn_frame = ttk.Frame(bulk_frame)
        btn_frame.grid(row=1, column=0, sticky="W")
        
        ttk.Button(btn_frame, text="Alle Items hinzufügen", 
                  command=self.add_all_equipment).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Alle Hüte hinzufügen", 
                  command=self.add_all_wearables).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Alle Waffen hinzufügen", 
                  command=self.add_all_weapons).pack(side="left", padx=3)
    
    def populate_data(self):
        """Lädt Daten in die UI-Komponenten"""
        # Items-Liste befüllen
        self.lst_items.delete(0, END)
        for item in ensure_list(self.savegame_data.data.get("inventoryItemIDs")):
            self.lst_items.insert(END, item)
        
        # Hüte-Liste befüllen
        self.lst_hats.delete(0, END)
        for hat in ensure_list(self.savegame_data.data.get("inventoryHatIDs")):
            self.lst_hats.insert(END, hat)
    
    def add_inventory_item(self):
        """Fügt Item (Equipment) hinzu"""
        item_id = (self.var_new_item_id.get() or "").strip()
        if not item_id:
            return
        
        items = self.savegame_data.data.setdefault("inventoryItemIDs", [])
        if item_id not in items:  # Duplikate vermeiden
            items.append(item_id)
            self.populate_data()
            self.var_new_item_id.set("")
            self.set_modified(True)
            self.set_status(f"Item hinzugefügt: {item_id}")
        else:
            self.set_status(f"Item bereits vorhanden: {item_id}")
    
    def add_hat_item(self):
        """Fügt Hut (Wearable) hinzu"""
        item_id = (self.var_new_hat_id.get() or "").strip()
        if not item_id:
            return
        
        hats = self.savegame_data.data.setdefault("inventoryHatIDs", [])
        if item_id not in hats:  # Duplikate vermeiden
            hats.append(item_id)
            self.populate_data()
            self.var_new_hat_id.set("")
            self.set_modified(True)
            self.set_status(f"Hut hinzugefügt: {item_id}")
        else:
            self.set_status(f"Hut bereits vorhanden: {item_id}")
    
    def remove_selected_item(self):
        """Entfernt ausgewähltes Item"""
        sel = self.lst_items.curselection()
        if not sel:
            self.set_status("Kein Item ausgewählt.")
            return
        
        idx = sel[0]
        items = self.savegame_data.data.setdefault("inventoryItemIDs", [])
        if 0 <= idx < len(items):
            removed_item = items[idx]
            del items[idx]
            self.populate_data()
            self.set_modified(True)
            self.set_status(f"Item entfernt: {removed_item}")
    
    def remove_selected_hat(self):
        """Entfernt ausgewählten Hut"""
        sel = self.lst_hats.curselection()
        if not sel:
            self.set_status("Kein Hut ausgewählt.")
            return
        
        idx = sel[0]
        hats = self.savegame_data.data.setdefault("inventoryHatIDs", [])
        if 0 <= idx < len(hats):
            removed_hat = hats[idx]
            del hats[idx]
            self.populate_data()
            self.set_modified(True)
            self.set_status(f"Hut entfernt: {removed_hat}")
    
    def add_all_equipment(self):
        """Fügt alle Equipment-Items zum Inventar hinzu"""
        if not self.asset_manager.is_loaded() or not self.asset_manager.get_assets("Equipment"):
            self.set_status("Keine Equipment-Assets verfügbar.")
            return
        
        items = self.savegame_data.data.setdefault("inventoryItemIDs", [])
        added = 0
        
        for eq in self.asset_manager.get_assets("Equipment"):
            if eq not in items:
                items.append(eq)
                added += 1
        
        if added > 0:
            self.populate_data()
            self.set_modified(True)
            self.set_status(f"{added} Equipment-Items hinzugefügt.")
        else:
            self.set_status("Alle Equipment-Items bereits im Inventar.")
    
    def add_all_wearables(self):
        """Fügt alle Wearables (Hüte) zum Inventar hinzu"""
        if not self.asset_manager.is_loaded() or not self.asset_manager.get_assets("Wearables"):
            self.set_status("Keine Wearable-Assets verfügbar.")
            return
        
        hats = self.savegame_data.data.setdefault("inventoryHatIDs", [])
        added = 0
        
        for wearable in self.asset_manager.get_assets("Wearables"):
            if wearable not in hats:
                hats.append(wearable)
                added += 1
        
        if added > 0:
            self.populate_data()
            self.set_modified(True)
            self.set_status(f"{added} Hüte hinzugefügt.")
        else:
            self.set_status("Alle Hüte bereits im Inventar.")
    
    def add_all_weapons(self):
        """Fügt alle Waffen als Weapon States zum Inventar hinzu"""
        if not self.asset_manager.is_loaded() or not self.asset_manager.get_assets("Weapons"):
            self.set_status("Keine Waffen-Assets verfügbar.")
            return
        
        weapon_states = self.savegame_data.data.setdefault("inventoryWeaponStates", [])
        existing_ids = {ws.get("weaponSoTemplateID") for ws in weapon_states if isinstance(ws, dict)}
        
        added = 0
        for weapon_id in self.asset_manager.get_assets("Weapons"):
            if weapon_id not in existing_ids:
                from ..savegame_data import create_weapon_state
                weapon_state = create_weapon_state(weapon_id)
                weapon_states.append(weapon_state)
                added += 1
        
        if added > 0:
            self.set_modified(True)
            self.set_status(f"{added} Waffen hinzugefügt zum Waffen-Inventar.")
        else:
            self.set_status("Alle Waffen bereits im Inventar.")