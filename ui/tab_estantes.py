"""Pestaña 3: Estantes (gestión de memoria).

Izquierda: el panel de estantes (asignación contigua con first fit / best fit
y su fragmentación).
Derecha: la mesa de acceso rápido (marcos de la RAM), la configuración del
reemplazo de páginas (FIFO, LRU, Óptimo) y los resultados paso a paso.

Toda la lógica vive en kernel/memoria; aquí solo se dibuja y se leen los datos.
"""

import tkinter as tk
from tkinter import ttk

from kernel.modelos import Libro
from kernel.memoria.estantes import BEST_FIT, FIRST_FIT, Estante
from kernel.memoria.reemplazo import ALGORITMOS, comparar, texto_marcos
from kernel.memoria.belady import demostrar_belady, texto_anomalia
from ui.estilos import (COLOR_FONDO, COLOR_MADERA, COLOR_ROJO, COLOR_TEXTO,
                        COLOR_VERDE)

from ui.ventana_paginacion import VentanaPaginacion
CAPACIDAD = 20          # posiciones del estante
COLUMNAS = 5            # el estante se dibuja en filas de 5 posiciones
ALTO_CELDA = 54
SECUENCIA_INICIAL = "7,0,1,2,0,3,0,4,2,3"
MAX_MARCOS = 8
ESTRATEGIAS = {"First fit": FIRST_FIT, "Best fit": BEST_FIT}

# Un color por libro (se repite si hay más libros que colores).
PALETA = ["#8B5A2B", "#4F8A4B", "#B5483F", "#7E57A8", "#3D6E91", "#B8862B"]

# Estante de ejemplo: ocho libros (código, tamaño) y se retiran el 2 y el 4,
# para que ya haya huecos de distinto tamaño y se note la diferencia entre
# first fit y best fit.
LIBROS_EJEMPLO = [(1, 2), (2, 3), (3, 1), (4, 2), (5, 2), (6, 3), (7, 1), (8, 2)]
RETIRADOS_EJEMPLO = [2, 4]


def color_libro(codigo):
    return PALETA[codigo % len(PALETA)]


class TabEstantes(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.estante = None
        self._siguiente_codigo = 1
        self._resultados = None      # comparar(...) de la última simulación
        self._pasos = []             # pasos del algoritmo elegido
        self._cursor = 0             # cuántos pedidos ya se mostraron
        self._marcos_sim = 3
        self._ventana_paginacion = None
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(0, weight=1)
        self._construir_izquierda()
        self._construir_derecha()

        self._reiniciar_estante()
        self._dibujar_mesa([None] * 3)
        self._mostrar_totales(None)

    # ---------- Construcción de la pantalla ----------

    def _construir_izquierda(self):
        izq = ttk.Frame(self)
        izq.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        izq.columnconfigure(0, weight=1)
        izq.rowconfigure(0, weight=1)

        panel = ttk.LabelFrame(izq, text="Panel Estantes")
        panel.grid(row=0, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        filas = -(-CAPACIDAD // COLUMNAS)
        self.canvas_estante = tk.Canvas(panel, height=filas * ALTO_CELDA + 2,
                                        bg=COLOR_FONDO, highlightthickness=0)
        self.canvas_estante.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.canvas_estante.bind("<Configure>", lambda e: self._dibujar_estante())

        self.lbl_fragmentacion = ttk.Label(panel, font=("Arial", 9, "bold"))
        self.lbl_fragmentacion.grid(row=1, column=0, sticky="w", padx=8)

        # Controles para colocar y retirar libros
        ctrl = ttk.Frame(panel)
        ctrl.grid(row=2, column=0, sticky="ew", padx=5, pady=(6, 2))
        self.var_estrategia = tk.StringVar(value="First fit")
        self.var_tamano = tk.StringVar(value="2")
        self.var_retirar = tk.StringVar()
        ttk.Combobox(ctrl, textvariable=self.var_estrategia, width=9,
                     values=list(ESTRATEGIAS), state="readonly").grid(row=0, column=0)
        ttk.Label(ctrl, text="Tamaño").grid(row=0, column=1, padx=(8, 2))
        ttk.Spinbox(ctrl, from_=1, to=CAPACIDAD, width=4,
                    textvariable=self.var_tamano).grid(row=0, column=2)
        ttk.Button(ctrl, text="Colocar libro", style="Accion.TButton",
                   command=self._colocar).grid(row=0, column=3, padx=(8, 0))

        ctrl2 = ttk.Frame(panel)
        ctrl2.grid(row=3, column=0, sticky="ew", padx=5, pady=(2, 2))
        ttk.Label(ctrl2, text="Retirar libro Nº").grid(row=0, column=0)
        ttk.Entry(ctrl2, textvariable=self.var_retirar, width=5).grid(
            row=0, column=1, padx=4)
        ttk.Button(ctrl2, text="Retirar", style="Accion.TButton",
                   command=self._retirar).grid(row=0, column=2, padx=4)
        ttk.Button(ctrl2, text="Reiniciar estante", style="Accion.TButton",
                   command=self._reiniciar_estante).grid(row=0, column=3, padx=4)

        self.lbl_estado_estante = ttk.Label(panel, font=("Arial", 9), wraplength=420)
        self.lbl_estado_estante.grid(row=4, column=0, sticky="w", padx=8, pady=(2, 6))

        ttk.Button(izq, text="Demostrar anomalía de Belady", style="Accion.TButton",
                   command=self._mostrar_belady).grid(row=1, column=0, sticky="ew",
                                                      pady=(8, 0))
                   
        ttk.Button(izq, text="Paginación y tabla de páginas", style="Accion.TButton",
                   command=self._abrir_paginacion).grid(row=2, column=0, sticky="ew",
                                                        pady=(6, 0))                   

    def _construir_derecha(self):
        der = ttk.Frame(self)
        der.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        der.columnconfigure(0, weight=1)
        der.rowconfigure(2, weight=1)

        # Mesa de acceso rápido (RAM)
        mesa = ttk.LabelFrame(der, text="Mesa de acceso rápido (RAM)")
        mesa.grid(row=0, column=0, sticky="ew")
        self.canvas_mesa = tk.Canvas(mesa, height=90, bg=COLOR_FONDO,
                                     highlightthickness=0)
        self.canvas_mesa.pack(fill="x", padx=5, pady=5)
        self.canvas_mesa.bind("<Configure>", lambda e: self._redibujar_mesa())
        self._marcos_mostrados = [None] * 3

        # Configuración
        config = ttk.LabelFrame(der, text="Configuración")
        config.grid(row=1, column=0, sticky="ew", pady=8)
        config.columnconfigure(1, weight=1)
        self.var_secuencia = tk.StringVar(value=SECUENCIA_INICIAL)
        self.var_algoritmo = tk.StringVar(value=ALGORITMOS[0])
        self.var_marcos = tk.StringVar(value="3")
        ttk.Label(config, text="Secuencia de pedidos").grid(
            row=0, column=0, padx=10, pady=4, sticky="w")
        ttk.Entry(config, textvariable=self.var_secuencia).grid(
            row=0, column=1, padx=10, pady=4, sticky="ew")
        ttk.Label(config, text="Algoritmo").grid(row=1, column=0, padx=10, pady=4, sticky="w")
        ttk.Combobox(config, textvariable=self.var_algoritmo, values=ALGORITMOS,
                     state="readonly").grid(row=1, column=1, padx=10, pady=4, sticky="ew")
        ttk.Label(config, text="Marcos").grid(row=2, column=0, padx=10, pady=4, sticky="w")
        ttk.Spinbox(config, from_=1, to=MAX_MARCOS, textvariable=self.var_marcos,
                    width=5).grid(row=2, column=1, padx=10, pady=4, sticky="ew")
        botones = ttk.Frame(config)
        botones.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(4, 8))
        botones.columnconfigure((0, 1), weight=1)
        ttk.Button(botones, text="Simular", style="Accion.TButton",
                   command=self._simular).grid(row=0, column=0, sticky="ew", padx=(0, 3))
        ttk.Button(botones, text="Siguiente paso", style="Accion.TButton",
                   command=self._siguiente_paso).grid(row=0, column=1, sticky="ew",
                                                      padx=(3, 0))
        self.lbl_error = ttk.Label(config, foreground=COLOR_ROJO, font=("Arial", 9))
        self.lbl_error.grid(row=4, column=0, columnspan=2, sticky="w", padx=10)

        # Resultados
        res = ttk.LabelFrame(der, text="Resultados")
        res.grid(row=2, column=0, sticky="nsew")
        res.columnconfigure(0, weight=1)
        res.rowconfigure(0, weight=1)
        self.tabla = ttk.Treeview(res, columns=("pedido", "marcos", "fallo", "sale"),
                                  show="headings", height=6)
        for col, texto, ancho in [("pedido", "Pedido", 55), ("marcos", "Estado de Marcos", 120),
                                  ("fallo", "Fallo", 50), ("sale", "Sale", 50)]:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="center")
        barra = ttk.Scrollbar(res, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        barra.grid(row=0, column=1, sticky="ns", pady=5)

        totales = ttk.LabelFrame(res, text="Fallos totales")
        totales.grid(row=0, column=2, sticky="ns", padx=5, pady=5)
        self.lbl_totales = {}
        for nombre in ALGORITMOS:
            etiqueta = ttk.Label(totales, font=("Arial", 10))
            etiqueta.pack(anchor="w", padx=8, pady=3)
            self.lbl_totales[nombre] = etiqueta

    # ---------- Estantes ----------

    def _reiniciar_estante(self):
        self.estante = Estante(CAPACIDAD)
        for codigo, tamano in LIBROS_EJEMPLO:
            self.estante.colocar(Libro(codigo, f"Libro {codigo}"), tamano, FIRST_FIT)
        for codigo in RETIRADOS_EJEMPLO:
            self.estante.retirar(codigo)
        self._siguiente_codigo = max(c for c, _ in LIBROS_EJEMPLO) + 1
        self.lbl_estado_estante.configure(
            text="Estante de ejemplo: tiene huecos de distinto tamaño. "
                 "Coloca un libro con cada estrategia y compara.")
        self._refrescar_estante()

    def _refrescar_estante(self):
        f = self.estante.fragmentacion()
        self.lbl_fragmentacion.configure(
            text=(f"Libre: {f['libre_total']}  |  Hueco mayor: {f['hueco_mayor']}  |  "
                  f"Huecos: {f['num_huecos']}  |  Fragmentación externa: "
                  f"{f['fragmentacion_externa']}%"))
        self._dibujar_estante()

    def _leer_entero(self, texto, nombre):
        try:
            valor = int(texto.strip())
        except ValueError:
            raise ValueError(f"{nombre} debe ser un número entero")
        if valor <= 0:
            raise ValueError(f"{nombre} debe ser mayor que 0")
        return valor

    def _colocar(self):
        try:
            tamano = self._leer_entero(self.var_tamano.get(), "El tamaño")
        except ValueError as error:
            self.lbl_estado_estante.configure(text=str(error))
            return
        estrategia = ESTRATEGIAS[self.var_estrategia.get()]
        codigo = self._siguiente_codigo
        inicio = self.estante.colocar(Libro(codigo, f"Libro {codigo}"), tamano, estrategia)
        if inicio is None:
            f = self.estante.fragmentacion()
            self.lbl_estado_estante.configure(
                text=(f"El Libro {codigo} (tamaño {tamano}) no cabe: hay {f['libre_total']} "
                      f"posiciones libres, pero el hueco mayor es de {f['hueco_mayor']}."))
        else:
            self._siguiente_codigo += 1
            self.lbl_estado_estante.configure(
                text=(f"Libro {codigo} (tamaño {tamano}) colocado en la posición {inicio} "
                      f"con {self.var_estrategia.get().lower()}."))
        self._refrescar_estante()

    def _retirar(self):
        try:
            codigo = self._leer_entero(self.var_retirar.get(), "El número de libro")
        except ValueError as error:
            self.lbl_estado_estante.configure(text=str(error))
            return
        if self.estante.retirar(codigo):
            self.lbl_estado_estante.configure(text=f"Libro {codigo} retirado.")
        else:
            self.lbl_estado_estante.configure(text=f"El Libro {codigo} no está en el estante.")
        self._refrescar_estante()

    def _dibujar_estante(self):
        c = self.canvas_estante
        c.delete("all")
        ancho = max(c.winfo_width(), 300)
        celda = ancho / COLUMNAS
        bloques = self.estante.bloques()
        dueno = {}
        for n, b in enumerate(bloques):
            for pos in range(b["inicio"], b["inicio"] + b["tamano"]):
                dueno[pos] = n

        filas = -(-CAPACIDAD // COLUMNAS)
        for fila in range(filas):
            pos = fila * COLUMNAS
            fin = min(pos + COLUMNAS, CAPACIDAD)
            while pos < fin:
                n = dueno[pos]
                ultimo = pos
                while ultimo + 1 < fin and dueno[ultimo + 1] == n:
                    ultimo += 1
                b = bloques[n]
                x0 = (pos % COLUMNAS) * celda + 1
                x1 = ((ultimo % COLUMNAS) + 1) * celda - 1
                y0 = fila * ALTO_CELDA + 1
                y1 = (fila + 1) * ALTO_CELDA - 1
                if b["libro"] is None:
                    c.create_rectangle(x0, y0, x1, y1, fill=COLOR_FONDO, outline=COLOR_MADERA)
                    c.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="Hueco libre",
                                  fill=COLOR_TEXTO, width=x1 - x0 - 6, font=("Arial", 9))
                else:
                    c.create_rectangle(x0, y0, x1, y1, fill=color_libro(b["libro"].codigo),
                                       outline=COLOR_TEXTO, width=2)
                    c.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                  text=f"Libro {b['libro'].codigo}", fill="white",
                                  font=("Arial", 9, "bold"))
                pos = ultimo + 1

    # ---------- Reemplazo de páginas ----------

    def _leer_simulacion(self):
        """Lee y valida la configuración. Devuelve (secuencia, marcos) o None."""
        self.lbl_error.configure(text="")
        try:
            secuencia = [int(p) for p in self.var_secuencia.get().replace(" ", "").split(",")
                         if p != ""]
            if not secuencia:
                raise ValueError("Escribe la secuencia de pedidos, por ejemplo 7,0,1,2")
            marcos = self._leer_entero(self.var_marcos.get(), "Los marcos")
            if marcos > MAX_MARCOS:
                raise ValueError(f"Máximo {MAX_MARCOS} marcos")
        except ValueError as error:
            texto = str(error)
            if texto.startswith("invalid literal"):
                texto = "La secuencia solo puede tener números separados por comas"
            self.lbl_error.configure(text=texto)
            return None
        return secuencia, marcos

    def _preparar(self):
        """Corre los tres algoritmos y deja listos los pasos del elegido."""
        datos = self._leer_simulacion()
        if datos is None:
            return False
        secuencia, marcos = datos
        self._resultados = comparar(secuencia, marcos)
        self._pasos = self._resultados[self.var_algoritmo.get()]["pasos"]
        self._cursor = 0
        self._marcos_sim = marcos
        self._limpiar_tabla()
        self._marcos_mostrados = [None] * marcos
        self._redibujar_mesa()
        self._mostrar_totales(None)
        return True

    def _simular(self):
        """Muestra todos los pasos de una vez."""
        if not self._preparar():
            return
        while self._cursor < len(self._pasos):
            self._avanzar()

    def _siguiente_paso(self):
        """Muestra el siguiente pedido; si ya terminó, empieza de nuevo."""
        if self._resultados is None or self._cursor >= len(self._pasos):
            if not self._preparar():
                return
        self._avanzar()

    def _avanzar(self):
        paso = self._pasos[self._cursor]
        self._cursor += 1
        self.tabla.insert("", "end", values=(
            paso["pedido"], texto_marcos(paso["marcos"]),
            "Sí" if paso["fallo"] else "No",
            "–" if paso["victima"] is None else paso["victima"]))
        self.tabla.yview_moveto(1)
        self._marcos_mostrados = list(paso["marcos"])
        self._redibujar_mesa(resaltar=paso["pedido"] if paso["fallo"] else None)
        if self._cursor == len(self._pasos):
            self._mostrar_totales(self._resultados)

    def _limpiar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

    def _mostrar_totales(self, resultados):
        for nombre, etiqueta in self.lbl_totales.items():
            if resultados is None:
                etiqueta.configure(text=f"{nombre}: –")
            else:
                etiqueta.configure(text=f"{nombre}: {resultados[nombre]['fallos']}")

    def _redibujar_mesa(self, resaltar=None):
        self._dibujar_mesa(self._marcos_mostrados, resaltar)

    def _dibujar_mesa(self, marcos, resaltar=None):
        self._marcos_mostrados = list(marcos)
        c = self.canvas_mesa
        c.delete("all")
        ancho = max(c.winfo_width(), 300)
        celda = ancho / len(marcos)
        for i, libro in enumerate(marcos):
            x0, x1 = i * celda + 4, (i + 1) * celda - 4
            c.create_rectangle(x0, 4, x1, 86, fill=COLOR_FONDO, outline=COLOR_MADERA)
            if libro is not None:
                borde = COLOR_ROJO if libro == resaltar else COLOR_TEXTO
                c.create_rectangle(x0 + 8, 12, x1 - 8, 78, fill=color_libro(libro),
                                   outline=borde, width=3 if libro == resaltar else 2)
                c.create_text((x0 + x1) / 2, 45, text=f"Libro {libro}", fill="white",
                              font=("Arial", 9, "bold"))
                
    # ---------- Paginación ----------

    def _abrir_paginacion(self):
        """Abre la ventana de paginación (una sola a la vez)."""
        if self._ventana_paginacion is not None and self._ventana_paginacion.winfo_exists():
            self._ventana_paginacion.lift()
            return
        self._ventana_paginacion = VentanaPaginacion(self, color_libro)                
                

    # ---------- Anomalía de Belady ----------

    def _mostrar_belady(self):
        r = demostrar_belady()
        ventana = tk.Toplevel(self)
        ventana.title("Anomalía de Belady")
        ventana.configure(bg=COLOR_FONDO)
        ventana.resizable(False, False)

        secuencia = ",".join(str(p) for p in r["secuencia"])
        ttk.Label(ventana, text=f"Secuencia: {secuencia}",
                  font=("Arial", 10, "bold")).pack(padx=14, pady=(12, 4))
        ttk.Label(ventana, text="Más marcos debería significar menos fallos...").pack()

        tabla = ttk.Treeview(ventana, columns=("marcos", "fifo", "lru"),
                             show="headings", height=len(r["fifo"]))
        for col, texto in [("marcos", "Marcos"), ("fifo", "Fallos FIFO"), ("lru", "Fallos LRU")]:
            tabla.heading(col, text=texto)
            tabla.column(col, width=100, anchor="center")
        tabla.tag_configure("anomalia", foreground=COLOR_ROJO)
        marcas = {m2 for _, _, m2, _ in r["anomalias"]}
        for (m, f_fifo), (_, f_lru) in zip(r["fifo"], r["lru"]):
            tabla.insert("", "end", values=(m, f_fifo, f_lru),
                         tags=("anomalia",) if m in marcas else ())
        tabla.pack(padx=14, pady=8)

        if r["hay_anomalia"]:
            for anomalia in r["anomalias"]:
                ttk.Label(ventana, text="FIFO: " + texto_anomalia(anomalia),
                          foreground=COLOR_ROJO,
                          font=("Arial", 10, "bold")).pack(padx=14)
            ttk.Label(ventana, text="Con más memoria, FIFO falló más. LRU nunca lo hace.",
                      foreground=COLOR_VERDE).pack(padx=14, pady=(2, 0))
        ttk.Button(ventana, text="Cerrar", style="Accion.TButton",
                   command=ventana.destroy).pack(pady=12)