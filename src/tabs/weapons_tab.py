"""
Waffen-Tab für die Verwaltung von Waffen im Inventar
"""
from tkinter import ttk, StringVar, IntVar, DoubleVar, BooleanVar, END
from ..ui_components import (tk_listbox, add_label_entry, add_label_spin, add_label_float, 
                           add_label_check, create_separator, create_section_label, setup_grid_weights)
from ..savegame_data import ensure_list, create_weapon_state
from .base_tab import BaseTab


class WeaponsTab(BaseTab):
    """Tab für Waffen-Verwaltung"""
    
    def __init__(self, parent, savegame_data, asset_manager, status_callback=None):
        # State
        self.selected_weapon_index = None
        
        # Variables für neue Waffe
        self.var_new_weapon_id = StringVar()
        
        # Waffen-Detail Variables
        self.var_weapon_inv_template_id = StringVar()
        self.var_weapon_inv_ammo = IntVar()
        self.var_weapon_inv_ammo_max = IntVar()
        self.var_weapon_inv_cooldown = IntVar()
        self.var_weapon_inv_reloading = BooleanVar()
        self.var_weapon_inv_equipped = BooleanVar()
        self.var_weapon_inv_drawn = BooleanVar()
        self.var_weapon_inv_blocked = BooleanVar()
        self.var_weapon_inv_dura = DoubleVar()
        self.var_weapon_inv_dura_max = DoubleVar()
        self.var_weapon_inv_dmg_mult = DoubleVar()
        self.var_weapon_inv_fire_mult = DoubleVar()
        self.var_weapon_inv_spread_mult = DoubleVar()
        self.var_weapon_inv_bullets_bonus = IntVar()
        self.var_weapon_inv_pen_bonus = IntVar()
        
        super().__init__(parent, savegame_data, asset_manager, status_callback)
    
    def build_ui(self):
        """Baut die Benutzeroberfläche auf"""
        setup_grid_weights(self.frame, columns=[1, 2], rows=[1])
        
        # Linke Seite - Waffen Liste
        left = ttk.Frame(self.frame, padding=8)
        left.grid(row=0, column=0, sticky="NSEW")
        
        ttk.Label(left, text="Waffen im Inventar").pack(anchor="w")
        self.lst_weapons = tk_listbox(left, height=20)
        self.lst_weapons.pack(fill="both", expand=True, pady=(6, 8))
        self.lst_weapons.bind("<<ListboxSelect>>", self.on_select_weapon)
        
        # Buttons für Waffen-Management
        self._build_weapon_controls(left)
        
        # Rechte Seite - Detail Form
        right = ttk.Frame(self.frame, padding=8)
        right.grid(row=0, column=1, sticky="NSEW")
        
        self._build_weapon_detail_form(right)
    
    def _build_weapon_controls(self, parent):
        """Erstellt die Waffen-Steuerelemente"""
        btns = ttk.Frame(parent)
        btns.pack(fill="x")
        
        # Waffe hinzufügen
        add_frame = ttk.Frame(btns)
        add_frame.pack(fill="x", pady=(0, 6))
        
        if self.asset_manager.is_loaded():
            cmb = ttk.Combobox(add_frame, textvariable=self.var_new_weapon_id, 
                             values=self.asset_manager.get_assets("Weapons"))
            cmb.pack(side="left", fill="x", expand=True, padx=(0, 6))
        else:
            ttk.Entry(add_frame, textvariable=self.var_new_weapon_id).pack(
                side="left", fill="x", expand=True, padx=(0, 6))
        
        ttk.Button(add_frame, text="Hinzufügen", command=self.add_weapon_to_inventory).pack(side="left")
        
        # Management-Buttons
        ttk.Button(btns, text="Entfernen", command=self.remove_selected_weapon).pack(
            side="left", padx=(0, 6))
        ttk.Button(btns, text="Alle hinzufügen", command=self.add_all_weapons).pack(side="left")
    
    def _build_weapon_detail_form(self, parent):
        """Erstellt das Waffen-Detail-Formular"""
        frm = ttk.Frame(parent)
        frm.pack(fill="both", expand=True)
        setup_grid_weights(frm, columns=[1, 1], rows=[])
        
        r = 0
        
        # Template ID (readonly)
        create_section_label(frm, "Waffen-ID (Template)", r, 4)
        r += 1
        
        ttk.Label(frm, text="weaponSoTemplateID:").grid(row=r, column=0, sticky="E", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.var_weapon_inv_template_id, state="readonly").grid(
            row=r, column=1, columnspan=3, sticky="EW", padx=6, pady=4)
        
        r += 1
        create_separator(frm, r, 4)
        
        r += 1
        create_section_label(frm, "Munition & Cooldown", r, 4)
        
        r += 1
        add_label_spin(frm, "currentAmmo", self.var_weapon_inv_ammo, r, 0, 0, 0, 99999)
        add_label_spin(frm, "maxAmmo", self.var_weapon_inv_ammo_max, r, 2, 0, 0, 99999)
        
        r += 1
        add_label_spin(frm, "currentCooldown (Runden)", self.var_weapon_inv_cooldown, r, 0, 0, 0, 100)
        add_label_check(frm, "isReloading", self.var_weapon_inv_reloading, r, 2)
        
        r += 1
        create_separator(frm, r, 4)
        
        r += 1
        create_section_label(frm, "Status-Flags", r, 4)
        
        r += 1
        add_label_check(frm, "isEquipped", self.var_weapon_inv_equipped, r, 0)
        add_label_check(frm, "isDrawn", self.var_weapon_inv_drawn, r, 1)
        add_label_check(frm, "isBlocked", self.var_weapon_inv_blocked, r, 2)
        
        r += 1
        create_separator(frm, r, 4)
        
        r += 1
        create_section_label(frm, "Haltbarkeit", r, 4)
        
        r += 1
        add_label_float(frm, "durability", self.var_weapon_inv_dura, r, 0, 0, 0, 100000)
        add_label_float(frm, "maxDurability", self.var_weapon_inv_dura_max, r, 2, 0, 0, 100000)
        
        r += 1
        create_separator(frm, r, 4)
        
        r += 1
        create_section_label(frm, "Multiplikatoren & Boni", r, 4)
        
        r += 1
        add_label_float(frm, "damageMultiplier", self.var_weapon_inv_dmg_mult, r, 0, 1.0, 0, 100)
        add_label_float(frm, "firingRateMultiplier", self.var_weapon_inv_fire_mult, r, 2, 1.0, 0, 100)
        
        r += 1
        add_label_float(frm, "spreadMultiplier", self.var_weapon_inv_spread_mult, r, 0, 1.0, 0, 100)
        add_label_spin(frm, "bulletsPerShotBonus", self.var_weapon_inv_bullets_bonus, r, 2, 0, 0, 100)
        
        r += 1
        add_label_spin(frm, "penetrationBonus", self.var_weapon_inv_pen_bonus, r, 0, 0, 0, 100)
        
        r += 1
        ttk.Button(frm, text="Änderungen übernehmen", command=self.apply_weapon_detail).grid(
            row=r, column=0, columnspan=4, sticky="W", pady=(12, 0))
    
    def populate_data(self):
        """Lädt Daten in die UI-Komponenten"""
        self.lst_weapons.delete(0, END)
        
        for i, wpn in enumerate(ensure_list(self.savegame_data.data.get("inventoryWeaponStates"))):
            if isinstance(wpn, dict):
                template_id = wpn.get("weaponSoTemplateID", "?")
                ammo = wpn.get("currentAmmo", 0)
                max_ammo = wpn.get("maxAmmo", 0)
                self.lst_weapons.insert(END, f"{i+1}. {template_id} ({ammo}/{max_ammo})")
    
    def on_select_weapon(self, event=None):
        """Handler für Waffen-Auswahl"""
        sel = self.lst_weapons.curselection()
        if not sel:
            self.selected_weapon_index = None
            return
        
        idx = sel[0]
        self.selected_weapon_index = idx
        weapons = ensure_list(self.savegame_data.data.get("inventoryWeaponStates"))
        
        if idx < len(weapons):
            wpn = weapons[idx]
            self._load_weapon_detail(wpn)
    
    def _load_weapon_detail(self, wpn):
        """Lädt Waffen-Details in die Formularfelder"""
        self.var_weapon_inv_template_id.set(wpn.get("weaponSoTemplateID", ""))
        self.var_weapon_inv_ammo.set(int(wpn.get("currentAmmo", 0) or 0))
        self.var_weapon_inv_ammo_max.set(int(wpn.get("maxAmmo", 0) or 0))
        self.var_weapon_inv_cooldown.set(int(wpn.get("currentCooldown", 0) or 0))
        self.var_weapon_inv_reloading.set(bool(wpn.get("isReloading", False)))
        self.var_weapon_inv_equipped.set(bool(wpn.get("isEquipped", False)))
        self.var_weapon_inv_drawn.set(bool(wpn.get("isDrawn", False)))
        self.var_weapon_inv_blocked.set(bool(wpn.get("isBlocked", False)))
        self.var_weapon_inv_dura.set(float(wpn.get("durability", 0.0) or 0.0))
        self.var_weapon_inv_dura_max.set(float(wpn.get("maxDurability", 0.0) or 0.0))
        self.var_weapon_inv_dmg_mult.set(float(wpn.get("damageMultiplier", 1.0) or 1.0))
        self.var_weapon_inv_fire_mult.set(float(wpn.get("firingRateMultiplier", 1.0) or 1.0))
        self.var_weapon_inv_spread_mult.set(float(wpn.get("spreadMultiplier", 1.0) or 1.0))
        self.var_weapon_inv_bullets_bonus.set(int(wpn.get("bulletsPerShotBonus", 0) or 0))
        self.var_weapon_inv_pen_bonus.set(int(wpn.get("penetrationBonus", 0) or 0))
    
    def apply_weapon_detail(self):
        """Übernimmt Waffen-Detail-Änderungen"""
        if self.selected_weapon_index is None:
            self.set_status("Keine Waffe ausgewählt.")
            return
        
        weapons = self.savegame_data.data.setdefault("inventoryWeaponStates", [])
        if self.selected_weapon_index >= len(weapons):
            self.set_status("Ungültiger Waffen-Index.")
            return
        
        wpn = weapons[self.selected_weapon_index]
        
        # Alle Werte übernehmen
        wpn["currentAmmo"] = int(self.var_weapon_inv_ammo.get())
        wpn["maxAmmo"] = int(self.var_weapon_inv_ammo_max.get())
        wpn["currentCooldown"] = int(self.var_weapon_inv_cooldown.get())
        wpn["isReloading"] = bool(self.var_weapon_inv_reloading.get())
        wpn["isEquipped"] = bool(self.var_weapon_inv_equipped.get())
        wpn["isDrawn"] = bool(self.var_weapon_inv_drawn.get())
        wpn["isBlocked"] = bool(self.var_weapon_inv_blocked.get())
        wpn["durability"] = float(self.var_weapon_inv_dura.get())
        wpn["maxDurability"] = float(self.var_weapon_inv_dura_max.get())
        wpn["damageMultiplier"] = float(self.var_weapon_inv_dmg_mult.get())
        wpn["firingRateMultiplier"] = float(self.var_weapon_inv_fire_mult.get())
        wpn["spreadMultiplier"] = float(self.var_weapon_inv_spread_mult.get())
        wpn["bulletsPerShotBonus"] = int(self.var_weapon_inv_bullets_bonus.get())
        wpn["penetrationBonus"] = int(self.var_weapon_inv_pen_bonus.get())
        
        self.set_modified(True)
        self.populate_data()
        self.lst_weapons.selection_set(self.selected_weapon_index)
        self.set_status("Waffen-Änderungen übernommen.")
    
    def add_weapon_to_inventory(self):
        """Fügt neue Waffe zum Inventar hinzu"""
        weapon_id = (self.var_new_weapon_id.get() or "").strip()
        if not weapon_id:
            self.set_status("Keine Waffen-ID eingegeben.")
            return
        
        weapons = self.savegame_data.data.setdefault("inventoryWeaponStates", [])
        
        # Prüfen ob Waffe bereits vorhanden
        existing_ids = {ws.get("weaponSoTemplateID") for ws in weapons if isinstance(ws, dict)}
        if weapon_id in existing_ids:
            self.set_status(f"Waffe bereits vorhanden: {weapon_id}")
            return
        
        # Neue Waffe erstellen
        weapon_state = create_weapon_state(weapon_id)
        weapons.append(weapon_state)
        
        self.populate_data()
        self.var_new_weapon_id.set("")
        self.set_modified(True)
        self.set_status(f"Waffe hinzugefügt: {weapon_id}")
    
    def remove_selected_weapon(self):
        """Entfernt ausgewählte Waffe"""
        if self.selected_weapon_index is None:
            self.set_status("Keine Waffe ausgewählt.")
            return
        
        weapons = self.savegame_data.data.setdefault("inventoryWeaponStates", [])
        if 0 <= self.selected_weapon_index < len(weapons):
            removed = weapons[self.selected_weapon_index].get("weaponSoTemplateID", "?")
            del weapons[self.selected_weapon_index]
            self.populate_data()
            self.set_modified(True)
            self.set_status(f"Waffe entfernt: {removed}")
            self.selected_weapon_index = None
    
    def add_all_weapons(self):
        """Fügt alle verfügbaren Waffen hinzu"""
        if not self.asset_manager.is_loaded() or not self.asset_manager.get_assets("Weapons"):
            self.set_status("Keine Waffen-Assets verfügbar.")
            return
        
        weapons = self.savegame_data.data.setdefault("inventoryWeaponStates", [])
        existing_ids = {ws.get("weaponSoTemplateID") for ws in weapons if isinstance(ws, dict)}
        
        added = 0
        for weapon_id in self.asset_manager.get_assets("Weapons"):
            if weapon_id not in existing_ids:
                weapon_state = create_weapon_state(weapon_id)
                weapons.append(weapon_state)
                added += 1
        
        if added > 0:
            self.populate_data()
            self.set_modified(True)
            self.set_status(f"{added} Waffen hinzugefügt.")
        else:
            self.set_status("Alle Waffen bereits im Inventar.")