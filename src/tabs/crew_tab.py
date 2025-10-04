"""
Crew-Tab für die Verwaltung von Crew-Mitgliedern
"""
from tkinter import ttk, StringVar, IntVar, DoubleVar, BooleanVar, END, messagebox
from ..ui_components import tk_listbox, add_label_entry, add_label_spin, add_label_float, add_label_check
from ..savegame_data import ensure_list, create_weapon_state
from .base_tab import BaseTab


class CrewTab(BaseTab):
    """Tab für die Crew-Verwaltung"""
    
    def __init__(self, parent, savegame_data, asset_manager, status_callback=None):
        # State
        self.selected_crew_index = None
        
        # Tk Variables
        self.var_crew_runtime_name = StringVar()
        self.var_crew_template_id = StringVar()
        self.var_crew_level = IntVar()
        self.var_crew_xp = IntVar()
        self.var_crew_hp = DoubleVar()
        self.var_crew_hp_max = DoubleVar()
        self.var_crew_ap = IntVar()
        self.var_crew_ap_max = IntVar()
        self.var_crew_move = IntVar()
        self.var_crew_dead = BooleanVar()
        self.var_crew_god = BooleanVar()
        self.var_crew_selected = BooleanVar()
        self.var_crew_stunned = BooleanVar()
        self.var_crew_weapon_id = StringVar()
        self.var_weapon_ammo = IntVar()
        self.var_weapon_ammo_max = IntVar()
        self.var_weapon_dura = DoubleVar()
        self.var_weapon_dura_max = DoubleVar()
        # Neue State-Variablen für Equipment
        self.selected_crew_index = None
        self.var_new_equip_item = StringVar()
        
        super().__init__(parent, savegame_data, asset_manager, status_callback)
    
    def build_ui(self):
        """Baut die Benutzeroberfläche auf"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=2)
        self.frame.rowconfigure(0, weight=1)
        
        # Linke Seite - Crew Liste
        left = ttk.Frame(self.frame, padding=8)
        left.grid(row=0, column=0, sticky="NSEW")
        
        ttk.Label(left, text="Crew Mitglieder").pack(anchor="w")
        self.lst_crew = tk_listbox(left, height=20)
        self.lst_crew.pack(fill="both", expand=True, pady=(6, 8))
        self.lst_crew.bind("<<ListboxSelect>>", self.on_select_crew)
        
        # Buttons
        btns = ttk.Frame(left)
        btns.pack(fill="x")
        ttk.Button(btns, text="Heilen", command=self.action_heal_selected).pack(side="left")
        ttk.Button(btns, text="AP voll", command=self.action_refill_ap_selected).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="Munition voll", command=self.action_refill_ammo_selected).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="Godmode um", command=self.action_toggle_god_selected).pack(side="left", padx=(6, 0))
        
        # Rechte Seite - Detail Form
        right = ttk.Frame(self.frame, padding=8)
        right.grid(row=0, column=1, sticky="NSEW")
        
        frm = ttk.Frame(right)
        frm.pack(fill="both", expand=True)
        for c in range(4):
            frm.columnconfigure(c, weight=1)
        
        r = 0
        add_label_entry(frm, "Name (runtimeName)", self.var_crew_runtime_name, r, 0, 2)
        add_label_entry(frm, "Template ID", self.var_crew_template_id, r, 2, 2, readonly=True)
        
        r += 1
        add_label_spin(frm, "Level", self.var_crew_level, r, 0, 0, 0, 200)
        add_label_spin(frm, "XP", self.var_crew_xp, r, 1, 0, 0, 1_000_000)
        add_label_spin(frm, "Bewegung", self.var_crew_move, r, 2, 0, 0, 999)
        add_label_spin(frm, "AP", self.var_crew_ap, r, 3, 0, 0, 99)
        
        r += 1
        add_label_spin(frm, "AP max", self.var_crew_ap_max, r, 0, 0, 0, 99)
        add_label_float(frm, "HP", self.var_crew_hp, r, 1, 0, 0, 9999)
        add_label_float(frm, "HP max", self.var_crew_hp_max, r, 2, 0, 0, 9999)
        
        r += 1
        add_label_check(frm, "Tot", self.var_crew_dead, r, 0)
        add_label_check(frm, "Godmode", self.var_crew_god, r, 1)
        add_label_check(frm, "Ausgewählt", self.var_crew_selected, r, 2)
        add_label_check(frm, "Betäubt", self.var_crew_stunned, r, 3)
        
        r += 1
        ttk.Label(frm, text="Waffe (ID)").grid(row=r, column=0, sticky="E", padx=6, pady=4)
        if self.asset_manager.is_loaded() and self.asset_manager.get_assets("Weapons"):
            cmb = ttk.Combobox(frm, textvariable=self.var_crew_weapon_id, 
                             values=self.asset_manager.get_assets("Weapons"))
            cmb.grid(row=r, column=1, sticky="EW", padx=6, pady=4, columnspan=2)
        else:
            e = ttk.Entry(frm, textvariable=self.var_crew_weapon_id)
            e.grid(row=r, column=1, sticky="EW", padx=6, pady=4, columnspan=2)
        
        r += 1
        add_label_spin(frm, "Ammo", self.var_weapon_ammo, r, 0, 0, 0, 99999)
        add_label_spin(frm, "Ammo max", self.var_weapon_ammo_max, r, 1, 0, 0, 99999)
        add_label_float(frm, "Haltbarkeit", self.var_weapon_dura, r, 2, 0, 0, 100000)
        add_label_float(frm, "Haltb. max", self.var_weapon_dura_max, r, 3, 0, 0, 100000)
        
        # Equipment-Sektion
        r += 1
        equip_frame = ttk.LabelFrame(frm, text="Equipment", padding=6)
        equip_frame.grid(row=r, column=0, columnspan=4, sticky="NSEW", pady=(12, 0))
        for c in range(4):
            equip_frame.columnconfigure(c, weight=1)
        
        # Liste der ausgerüsteten Items
        ttk.Label(equip_frame, text="Ausgerüstete Items").grid(row=0, column=0, sticky="W")
        self.lst_equipment = tk_listbox(equip_frame, height=6)
        self.lst_equipment.grid(row=1, column=0, columnspan=2, sticky="NSEW", pady=(4, 4))
        self.lst_equipment.bind("<<ListboxSelect>>", self.on_select_equipment)
        
        # Controls rechts
        ctrl_frame = ttk.Frame(equip_frame)
        ctrl_frame.grid(row=1, column=2, columnspan=2, sticky="NS")
        
        ttk.Button(ctrl_frame, text="Hinzufügen", command=self.action_add_equipment).pack(fill="x", pady=2)
        ttk.Button(ctrl_frame, text="Entfernen", command=self.action_remove_equipment).pack(fill="x", pady=2)
        ttk.Button(ctrl_frame, text="Alle aus Inventar", command=self.action_equip_all_from_inventory).pack(fill="x", pady=4)
        ttk.Button(ctrl_frame, text="Alle (Assets)", command=self.action_equip_all_assets).pack(fill="x", pady=2)
        ttk.Button(ctrl_frame, text="Leeren", command=self.action_clear_equipment).pack(fill="x", pady=(8,2))
        ttk.Button(ctrl_frame, text="Debug", command=self.action_debug_equipment).pack(fill="x", pady=(4,2))
        
        # Combobox / Entry für neues Equipment
        ttk.Label(equip_frame, text="Item hinzufügen:").grid(row=2, column=0, sticky="W", pady=(6,0))
        if self.asset_manager.is_loaded() and self.asset_manager.get_assets("Equipment"):
            cmb_eq = ttk.Combobox(equip_frame, textvariable=self.var_new_equip_item,
                                   values=sorted(self.asset_manager.get_assets("Equipment")))
            cmb_eq.grid(row=3, column=0, columnspan=2, sticky="EW", pady=(2,4))
        else:
            ttk.Entry(equip_frame, textvariable=self.var_new_equip_item).grid(row=3, column=0, columnspan=2, sticky="EW", pady=(2,4))
        
        ttk.Button(equip_frame, text="Zu Liste", command=self.action_add_equipment).grid(row=3, column=2, sticky="EW", padx=(6,0))
        
        # Apply Button
        r += 1
        ttk.Button(frm, text="Änderungen übernehmen", command=self.apply_crew_detail).grid(
            row=r, column=0, columnspan=4, sticky="W", pady=(8, 0))
    
    def populate_data(self):
        """Lädt Daten in die UI-Komponenten"""
        self.lst_crew.delete(0, END)
        for i, c in enumerate(ensure_list(self.savegame_data.data.get("crewStates"))):
            rn = c.get("runtimeName", "?")
            tid = c.get("templateID", "?")
            self.lst_crew.insert(END, f"{i+1}. {rn} ({tid})")
    
    def on_select_crew(self, event=None):
        """Handler für Crew-Auswahl"""
        sel = self.lst_crew.curselection()
        if not sel:
            self.selected_crew_index = None
            return
        
        idx = sel[0]
        self.selected_crew_index = idx
        crew_list = ensure_list(self.savegame_data.data.get("crewStates"))
        if idx < len(crew_list):
            crew = crew_list[idx]
            self._load_crew_detail(crew)
    
    def _load_crew_detail(self, crew):
        """Lädt Crew-Details in die Formularfelder"""
        self.var_crew_runtime_name.set(crew.get("runtimeName", ""))
        self.var_crew_template_id.set(crew.get("templateID", ""))
        self.var_crew_level.set(int(crew.get("currentLevel", 0) or 0))
        self.var_crew_xp.set(int(crew.get("currentXP", 0) or 0))
        self.var_crew_move.set(int(crew.get("movementRange", 0) or 0))
        self.var_crew_ap.set(int(crew.get("currentActionPoints", 0) or 0))
        self.var_crew_ap_max.set(int(crew.get("maxActionPoints", 0) or 0))
        self.var_crew_hp.set(float(crew.get("currentHP", 0.0) or 0.0))
        self.var_crew_hp_max.set(float(crew.get("maxHP", 0.0) or 0.0))
        self.var_crew_dead.set(bool(crew.get("isDead", False)))
        self.var_crew_god.set(bool(crew.get("godMode", False)))
        self.var_crew_selected.set(bool(crew.get("isSelected", False)))
        self.var_crew_stunned.set(bool(crew.get("isStunned", False)))
        self.var_crew_weapon_id.set(crew.get("equippedWeaponID", ""))
        
        wpn = crew.get("equippedWeaponState", {}) or {}
        self.var_weapon_ammo.set(int(wpn.get("currentAmmo", 0) or 0))
        self.var_weapon_ammo_max.set(int(wpn.get("maxAmmo", 0) or 0))
        self.var_weapon_dura.set(float(wpn.get("durability", 0.0) or 0.0))
        self.var_weapon_dura_max.set(float(wpn.get("maxDurability", 0.0) or 0.0))
        # Merke ursprüngliche Waffen-ID für Wechsel-Erkennung
        self._original_weapon_id = crew.get("equippedWeaponID", "")
        
        # Equipment laden (robuste Erkennung verschiedener möglicher Felder)
        equip_list, field_name = self._extract_equipment_from_crew(crew)
        self._equipment_field_name = field_name  # merken für späteres Speichern
        if hasattr(self, 'lst_equipment'):
            self.lst_equipment.delete(0, END)
            for it in equip_list:
                self.lst_equipment.insert(END, it)
        self._current_equipment_cache = equip_list[:]  # lokale Kopie
        # Hinweis falls nichts gefunden aber potentielle Felder existieren
        if not equip_list:
            possible_keys = [k for k in crew.keys() if 'equip' in k.lower()]
            if possible_keys:
                self.set_status(f"Hinweis: Keine Items erkannt (Felder: {', '.join(possible_keys)})")

    def action_debug_equipment(self):
        """Zeigt eine diagnostische Analyse der Ausrüstung für das ausgewählte Crew-Mitglied."""
        if self.selected_crew_index is None:
            messagebox.showinfo("Equipment-Debug", "Kein Crew-Mitglied ausgewählt.")
            return
        crew_list = ensure_list(self.savegame_data.data.get("crewStates"))
        if self.selected_crew_index >= len(crew_list):
            return
        crew = crew_list[self.selected_crew_index]
        eq_list, field = self._extract_equipment_from_crew(crew)
        keys_with_equip = [k for k in crew.keys() if 'equip' in k.lower()]
        msg = [
            f"Gefundenes Feld: {field or '-'}",
            f"Anzahl erkannter Items: {len(eq_list)}",
            *(f" • {it}" for it in eq_list[:50]),
            "",
            f"Alle crew-Felder mit 'equip': {', '.join(keys_with_equip) or '-'}"
        ]
        if not eq_list:
            msg.append("Hinweis: Falls die Ausrüstung tiefer verschachtelt ist, bitte Beispiel-Crew-JSON schicken.")
        messagebox.showinfo("Equipment-Debug", "\n".join(msg))

    def apply_crew_detail(self):
        """Übernimmt Crew-Detail-Änderungen"""
        if self.selected_crew_index is None:
            return
        
        crew_list = ensure_list(self.savegame_data.data.get("crewStates"))
        if self.selected_crew_index >= len(crew_list):
            return
        
        crew = crew_list[self.selected_crew_index]
        crew["runtimeName"] = self.var_crew_runtime_name.get()
        crew["currentLevel"] = int(self.var_crew_level.get())
        crew["currentXP"] = int(self.var_crew_xp.get())
        crew["movementRange"] = int(self.var_crew_move.get())
        crew["currentActionPoints"] = int(self.var_crew_ap.get())
        crew["maxActionPoints"] = int(self.var_crew_ap_max.get())
        crew["currentHP"] = float(self.var_crew_hp.get())
        crew["maxHP"] = float(self.var_crew_hp_max.get())
        crew["isDead"] = bool(self.var_crew_dead.get())
        crew["godMode"] = bool(self.var_crew_god.get())
        crew["isSelected"] = bool(self.var_crew_selected.get())
        crew["isStunned"] = bool(self.var_crew_stunned.get())
        new_weapon_id = (self.var_crew_weapon_id.get() or "").strip()
        old_weapon_id = getattr(self, '_original_weapon_id', None)
        inventory_weapons = self.savegame_data.data.setdefault("inventoryWeaponStates", [])
        inventory_index_by_id = {ws.get("weaponSoTemplateID"): i for i, ws in enumerate(inventory_weapons) if isinstance(ws, dict)}

        # Falls Waffe gewechselt wurde: alte Waffe in Inventar verschieben
        if old_weapon_id and new_weapon_id and old_weapon_id != new_weapon_id:
            old_state = crew.get("equippedWeaponState") if isinstance(crew.get("equippedWeaponState"), dict) else None
            if old_state and old_state.get("weaponSoTemplateID") == old_weapon_id:
                if old_weapon_id not in inventory_index_by_id:
                    # ursprünglichen equippedWeaponState klonen (oder direkt nutzen) und ins Inventar legen
                    inventory_weapons.append(old_state)
                # Referenz im Crew-Objekt wird nachher durch neue ersetzt
            # Statushinweis vorbereiten
            weapon_switch_msg = f"Waffe gewechselt: {old_weapon_id} -> {new_weapon_id} (alte ins Inventar)"
        else:
            weapon_switch_msg = None

        # Neue Waffe aus Inventar holen oder erstellen
        if new_weapon_id:
            if new_weapon_id in inventory_index_by_id:
                # WeaponState aus Inventar entnehmen
                idx = inventory_index_by_id[new_weapon_id]
                new_state = inventory_weapons.pop(idx)
            else:
                # Neu erstellen (damit keine Re-Initialisierung im Spiel notwendig wäre – placeholder Werte)
                new_state = create_weapon_state(new_weapon_id)
        else:
            new_state = crew.get("equippedWeaponState") if isinstance(crew.get("equippedWeaponState"), dict) else create_weapon_state("")

        # State mit GUI-Werten überschreiben (User-Eingaben haben Vorrang)
        try:
            new_state["weaponSoTemplateID"] = new_weapon_id
            new_state["currentAmmo"] = int(self.var_weapon_ammo.get())
            new_state["maxAmmo"] = int(self.var_weapon_ammo_max.get())
            new_state["durability"] = float(self.var_weapon_dura.get())
            new_state["maxDurability"] = float(self.var_weapon_dura_max.get())
        except Exception:
            pass

        crew["equippedWeaponID"] = new_weapon_id
        crew["equippedWeaponState"] = new_state
        # Update Original-ID Tracker
        self._original_weapon_id = new_weapon_id
        
        # Equipment übernehmen
        if hasattr(self, 'lst_equipment'):
            eq_items = [self.lst_equipment.get(i) for i in range(self.lst_equipment.size())]
            # In dasselbe Feld zurückschreiben das wir beim Laden gefunden haben
            target_field = getattr(self, '_equipment_field_name', None)
            if not target_field:  # Fallback / neues Feld
                # Falls das Save ursprünglich ein Feld mit 'equip' enthält, dieses nehmen
                for candidate in [
                    'equippedItemIDs','equippedItems','equipmentItemIDs','equipmentIDs',
                    'equippedEquipmentIDs','equippedItemsIDs']:
                    if candidate in crew:
                        target_field = candidate
                        break
            if not target_field:
                target_field = 'equippedItemIDs'
            crew[target_field] = eq_items
        
        self.set_modified(True)
        if weapon_switch_msg:
            self.set_status(weapon_switch_msg)
            # Versuche Waffen-Tab zu aktualisieren (falls vorhanden)
            try:
                # Master-Hierarchie hochlaufen bis zur App
                parent = self.frame.master
                app = None
                depth = 0
                while parent is not None and depth < 6:
                    if hasattr(parent, 'tab_instances') and 'weapons' in getattr(parent, 'tab_instances'):
                        app = parent
                        break
                    parent = getattr(parent, 'master', None)
                    depth += 1
                if app:
                    weapons_tab = app.tab_instances.get('weapons')
                    if weapons_tab:
                        weapons_tab.populate_data()
                # Optional: Crew-List aktualisieren damit Auswahl bestehen bleibt
                self.populate_data()
            except Exception:
                pass
        else:
            self.set_status("Crew-Änderungen übernommen.")

    # --------------------------------------------------
    # Equipment Hilfsmethoden
    # --------------------------------------------------
    def _extract_equipment_from_crew(self, crew):
        """Versucht eine Liste von ausgerüsteten Item-IDs und den Feldnamen zu extrahieren.
        Unterstützt verschiedene mögliche Daten-Layouts:
        - Liste von Strings unter diversen Feldnamen
        - Liste von Dictionaries mit ID-Schlüsseln (itemID, equipmentID, templateID, soTemplateID, id)
        - States-Listen (z.B. equipmentStates) mit ähnlicher Struktur
        Rückgabe: (list[str], feldname|None)
        """
        candidate_fields = [
            'equippedItemIDs','equippedItems','equippedItemsIDs','equipmentItemIDs',
            'equipmentIDs','equippedEquipmentIDs','equipmentItems','equipmentStates'
        ]
        id_keys = ['itemID','equipmentID','templateID','soTemplateID','id','runtimeID']
        for field in candidate_fields:
            if field not in crew:
                continue
            raw = crew.get(field)
            if isinstance(raw, list):
                # Liste von Strings
                if all(isinstance(x, str) for x in raw):
                    return raw, field
                # Liste von Dicts
                extracted = []
                for entry in raw:
                    if isinstance(entry, dict):
                        # Direkt als ID wenn einzelnes String-Feld
                        for k in id_keys:
                            if k in entry and isinstance(entry[k], (str,int)):
                                extracted.append(str(entry[k]))
                                break
                if extracted:
                    return extracted, field
        # Nichts gefunden
        return [], None
    
    # Action Methods
    def action_heal_selected(self):
        """Heilt das ausgewählte Crew-Mitglied"""
        if self.selected_crew_index is None:
            return
        
        crew_list = ensure_list(self.savegame_data.data.get("crewStates"))
        if self.selected_crew_index >= len(crew_list):
            return
        
        c = crew_list[self.selected_crew_index]
        c["currentHP"] = float(c.get("maxHP", c.get("currentHP", 0.0)))
        c["isDead"] = False
        self._load_crew_detail(c)
        self.set_modified(True)
        self.set_status("Ausgewähltes Crew-Mitglied geheilt.")
    
    def action_refill_ap_selected(self):
        """Füllt AP des ausgewählten Crew-Mitglieds auf"""
        if self.selected_crew_index is None:
            return
        
        crew_list = ensure_list(self.savegame_data.data.get("crewStates"))
        if self.selected_crew_index >= len(crew_list):
            return
        
        c = crew_list[self.selected_crew_index]
        c["currentActionPoints"] = int(c.get("maxActionPoints", c.get("currentActionPoints", 0)))
        self._load_crew_detail(c)
        self.set_modified(True)
        self.set_status("AP aufgefüllt (ausgewählt).")
    
    def action_refill_ammo_selected(self):
        """Füllt Munition des ausgewählten Crew-Mitglieds auf"""
        if self.selected_crew_index is None:
            return
        
        crew_list = ensure_list(self.savegame_data.data.get("crewStates"))
        if self.selected_crew_index >= len(crew_list):
            return
        
        c = crew_list[self.selected_crew_index]
        w = c.get("equippedWeaponState", {}) or {}
        w["currentAmmo"] = int(w.get("maxAmmo", w.get("currentAmmo", 0)))
        w["durability"] = float(w.get("maxDurability", w.get("durability", 0.0)))
        c["equippedWeaponState"] = w
        self._load_crew_detail(c)
        self.set_modified(True)
        self.set_status("Munition/Haltbarkeit aufgefüllt (ausgewählt).")
    
    def action_toggle_god_selected(self):
        """Schaltet Godmode für das ausgewählte Crew-Mitglied um"""
        if self.selected_crew_index is None:
            return
        
        crew_list = ensure_list(self.savegame_data.data.get("crewStates"))
        if self.selected_crew_index >= len(crew_list):
            return
        
        c = crew_list[self.selected_crew_index]
        c["godMode"] = not bool(c.get("godMode", False))
        self._load_crew_detail(c)
        self.set_modified(True)
        self.set_status("Godmode umgeschaltet (ausgewählt).")
    
    # Equipment Listbox Handler
    def on_select_equipment(self, event=None):
        """Optionaler Handler bei Auswahl eines Equipment-Eintrags (derzeit nur Statusmeldung)."""
        if not hasattr(self, 'lst_equipment'):
            return
        sel = self.lst_equipment.curselection()
        if not sel:
            return
        try:
            item = self.lst_equipment.get(sel[0])
            if item:
                self.set_status(f"Equipment ausgewählt: {item}")
        except Exception:
            pass

    # Equipment Actions
    def action_add_equipment(self):
        if self.selected_crew_index is None:
            return
        item_id = (getattr(self, 'var_new_equip_item', StringVar()).get() or '').strip()
        if not item_id:
            return
        # Prüfen ob Item existiert (optional)
        if self.asset_manager.is_loaded() and self.asset_manager.get_assets("Equipment"):
            if item_id not in self.asset_manager.get_assets("Equipment"):
                self.set_status(f"Unbekanntes Equipment: {item_id}")
                return
        # Nicht doppelt
        existing = [self.lst_equipment.get(i) for i in range(self.lst_equipment.size())]
        if item_id in existing:
            self.set_status("Bereits ausgerüstet.")
            return
        self.lst_equipment.insert(END, item_id)
        if hasattr(self, 'var_new_equip_item'):
            self.var_new_equip_item.set("")
        self.set_modified(True)
        self.set_status(f"Equipment hinzugefügt: {item_id}")

    def action_remove_equipment(self):
        if self.selected_crew_index is None:
            return
        sel = self.lst_equipment.curselection()
        if not sel:
            return
        idx = sel[0]
        removed = self.lst_equipment.get(idx)
        self.lst_equipment.delete(idx)
        self.set_modified(True)
        self.set_status(f"Equipment entfernt: {removed}")

    def action_clear_equipment(self):
        if self.selected_crew_index is None:
            return
        self.lst_equipment.delete(0, END)
        self.set_modified(True)
        self.set_status("Equipment geleert.")

    def action_equip_all_from_inventory(self):
        if self.selected_crew_index is None:
            return
        inv = self.savegame_data.data.get("inventoryItemIDs") or []
        existing = {self.lst_equipment.get(i) for i in range(self.lst_equipment.size())}
        added = 0
        for it in inv:
            if it not in existing:
                self.lst_equipment.insert(END, it)
                added += 1
        if added:
            self.set_modified(True)
        self.set_status(f"{added} Items aus Inventar ausgerüstet." if added else "Keine neuen Items.")

    def action_equip_all_assets(self):
        if self.selected_crew_index is None:
            return
        if not self.asset_manager.is_loaded() or not self.asset_manager.get_assets("Equipment"):
            self.set_status("Keine Equipment-Assets geladen.")
            return
        existing = {self.lst_equipment.get(i) for i in range(self.lst_equipment.size())}
        added = 0
        for it in self.asset_manager.get_assets("Equipment"):
            if it not in existing:
                self.lst_equipment.insert(END, it)
                added += 1
        if added:
            self.set_modified(True)
        self.set_status(f"{added} Items aus allen Assets ausgerüstet." if added else "Alle bereits vorhanden.")