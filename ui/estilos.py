"""Estilos de la interfaz: paleta de biblioteca (crema, madera y verde)."""

from tkinter import ttk

COLOR_FONDO = "#F5EBD5"         # crema
COLOR_MADERA = "#6B4423"        # marrón oscuro, encabezados
COLOR_MADERA_CLARA = "#D9C3A0"  # pestañas no seleccionadas
COLOR_VERDE = "#1F5A2B"         # botones de acción
COLOR_VERDE_HOVER = "#2A7A3B"
COLOR_ROJO = "#B22222"          # botón "sin protección"
COLOR_ROJO_HOVER = "#CC3333"
COLOR_TEXTO = "#2B1B0E"
COLOR_TEXTO_CLARO = "#FFFFFF"

FUENTE = ("Arial", 10)
FUENTE_TITULO = ("Arial", 12, "bold")


def aplicar_estilos(raiz):
    """Configura el tema ttk de toda la aplicación."""
    raiz.configure(bg=COLOR_FONDO)
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")  # el tema que mejor deja cambiar colores

    estilo.configure(".", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=FUENTE)
    estilo.configure("TFrame", background=COLOR_FONDO)
    estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO)
    estilo.configure("Titulo.TLabel", font=FUENTE_TITULO)

    # Marcos con título (LabelFrame)
    estilo.configure("TLabelframe", background=COLOR_FONDO,
                     bordercolor=COLOR_MADERA, relief="solid")
    estilo.configure("TLabelframe.Label", background=COLOR_FONDO,
                     foreground=COLOR_MADERA, font=FUENTE_TITULO)

    # Pestañas
    estilo.configure("TNotebook", background=COLOR_MADERA, borderwidth=0)
    estilo.configure("TNotebook.Tab", background=COLOR_MADERA_CLARA,
                     foreground=COLOR_TEXTO, padding=(14, 6), font=FUENTE_TITULO)
    estilo.map("TNotebook.Tab", background=[("selected", COLOR_FONDO)])

    # Botones: verde para acciones, rojo para la demo sin protección
    estilo.configure("Accion.TButton", background=COLOR_VERDE,
                     foreground=COLOR_TEXTO_CLARO, padding=6, borderwidth=0)
    estilo.map("Accion.TButton", background=[("active", COLOR_VERDE_HOVER)])
    estilo.configure("Peligro.TButton", background=COLOR_ROJO,
                     foreground=COLOR_TEXTO_CLARO, padding=6, borderwidth=0)
    estilo.map("Peligro.TButton", background=[("active", COLOR_ROJO_HOVER)])

    # Tablas (Treeview)
    estilo.configure("Treeview", background=COLOR_FONDO, fieldbackground=COLOR_FONDO,
                     foreground=COLOR_TEXTO, rowheight=24, borderwidth=0)
    estilo.configure("Treeview.Heading", background=COLOR_MADERA,
                     foreground=COLOR_TEXTO_CLARO, font=("Arial", 10, "bold"))
    estilo.map("Treeview.Heading", background=[("active", COLOR_MADERA)])