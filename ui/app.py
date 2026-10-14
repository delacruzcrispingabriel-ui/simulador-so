"""Ventana principal: una pestaña por módulo."""

import tkinter as tk
from tkinter import ttk

from ui.estilos import aplicar_estilos

PESTANAS = [
    ("1. Mostrador", "Planificación de procesos"),
    ("2. Catálogo", "Sincronización"),
    ("3. Estantes", "Gestión de memoria"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biblioteca FIIS - Simulador de Sistema Operativo")
        self.geometry("900x600")
        self.minsize(800, 520)
        aplicar_estilos(self)

        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)

        for titulo, tema in PESTANAS:
            cuaderno.add(self._pestana_provisional(cuaderno, tema), text=titulo)

    def _pestana_provisional(self, padre, tema):
        """Cartel temporal; se reemplaza cuando se construye cada pestaña."""
        marco = ttk.Frame(padre)
        ttk.Label(marco, text=f"{tema}\n(en construcción)",
                  style="Titulo.TLabel", justify="center").pack(expand=True)
        return marco