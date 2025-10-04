"""
Level-Tab für die Verwaltung von Levels und Performance-Daten
"""
from tkinter import ttk, StringVar, IntVar, END
from ..ui_components import (tk_listbox, add_label_spin, setup_grid_weights, 
                           create_section_label, create_separator)
from ..savegame_data import ensure_list
from ..config import LEVEL_STATUS_ENUM
from .base_tab import BaseTab


class LevelsTab(BaseTab):
    """Tab für Level-Verwaltung"""
    
    def __init__(self, parent, savegame_data, asset_manager, status_callback=None):
        # State
        self.selected_level_index = None
        
        # Variables
        self.var_level_star = IntVar()
        self.var_level_status = StringVar()
        
        super().__init__(parent, savegame_data, asset_manager, status_callback)
    
    def build_ui(self):
        """Baut die Benutzeroberfläche auf"""
        setup_grid_weights(self.frame, columns=[1, 2], rows=[0, 1])
        
        # Header
        ttk.Label(self.frame, text="Level (aus levelStates)").grid(
            row=0, column=0, sticky="W", padx=8, pady=(8, 0))
        ttk.Label(self.frame, text="Level-Details & Performance").grid(
            row=0, column=1, sticky="W", padx=8, pady=(8, 0))
        
        # Linke Seite - Level Liste
        left = ttk.Frame(self.frame, padding=8)
        left.grid(row=1, column=0, sticky="NSEW")
        
        self.lst_levels = tk_listbox(left, height=25)
        self.lst_levels.pack(fill="both", expand=True, pady=(0, 8))
        self.lst_levels.bind("<<ListboxSelect>>", self.on_select_level)
        
        # Level-Actions
        self._build_level_actions(left)
        
        # Rechte Seite - Detail Notebook
        right = ttk.Frame(self.frame, padding=8)
        right.grid(row=1, column=1, sticky="NSEW")
        setup_grid_weights(right, columns=[1], rows=[1])
        
        self.level_notebook = ttk.Notebook(right)
        self.level_notebook.grid(row=0, column=0, sticky="NSEW")
        
        # Tabs erstellen
        self._build_level_tabs()
    
    def _build_level_actions(self, parent):
        """Erstellt Level-Action-Buttons"""
        actions = ttk.Frame(parent)
        actions.pack(fill="x")
        
        ttk.Button(actions, text="Freischalten", 
                  command=self.action_unlock_selected_level).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Abschließen", 
                  command=self.action_complete_selected_level).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="3 Sterne", 
                  command=self.action_max_stars_selected).pack(side="left")
    
    def _build_level_tabs(self):
        """Erstellt die Level-Detail-Tabs"""
        # Tab 1: Basic Info
        basic_tab = ttk.Frame(self.level_notebook)
        self.level_notebook.add(basic_tab, text="Info")
        self._build_level_basic_tab(basic_tab)
        
        # Tab 2: Performance Stats
        perf_tab = ttk.Frame(self.level_notebook)
        self.level_notebook.add(perf_tab, text="Performance")
        self._build_level_performance_tab(perf_tab)
        
        # Tab 3: Mission Results
        results_tab = ttk.Frame(self.level_notebook)
        self.level_notebook.add(results_tab, text="Mission Results")
        self._build_level_results_tab(results_tab)
    
    def _build_level_basic_tab(self, parent):
        """Erstellt den Basic-Info-Tab"""
        frm = ttk.Frame(parent, padding=8)
        frm.pack(fill="both", expand=True)
        setup_grid_weights(frm, columns=[1])
        
        r = 0
        
        # Level ID (readonly)
        ttk.Label(frm, text="Level ID:").grid(row=r, column=0, sticky="E", padx=6, pady=4)
        self.lbl_level_id = ttk.Label(frm, text="-", font=('TkDefaultFont', 9, 'bold'))
        self.lbl_level_id.grid(row=r, column=1, sticky="W", padx=6, pady=4)
        
        r += 1
        # Sterne
        add_label_spin(frm, "Sterne (0-3):", self.var_level_star, r, 0, 0, 0, 3)
        
        r += 1
        # Status
        ttk.Label(frm, text="Status:").grid(row=r, column=0, sticky="E", padx=6, pady=4)
        status_values = [f"{k}: {v}" for k, v in LEVEL_STATUS_ENUM.items()]
        self.cmb_level_status = ttk.Combobox(frm, textvariable=self.var_level_status, 
                                           values=status_values, state="readonly", width=20)
        self.cmb_level_status.grid(row=r, column=1, sticky="W", padx=6, pady=4)
        
        r += 1
        # Apply Button
        ttk.Button(frm, text="Änderungen übernehmen", 
                  command=self.apply_level_detail).grid(row=r, column=1, sticky="W", padx=6, pady=(12, 0))
        
        r += 1
        create_separator(frm, r, 2, pady=12)
        
        r += 1
        create_section_label(frm, "Quick Actions:", r, 2, pady=(0, 8))
        
        r += 1
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=r, column=0, columnspan=2, sticky="W", padx=6)
        
        ttk.Button(btn_frame, text="Freischalten", 
                  command=self.action_unlock_selected_level).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Als abgeschlossen", 
                  command=self.action_complete_selected_level).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="3 Sterne setzen", 
                  command=self.action_max_stars_selected).pack(side="left")
    
    def _build_level_performance_tab(self, parent):
        """Erstellt den Performance-Tab"""
        frm = ttk.Frame(parent, padding=8)
        frm.pack(fill="both", expand=True)
        setup_grid_weights(frm, columns=[1])
        
        # Performance-Labels erstellen
        self.lbl_perf_plays = ttk.Label(frm, text="-")
        self.lbl_perf_best_time = ttk.Label(frm, text="-")
        self.lbl_perf_avg_time = ttk.Label(frm, text="-")
        self.lbl_perf_enemies = ttk.Label(frm, text="-")
        self.lbl_perf_damage_dealt = ttk.Label(frm, text="-")
        self.lbl_perf_damage_taken = ttk.Label(frm, text="-")
        self.lbl_perf_items = ttk.Label(frm, text="-")
        self.lbl_perf_perfect = ttk.Label(frm, text="-")
        self.lbl_perf_noloss = ttk.Label(frm, text="-")
        self.lbl_perf_speed = ttk.Label(frm, text="-")
        
        r = 0
        create_section_label(frm, "Performance-Statistiken", r, 2, pady=(0, 12))
        
        r += 1
        ttk.Label(frm, text="Gespielt:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_plays.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        ttk.Label(frm, text="Beste Zeit:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_best_time.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        ttk.Label(frm, text="Durchschn. Zeit:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_avg_time.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        create_separator(frm, r, 2, pady=8)
        
        r += 1
        ttk.Label(frm, text="Gesamt besiegt:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_enemies.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        ttk.Label(frm, text="Schaden ausgeteilt:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_damage_dealt.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        ttk.Label(frm, text="Schaden erhalten:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_damage_taken.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        ttk.Label(frm, text="Items gefunden:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_items.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        create_separator(frm, r, 2, pady=8)
        
        r += 1
        ttk.Label(frm, text="Perfect Runs (3★):").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_perfect.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        ttk.Label(frm, text="No-Loss Runs:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_noloss.grid(row=r, column=1, sticky="W", padx=6, pady=3)
        
        r += 1
        ttk.Label(frm, text="Speed Runs:").grid(row=r, column=0, sticky="E", padx=6, pady=3)
        self.lbl_perf_speed.grid(row=r, column=1, sticky="W", padx=6, pady=3)
    
    def _build_level_results_tab(self, parent):
        """Erstellt den Mission Results Tab"""
        frm = ttk.Frame(parent, padding=8)
        frm.pack(fill="both", expand=True)
        setup_grid_weights(frm, columns=[1, 0], rows=[0, 1])
        
        create_section_label(frm, "Mission Results (Chronologisch)", 0, 2, pady=(0, 8))
        
        # Treeview für Mission Results
        cols = ("date", "stars", "time", "enemies", "survival")
        self.tree_mission_results = ttk.Treeview(frm, columns=cols, show="headings", height=15)
        
        # Headers
        self.tree_mission_results.heading("date", text="Datum")
        self.tree_mission_results.heading("stars", text="★")
        self.tree_mission_results.heading("time", text="Zeit")
        self.tree_mission_results.heading("enemies", text="Enemies")
        self.tree_mission_results.heading("survival", text="Squad")
        
        # Spaltenbreiten
        self.tree_mission_results.column("date", width=120)
        self.tree_mission_results.column("stars", width=40)
        self.tree_mission_results.column("time", width=70)
        self.tree_mission_results.column("enemies", width=70)
        self.tree_mission_results.column("survival", width=70)
        
        self.tree_mission_results.grid(row=1, column=0, sticky="NSEW")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frm, orient="vertical", command=self.tree_mission_results.yview)
        scrollbar.grid(row=1, column=1, sticky="NS")
        self.tree_mission_results.configure(yscrollcommand=scrollbar.set)
    
    def populate_data(self):
        """Lädt Daten in die UI-Komponenten"""
        self.lst_levels.delete(0, END)
        
        for i, lv in enumerate(ensure_list(self.savegame_data.data.get("levelStates"))):
            lid = lv.get("levelID", f"level_{i}")
            sr = lv.get("starRating", 0)
            st = lv.get("levelStatus", 0)
            status_name = LEVEL_STATUS_ENUM.get(st, f"Unknown({st})")
            stars = "⭐" * sr if sr > 0 else "☆☆☆"
            self.lst_levels.insert(END, f"{i+1}. {lid} [{stars}] {status_name}")
    
    def on_select_level(self, event=None):
        """Handler für Level-Auswahl"""
        sel = self.lst_levels.curselection()
        if not sel:
            self.selected_level_index = None
            self._clear_level_details()
            return
        
        idx = sel[0]
        self.selected_level_index = idx
        levels = ensure_list(self.savegame_data.data.get("levelStates"))
        
        if idx < len(levels):
            lv = levels[idx]
            self._load_level_details(lv)
    
    def _load_level_details(self, lv):
        """Lädt Level-Details in die UI"""
        # Basic Info
        lid = lv.get("levelID", "?")
        self.lbl_level_id.config(text=lid)
        self.var_level_star.set(int(lv.get("starRating", 0) or 0))
        
        st = int(lv.get("levelStatus", 0) or 0)
        status_str = f"{st}: {LEVEL_STATUS_ENUM.get(st, 'Unknown')}"
        self.var_level_status.set(status_str)
        
        # Performance Data
        self._load_performance_data(lv)
        
        # Mission Results
        self._load_mission_results(lv)
    
    def _load_performance_data(self, lv):
        """Lädt Performance-Daten"""
        perf = lv.get("performanceData", {}) or {}
        
        play_count = perf.get("totalPlayCount", 0)
        self.lbl_perf_plays.config(text=str(play_count))
        
        best_time = perf.get("bestCompletionTime", float('inf'))
        if best_time < float('inf'):
            self.lbl_perf_best_time.config(text=f"{best_time:.1f}s")
        else:
            self.lbl_perf_best_time.config(text="-")
        
        if play_count > 0:
            total_time = perf.get("totalCompletionTime", 0)
            avg_time = total_time / play_count
            self.lbl_perf_avg_time.config(text=f"{avg_time:.1f}s")
        else:
            self.lbl_perf_avg_time.config(text="-")
        
        self.lbl_perf_enemies.config(text=str(perf.get("totalEnemiesDefeated", 0)))
        self.lbl_perf_damage_dealt.config(text=str(perf.get("totalDamageDealt", 0)))
        self.lbl_perf_damage_taken.config(text=str(perf.get("totalDamageTaken", 0)))
        self.lbl_perf_items.config(text=str(perf.get("totalItemsFound", 0)))
        self.lbl_perf_perfect.config(text=str(perf.get("perfectRuns", 0)))
        self.lbl_perf_noloss.config(text=str(perf.get("noLossRuns", 0)))
        self.lbl_perf_speed.config(text=str(perf.get("speedRuns", 0)))
    
    def _load_mission_results(self, lv):
        """Lädt Mission Results"""
        self.tree_mission_results.delete(*self.tree_mission_results.get_children())
        
        results = ensure_list(lv.get("missionResults"))
        for res in results:
            date_str = res.get("completionDate", "?")
            stars = "⭐" * res.get("starRating", 0)
            time_val = res.get("completionTime", 0)
            enemies = res.get("enemiesDefeated", 0)
            survival = f"{res.get('squadSurvivalRate', 0)*100:.0f}%"
            
            self.tree_mission_results.insert("", END, values=(
                date_str, stars, f"{time_val:.1f}s", enemies, survival
            ))
    
    def _clear_level_details(self):
        """Löscht Level-Details"""
        self.lbl_level_id.config(text="-")
        self.var_level_star.set(0)
        self.var_level_status.set("0: Hidden")
        
        # Performance zurücksetzen
        for lbl in [self.lbl_perf_plays, self.lbl_perf_best_time, self.lbl_perf_avg_time,
                   self.lbl_perf_enemies, self.lbl_perf_damage_dealt, self.lbl_perf_damage_taken,
                   self.lbl_perf_items, self.lbl_perf_perfect, self.lbl_perf_noloss, self.lbl_perf_speed]:
            lbl.config(text="-")
        
        # Mission Results löschen
        self.tree_mission_results.delete(*self.tree_mission_results.get_children())
    
    def apply_level_detail(self):
        """Übernimmt Level-Detail-Änderungen"""
        if self.selected_level_index is None:
            self.set_status("Kein Level ausgewählt.")
            return
        
        levels = ensure_list(self.savegame_data.data.get("levelStates"))
        if self.selected_level_index >= len(levels):
            return
        
        lv = levels[self.selected_level_index]
        lv["starRating"] = int(self.var_level_star.get())
        
        # Parse Status aus "0: Hidden" Format
        status_str = self.var_level_status.get()
        try:
            status_int = int(status_str.split(":")[0])
            lv["levelStatus"] = status_int
        except (ValueError, IndexError):
            self.set_status("Ungültiger Status-Wert.")
            return
        
        self.set_modified(True)
        self.set_status("Level-Details übernommen.")
        
        # Refresh
        self.populate_data()
        self.lst_levels.selection_set(self.selected_level_index)
        self.on_select_level()
    
    def action_unlock_selected_level(self):
        """Schaltet das ausgewählte Level frei"""
        if self.selected_level_index is None:
            self.set_status("Kein Level ausgewählt.")
            return
        
        levels = ensure_list(self.savegame_data.data.get("levelStates"))
        if self.selected_level_index >= len(levels):
            return
        
        lv = levels[self.selected_level_index]
        lid = lv.get("levelID")
        if not lid:
            self.set_status("Level hat keine ID.")
            return
        
        # Zu unlockedLevelIDs hinzufügen
        unlocked = self.savegame_data.data.setdefault("unlockedLevelIDs", [])
        if lid not in unlocked:
            unlocked.append(lid)
            self.set_modified(True)
            self.set_status(f"Level freigeschaltet: {lid}")
        else:
            self.set_status(f"Level bereits freigeschaltet: {lid}")
    
    def action_complete_selected_level(self):
        """Markiert das ausgewählte Level als abgeschlossen"""
        if self.selected_level_index is None:
            self.set_status("Kein Level ausgewählt.")
            return
        
        levels = ensure_list(self.savegame_data.data.get("levelStates"))
        if self.selected_level_index >= len(levels):
            return
        
        lv = levels[self.selected_level_index]
        lid = lv.get("levelID")
        if not lid:
            self.set_status("Level hat keine ID.")
            return
        
        # Zu completedLevelIDs hinzufügen
        completed = self.savegame_data.data.setdefault("completedLevelIDs", [])
        if lid not in completed:
            completed.append(lid)
            self.set_modified(True)
            self.set_status(f"Level als abgeschlossen markiert: {lid}")
        else:
            self.set_status(f"Level bereits abgeschlossen: {lid}")
    
    def action_max_stars_selected(self):
        """Setzt 3 Sterne für das ausgewählte Level"""
        if self.selected_level_index is None:
            self.set_status("Kein Level ausgewählt.")
            return
        
        levels = ensure_list(self.savegame_data.data.get("levelStates"))
        if self.selected_level_index >= len(levels):
            return
        
        lv = levels[self.selected_level_index]
        lv["starRating"] = 3
        
        self.set_modified(True)
        self.set_status("3 Sterne gesetzt.")
        
        # UI aktualisieren
        self.var_level_star.set(3)
        self.populate_data()
        self.lst_levels.selection_set(self.selected_level_index)