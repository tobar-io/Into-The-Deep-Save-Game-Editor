"""
Wiederverwendbare UI-Komponenten für den Save Game Editor
"""
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar, IntVar, DoubleVar, BooleanVar
from typing import Union


def tk_listbox(parent, height: int = 18) -> tk.Listbox:
    """Erstellt eine Listbox mit Standardeinstellungen"""
    # ttk bietet kein natives Listbox-Widget, daher klassisch:
    lb = tk.Listbox(parent, height=height, activestyle="dotbox")
    lb.configure(exportselection=False)
    return lb


def add_label_entry(frm: ttk.Frame, label: str, var: StringVar, row: int, col: int, 
                   col_span: int = 1, readonly: bool = False) -> ttk.Entry:
    """Fügt Label und Entry zu einem Frame hinzu"""
    ttk.Label(frm, text=label).grid(row=row, column=col, sticky="E", padx=6, pady=4)
    e = ttk.Entry(frm, textvariable=var)
    if readonly:
        e.state(["readonly"])
    e.grid(row=row, column=col+1, sticky="EW", padx=6, pady=4, columnspan=col_span)
    return e


def add_label_spin(frm: ttk.Frame, label: str, var: Union[IntVar, DoubleVar], 
                  row: int, col: int, default: Union[int, float], 
                  frm_min: Union[int, float], frm_max: Union[int, float]) -> ttk.Spinbox:
    """Fügt Label und Spinbox zu einem Frame hinzu"""
    ttk.Label(frm, text=label).grid(row=row, column=col, sticky="E", padx=6, pady=4)
    
    if isinstance(var, IntVar):
        spn = ttk.Spinbox(frm, from_=frm_min, to=frm_max, textvariable=var, width=10)
    else:
        spn = ttk.Spinbox(frm, from_=frm_min, to=frm_max, textvariable=var, width=10, increment=1)
    
    spn.grid(row=row, column=col+1, sticky="W", padx=6, pady=4)
    return spn


def add_label_float(frm: ttk.Frame, label: str, var: DoubleVar, row: int, col: int, 
                   default: float, frm_min: float, frm_max: float) -> ttk.Spinbox:
    """Fügt Label und Float-Spinbox zu einem Frame hinzu"""
    ttk.Label(frm, text=label).grid(row=row, column=col, sticky="E", padx=6, pady=4)
    spn = ttk.Spinbox(frm, from_=frm_min, to=frm_max, textvariable=var, width=10, increment=0.5)
    spn.grid(row=row, column=col+1, sticky="W", padx=6, pady=4)
    return spn


def add_label_check(frm: ttk.Frame, label: str, var: BooleanVar, row: int, col: int) -> ttk.Checkbutton:
    """Fügt eine Checkbox zu einem Frame hinzu"""
    cb = ttk.Checkbutton(frm, text=label, variable=var)
    cb.grid(row=row, column=col, sticky="W", padx=6, pady=4)
    return cb


def create_separator(frm: ttk.Frame, row: int, col_span: int = 2, pady: int = 8) -> ttk.Separator:
    """Erstellt einen horizontalen Separator"""
    sep = ttk.Separator(frm, orient='horizontal')
    sep.grid(row=row, column=0, columnspan=col_span, sticky="EW", pady=pady)
    return sep


def create_section_label(frm: ttk.Frame, text: str, row: int, col_span: int = 2, 
                        pady: tuple = (0, 8)) -> ttk.Label:
    """Erstellt ein Abschnitts-Label"""
    lbl = ttk.Label(frm, text=text, font=('TkDefaultFont', 9, 'bold'))
    lbl.grid(row=row, column=0, columnspan=col_span, sticky="W", pady=pady)
    return lbl


def setup_grid_weights(widget: ttk.Widget, columns: list = None, rows: list = None) -> None:
    """Konfiguriert Grid-Gewichte für responsives Layout"""
    if columns:
        for i, weight in enumerate(columns):
            widget.columnconfigure(i, weight=weight)
    
    if rows:
        for i, weight in enumerate(rows):
            widget.rowconfigure(i, weight=weight)


def create_button_frame(parent: ttk.Widget, buttons: list) -> ttk.Frame:
    """Erstellt einen Frame mit mehreren Buttons
    
    Args:
        parent: Übergeordnetes Widget
        buttons: Liste von Tuples (text, command, **kwargs)
    """
    frame = ttk.Frame(parent)
    
    for i, button_info in enumerate(buttons):
        text = button_info[0]
        command = button_info[1]
        kwargs = button_info[2] if len(button_info) > 2 else {}
        
        btn = ttk.Button(frame, text=text, command=command, **kwargs)
        btn.pack(side="left", padx=(0 if i == 0 else 6, 0))
    
    return frame


class ScrollableFrame(ttk.Frame):
    """Ein scrollbarer Frame für längere Inhalte"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Canvas und Scrollbar erstellen
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Frame zu Canvas hinzufügen
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Scrolling konfigurieren
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Mausrad-Scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Canvas-Größe an Frame anpassen
        self.bind(
            "<Configure>",
            lambda e: self.canvas.configure(width=e.width - self.scrollbar.winfo_reqwidth())
        )
    
    def _on_mousewheel(self, event):
        """Verarbeitet Mausrad-Events für Scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")