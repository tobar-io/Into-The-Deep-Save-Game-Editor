"""
Quest-Tab für die Verwaltung von Quests und Goals
"""
from tkinter import ttk, StringVar, END, simpledialog
from ..ui_components import tk_listbox, setup_grid_weights, create_section_label
from ..savegame_data import ensure_list
from ..config import QUEST_STATUS_ENUM
from .base_tab import BaseTab


class QuestsTab(BaseTab):
    """Tab für Quest-Verwaltung"""
    
    def __init__(self, parent, savegame_data, asset_manager, status_callback=None):
        # Variables
        self.quest_status_var = StringVar()
        self.selected_quest_index = None
        
        super().__init__(parent, savegame_data, asset_manager, status_callback)
    
    def build_ui(self):
        """Baut die Benutzeroberfläche auf"""
        setup_grid_weights(self.frame, columns=[1, 2], rows=[1])
        
        # Linke Seite - Quest Liste
        left = ttk.Frame(self.frame, padding=8)
        left.grid(row=0, column=0, sticky="NSEW")
        
        ttk.Label(left, text="Quests").pack(anchor="w")
        self.lst_quests = tk_listbox(left)
        self.lst_quests.pack(fill="both", expand=True, pady=(6, 8))
        self.lst_quests.bind("<<ListboxSelect>>", self.on_select_quest)
        
        # Quest-Actions
        btns = ttk.Frame(left)
        btns.pack(fill="x")
        ttk.Button(btns, text="Ziele abschließen", 
                  command=self.action_complete_selected_quest_goals).pack(side="left")
        ttk.Button(btns, text="Quest abschließen", 
                  command=self.action_complete_selected_quest).pack(side="left", padx=(8, 0))
        
        # Rechte Seite - Quest Details
        right = ttk.Frame(self.frame, padding=8)
        right.grid(row=0, column=1, sticky="NSEW")
        
        self._build_quest_detail_form(right)
    
    def _build_quest_detail_form(self, parent):
        """Erstellt das Quest-Detail-Formular"""
        frm = ttk.Frame(parent)
        frm.pack(fill="both", expand=True)
        setup_grid_weights(frm, columns=[1], rows=[0, 0, 0, 0, 1])
        
        # Quest-Info
        info_frame = ttk.Frame(frm)
        info_frame.grid(row=0, column=0, sticky="EW", pady=(0, 8))
        setup_grid_weights(info_frame, columns=[1])
        
        ttk.Label(info_frame, text="Quest ID:").grid(row=0, column=0, sticky="E", padx=6, pady=4)
        self.lbl_quest_id = ttk.Label(info_frame, text="-", font=('TkDefaultFont', 9, 'bold'))
        self.lbl_quest_id.grid(row=0, column=1, sticky="W", padx=6, pady=4)
        
        ttk.Label(info_frame, text="Status:").grid(row=1, column=0, sticky="E", padx=6, pady=4)
        status_values = [f"{k}: {v}" for k, v in QUEST_STATUS_ENUM.items()]
        self.cmb_quest_status = ttk.Combobox(info_frame, textvariable=self.quest_status_var, 
                                           values=status_values, state="readonly", width=20)
        self.cmb_quest_status.grid(row=1, column=1, sticky="W", padx=6, pady=4)
        
        ttk.Button(info_frame, text="Status übernehmen", 
                  command=self.apply_selected_quest_status).grid(
                      row=2, column=1, sticky="W", padx=6, pady=(8, 0))
        
        # Separator
        ttk.Separator(frm, orient='horizontal').grid(row=1, column=0, sticky="EW", pady=12)
        
        # Goal States Header
        create_section_label(frm, "Quest Goals (goalStates)", 2, 1, pady=(0, 4))
        
        # Goal States Treeview
        self._build_goals_treeview(frm)
        
        # Goal Actions
        self._build_goal_actions(frm)
    
    def _build_goals_treeview(self, parent):
        """Erstellt die Treeview für Goal States"""
        # Treeview für Goal States
        cols = ("goalID", "progress", "completed", "main")
        self.tree_quest_goals = ttk.Treeview(parent, columns=cols, show="headings", height=12)
        
        # Headers
        self.tree_quest_goals.heading("goalID", text="Goal ID")
        self.tree_quest_goals.heading("progress", text="Fortschritt")
        self.tree_quest_goals.heading("completed", text="Abgeschlossen")
        self.tree_quest_goals.heading("main", text="Hauptziel")
        
        # Spaltenbreiten
        self.tree_quest_goals.column("goalID", width=200)
        self.tree_quest_goals.column("progress", width=80)
        self.tree_quest_goals.column("completed", width=100)
        self.tree_quest_goals.column("main", width=80)
        
        self.tree_quest_goals.grid(row=3, column=0, sticky="NSEW", padx=6, pady=4)
        self.tree_quest_goals.bind("<Double-1>", self.on_goal_double_click)
        
        # Scrollbar für Treeview
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree_quest_goals.yview)
        scrollbar.grid(row=3, column=1, sticky="NS")
        self.tree_quest_goals.configure(yscrollcommand=scrollbar.set)
    
    def _build_goal_actions(self, parent):
        """Erstellt die Goal-Action-Buttons"""
        goal_actions = ttk.Frame(parent)
        goal_actions.grid(row=4, column=0, sticky="EW", pady=(8, 0))
        
        ttk.Button(goal_actions, text="Goal abschließen", 
                  command=self.action_complete_selected_goal).pack(side="left")
        ttk.Button(goal_actions, text="Goal Progress bearbeiten", 
                  command=self.action_edit_goal_progress).pack(side="left", padx=(8, 0))
        ttk.Button(goal_actions, text="Alle Goals abschließen", 
                  command=self.action_complete_all_goals).pack(side="left", padx=(8, 0))
    
    def populate_data(self):
        """Lädt Daten in die UI-Komponenten"""
        self.lst_quests.delete(0, END)
        
        for i, q in enumerate(ensure_list(self.savegame_data.data.get("questStates"))):
            qid = q.get("questID", f"quest_{i}")
            st = q.get("status", 0)
            status_name = QUEST_STATUS_ENUM.get(st, f"Unknown({st})")
            goals = ensure_list(q.get("goalStates"))
            completed_goals = sum(1 for g in goals if g.get("isCompleted", False))
            total_goals = len(goals)
            self.lst_quests.insert(END, f"{i+1}. {qid} [{status_name}] ({completed_goals}/{total_goals})")
    
    def on_select_quest(self, event=None):
        """Handler für Quest-Auswahl"""
        sel = self.lst_quests.curselection()
        if not sel:
            self.selected_quest_index = None
            self._clear_quest_details()
            return
        
        idx = sel[0]
        self.selected_quest_index = idx
        quests = ensure_list(self.savegame_data.data.get("questStates"))
        
        if idx < len(quests):
            q = quests[idx]
            self._load_quest_details(q)
    
    def _load_quest_details(self, quest):
        """Lädt Quest-Details in die UI"""
        qid = quest.get("questID", f"quest_{self.selected_quest_index}")
        self.lbl_quest_id.config(text=qid)
        
        st = int(quest.get("status", 0) or 0)
        status_str = f"{st}: {QUEST_STATUS_ENUM.get(st, 'Unknown')}"
        self.quest_status_var.set(status_str)
        
        # Goal States anzeigen
        self._update_goals_display(quest)
    
    def _update_goals_display(self, quest):
        """Aktualisiert die Goal-Anzeige"""
        self.tree_quest_goals.delete(*self.tree_quest_goals.get_children())
        
        for g in ensure_list(quest.get("goalStates")):
            goal_id = g.get("goalID", "?")
            progress = g.get("currentProgress", 0)
            completed = "✓" if g.get("isCompleted", False) else "✗"
            main = "✓" if g.get("isMainObjective", False) else "-"
            
            self.tree_quest_goals.insert("", END, values=(goal_id, progress, completed, main))
    
    def _clear_quest_details(self):
        """Löscht Quest-Details"""
        self.lbl_quest_id.config(text="-")
        self.quest_status_var.set("0: NotStarted")
        self.tree_quest_goals.delete(*self.tree_quest_goals.get_children())
    
    def on_goal_double_click(self, event):
        """Doppelklick auf Goal: Progress bearbeiten"""
        self.action_edit_goal_progress()
    
    def action_edit_goal_progress(self):
        """Bearbeitet Goal Progress"""
        sel = self.tree_quest_goals.selection()
        if not sel:
            self.set_status("Kein Goal ausgewählt.")
            return
        
        item = sel[0]
        values = self.tree_quest_goals.item(item, "values")
        goal_id = values[0]
        current_progress = int(values[1])
        
        # Dialog für Progress-Änderung
        new_progress = simpledialog.askinteger(
            "Goal Progress",
            f"Neuer Progress für '{goal_id}':",
            initialvalue=current_progress,
            minvalue=0
        )
        
        if new_progress is not None:
            self._update_goal_progress(goal_id, new_progress)
    
    def _update_goal_progress(self, goal_id, new_progress):
        """Aktualisiert den Progress eines Goals"""
        if self.selected_quest_index is None:
            return
        
        quests = ensure_list(self.savegame_data.data.get("questStates"))
        if self.selected_quest_index >= len(quests):
            return
        
        q = quests[self.selected_quest_index]
        for g in ensure_list(q.get("goalStates")):
            if g.get("goalID") == goal_id:
                g["currentProgress"] = new_progress
                self.set_modified(True)
                self.set_status(f"Goal '{goal_id}' Progress auf {new_progress} gesetzt.")
                break
        
        # Refresh
        self.populate_data()
        self.lst_quests.selection_set(self.selected_quest_index)
        self.on_select_quest()
    
    def apply_selected_quest_status(self):
        """Übernimmt Quest-Status-Änderungen"""
        if self.selected_quest_index is None:
            self.set_status("Keine Quest ausgewählt.")
            return
        
        quests = ensure_list(self.savegame_data.data.get("questStates"))
        if self.selected_quest_index >= len(quests):
            return
        
        q = quests[self.selected_quest_index]
        
        # Parse Status aus "0: NotStarted" Format
        status_str = self.quest_status_var.get()
        try:
            status_int = int(status_str.split(":")[0])
            q["status"] = status_int
            self.set_modified(True)
            self.set_status("Quest-Status übernommen.")
            
            # Refresh
            self.populate_data()
            self.lst_quests.selection_set(self.selected_quest_index)
            self.on_select_quest()
        except (ValueError, IndexError):
            self.set_status("Ungültiger Status-Wert.")
    
    def action_complete_selected_quest_goals(self):
        """Schließt alle Ziele der ausgewählten Quest ab"""
        if self.selected_quest_index is None:
            self.set_status("Keine Quest ausgewählt.")
            return
        
        quests = ensure_list(self.savegame_data.data.get("questStates"))
        if self.selected_quest_index >= len(quests):
            return
        
        q = quests[self.selected_quest_index]
        comp = q.setdefault("completedGoalIDs", [])
        
        goals_completed = 0
        for g in ensure_list(q.get("goalStates")):
            if not g.get("isCompleted", False):
                g["isCompleted"] = True
                goals_completed += 1
                
                gid = g.get("goalID")
                if gid and gid not in comp:
                    comp.append(gid)
        
        if goals_completed > 0:
            self.set_modified(True)
            self.set_status(f"{goals_completed} Ziele abgeschlossen.")
            self.on_select_quest()  # Refresh display
        else:
            self.set_status("Alle Ziele bereits abgeschlossen.")
    
    def action_complete_selected_quest(self):
        """Schließt die ausgewählte Quest komplett ab"""
        if self.selected_quest_index is None:
            self.set_status("Keine Quest ausgewählt.")
            return
        
        # Erst alle Goals abschließen
        self.action_complete_selected_quest_goals()
        
        # Dann Quest-Status auf Completed setzen
        quests = ensure_list(self.savegame_data.data.get("questStates"))
        if self.selected_quest_index < len(quests):
            q = quests[self.selected_quest_index]
            q["status"] = 2  # Completed
            self.set_modified(True)
            
            # Refresh
            self.populate_data()
            self.lst_quests.selection_set(self.selected_quest_index)
            self.on_select_quest()
            
            self.set_status("Quest komplett abgeschlossen.")
    
    def action_complete_selected_goal(self):
        """Schließt das ausgewählte Goal ab"""
        sel = self.tree_quest_goals.selection()
        if not sel:
            self.set_status("Kein Goal ausgewählt.")
            return
        
        item = sel[0]
        values = self.tree_quest_goals.item(item, "values")
        goal_id = values[0]
        
        if self.selected_quest_index is None:
            return
        
        quests = ensure_list(self.savegame_data.data.get("questStates"))
        if self.selected_quest_index >= len(quests):
            return
        
        q = quests[self.selected_quest_index]
        comp = q.setdefault("completedGoalIDs", [])
        
        for g in ensure_list(q.get("goalStates")):
            if g.get("goalID") == goal_id:
                g["isCompleted"] = True
                if goal_id not in comp:
                    comp.append(goal_id)
                self.set_modified(True)
                self.set_status(f"Goal '{goal_id}' abgeschlossen.")
                self.on_select_quest()  # Refresh
                return
        
        self.set_status(f"Goal '{goal_id}' nicht gefunden.")
    
    def action_complete_all_goals(self):
        """Schließt alle Goals der aktuellen Quest ab"""
        self.action_complete_selected_quest_goals()