"""Pestaña 1: Mostrador (planificación de procesos)."""

import tkinter as tk
from tkinter import ttk, messagebox

from kernel.modelos import Usuario, PRIORIDAD_POR_TIPO
from kernel.planificador.metricas import comparar_algoritmos
from ui.estilos import COLOR_FONDO, COLOR_TEXTO

ALGORITMOS = ["FCFS", "SJF", "Round Robin", "Prioridad"]
COLORES = ["#4A7FB5", "#C0504D", "#8E5FA8", "#5FA05F",
           "#D9902F", "#3FA7A0", "#A0522D", "#7A7A7A"]


class TabMostrador(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.usuarios = [
            Usuario("Ana Torres", "Estudiante", 1, 5),
            Usuario("Juan Quispe", "Docente", 2, 8),
            Usuario("Pedro Gomez", "Discapacidad", 3, 4),
            Usuario("Maria Arias", "Estudiante", 5, 6),
        ]
        self._linea = []  # última línea de tiempo dibujada

        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=1)
        self._construir_cola()
        self._construir_panel_derecho()
        self._refrescar_cola()

    # ---------- Construcción de la pantalla ----------

    def _construir_cola(self):
        marco = ttk.LabelFrame(self, text="Cola de usuarios")
        marco.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        columnas = ("usuario", "tipo", "llegada", "duracion", "prioridad")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings")
        encabezados = [("usuario", "Usuario", 105), ("tipo", "Tipo", 85),
                       ("llegada", "Llegada", 55), ("duracion", "Duración", 65),
                       ("prioridad", "Prioridad", 65)]
        for col, texto, ancho in encabezados:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        botones = ttk.Frame(marco)
        botones.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        botones.columnconfigure((0, 1), weight=1)
        ttk.Button(botones, text="Agregar usuario", style="Accion.TButton",
                   command=self._agregar).grid(row=0, column=0, sticky="ew", padx=(0, 3))
        ttk.Button(botones, text="Limpiar", style="Accion.TButton",
                   command=self._limpiar).grid(row=0, column=1, sticky="ew", padx=(3, 0))

    def _construir_panel_derecho(self):
        der = ttk.Frame(self)
        der.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        der.columnconfigure(0, weight=1)
        der.rowconfigure(1, weight=1)

        # Configuración
        config = ttk.LabelFrame(der, text="Configuración")
        config.grid(row=0, column=0, sticky="ew")
        config.columnconfigure(1, weight=1)
        self.var_algoritmo = tk.StringVar(value="Round Robin")
        self.var_quantum = tk.StringVar(value="3")
        ttk.Label(config, text="Algoritmo").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Combobox(config, textvariable=self.var_algoritmo, values=ALGORITMOS,
                     state="readonly").grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ttk.Label(config, text="Quantum").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(config, textvariable=self.var_quantum).grid(
            row=1, column=1, padx=10, pady=5, sticky="ew")
        ttk.Button(config, text="Ejecutar simulación", style="Accion.TButton",
                   command=self._ejecutar).grid(
            row=2, column=0, columnspan=2, padx=10, pady=8, sticky="ew")

        # Línea de tiempo (Gantt)
        gantt = ttk.LabelFrame(der, text="Línea de tiempo")
        gantt.grid(row=1, column=0, sticky="nsew", pady=8)
        self.canvas = tk.Canvas(gantt, height=170, bg=COLOR_FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self.canvas.bind("<Configure>", lambda e: self._dibujar_gantt())

        # Comparación de algoritmos
        comp = ttk.LabelFrame(der, text="Comparación de algoritmos")
        comp.grid(row=2, column=0, sticky="ew")
        self.tabla_comp = ttk.Treeview(comp, columns=("alg", "espera", "resp"),
                                       show="headings", height=4)
        for col, texto in [("alg", "Algoritmo"), ("espera", "Espera promedio"),
                           ("resp", "Respuesta promedio")]:
            self.tabla_comp.heading(col, text=texto)
            self.tabla_comp.column(col, anchor="center")
        self.tabla_comp.pack(fill="x", padx=5, pady=5)

    # ---------- Acciones ----------

    def _refrescar_cola(self):
        """Redibuja la tabla de usuarios e invalida los resultados anteriores."""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for u in self.usuarios:
            self.tabla.insert("", "end", values=(u.nombre, u.tipo, u.llegada,
                                                 u.duracion, u.prioridad))
        self._linea = []
        self._dibujar_gantt()
        for fila in self.tabla_comp.get_children():
            self.tabla_comp.delete(fila)

    def _limpiar(self):
        self.usuarios.clear()
        self._refrescar_cola()

    def _agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar usuario")
        ventana.configure(bg=COLOR_FONDO)
        ventana.resizable(False, False)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        nombre = tk.StringVar()
        tipo = tk.StringVar(value="Estudiante")
        llegada = tk.StringVar(value="0")
        duracion = tk.StringVar(value="1")
        campos = [
            ("Nombre", ttk.Entry(ventana, textvariable=nombre)),
            ("Tipo", ttk.Combobox(ventana, textvariable=tipo,
                                  values=list(PRIORIDAD_POR_TIPO), state="readonly")),
            ("Llegada (min)", ttk.Entry(ventana, textvariable=llegada)),
            ("Duración (min)", ttk.Entry(ventana, textvariable=duracion)),
        ]
        for fila, (texto, widget) in enumerate(campos):
            ttk.Label(ventana, text=texto).grid(row=fila, column=0, padx=10, pady=5, sticky="w")
            widget.grid(row=fila, column=1, padx=10, pady=5)

        def guardar():
            nom = nombre.get().strip()
            if not nom:
                messagebox.showerror("Dato no válido", "Escribe un nombre.", parent=ventana)
                return
            if any(u.nombre == nom for u in self.usuarios):
                messagebox.showerror("Dato no válido",
                                     "Ya existe un usuario con ese nombre.", parent=ventana)
                return
            try:
                ll = int(llegada.get())
                du = int(duracion.get())
            except ValueError:
                messagebox.showerror("Dato no válido",
                                     "Llegada y duración deben ser números enteros.",
                                     parent=ventana)
                return
            try:
                usuario = Usuario(nom, tipo.get(), ll, du)
            except ValueError as error:
                messagebox.showerror("Dato no válido", str(error), parent=ventana)
                return
            self.usuarios.append(usuario)
            self._refrescar_cola()
            ventana.destroy()

        ttk.Button(ventana, text="Guardar", style="Accion.TButton",
                   command=guardar).grid(row=4, column=0, columnspan=2, pady=10)

    def _ejecutar(self):
        if not self.usuarios:
            messagebox.showwarning("Cola vacía", "Agrega al menos un usuario.")
            return
        try:
            quantum = int(self.var_quantum.get())
            if quantum <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Quantum no válido",
                                 "El quantum debe ser un entero mayor que 0.")
            return

        resultados = comparar_algoritmos(self.usuarios, quantum)
        self._linea = resultados[self.var_algoritmo.get()]["linea"]
        self._dibujar_gantt()

        for fila in self.tabla_comp.get_children():
            self.tabla_comp.delete(fila)
        for nombre, r in resultados.items():
            m = r["metricas"]
            self.tabla_comp.insert("", "end", values=(
                nombre, f"{m['espera_promedio']:.2f}", f"{m['respuesta_promedio']:.2f}"))

    # ---------- Dibujo del Gantt ----------

    def _dibujar_gantt(self):
        c = self.canvas
        c.delete("all")
        if not self._linea:
            return
        nombres = [u.nombre for u in self.usuarios]
        colores = {n: COLORES[i % len(COLORES)] for i, n in enumerate(nombres)}

        ancho, alto = c.winfo_width(), c.winfo_height()
        izq, der, sup, inf = 95, 15, 10, 25
        t_max = max(fin for _, _, fin in self._linea)
        escala = (ancho - izq - der) / t_max
        alto_fila = (alto - sup - inf) / len(nombres)

        for i, n in enumerate(nombres):
            y = sup + i * alto_fila
            c.create_text(izq - 6, y + alto_fila / 2, text=n, anchor="e",
                          fill=COLOR_TEXTO, font=("Arial", 9))

        for nombre, ini, fin in self._linea:
            y = sup + nombres.index(nombre) * alto_fila
            c.create_rectangle(izq + ini * escala, y + 4, izq + fin * escala,
                               y + alto_fila - 4, fill=colores[nombre], outline=COLOR_TEXTO)

        y_eje = alto - inf + 2
        c.create_line(izq, y_eje, ancho - der, y_eje, fill=COLOR_TEXTO)
        paso = max(1, round(t_max / 10))
        for t in range(0, t_max + 1, paso):
            x = izq + t * escala
            c.create_line(x, y_eje, x, y_eje + 4, fill=COLOR_TEXTO)
            c.create_text(x, y_eje + 13, text=str(t), fill=COLOR_TEXTO, font=("Arial", 8))