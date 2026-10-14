"""Ventana principal: una pestaña por módulo."""

import tkinter as tk
from tkinter import ttk

from ui.estilos import aplicar_estilos
from ui.tab_mostrador import TabMostrador
from ui.tab_catalogo import TabCatalogo
from ui.tab_estantes import TabEstantes


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biblioteca FIIS - Simulador de Sistema Operativo")
        self.geometry("900x600")
        self.minsize(800, 520)
        aplicar_estilos(self)

        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)

        cuaderno.add(TabMostrador(cuaderno), text="1. Mostrador")
        cuaderno.add(TabCatalogo(cuaderno), text="2. Catálogo")
        cuaderno.add(TabEstantes(cuaderno), text="3. Estantes")


if __name__ == "__main__":
    App().mainloop()