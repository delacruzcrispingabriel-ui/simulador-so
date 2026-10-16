"""Ventana de paginación (Módulo 3): tabla de páginas y traducción de direcciones.

Se abre desde la pestaña Estantes. Toda la lógica vive en
kernel/memoria/paginacion.py; aquí solo se dibuja y se leen los datos.
"""

import tkinter as tk
from tkinter import ttk

from kernel.memoria.paginacion import (
    MemoriaPaginada, fragmentacion_interna, paginas_necesarias)
from ui.estilos import COLOR_FONDO, COLOR_MADERA, COLOR_ROJO, COLOR_TEXTO, COLOR_VERDE

MARCOS_INICIAL = 8
PAGINA_INICIAL = 4
MAX_MARCOS = 12
MAX_PAGINA = 16
MAX_LIBRO = 100
ANCHO_MESA = 640

# Mesa de ejemplo: cuatro libros (código, tamaño); luego se retiran el 1 y el 3
# para que los marcos libres queden separados y se note que la paginación
# no necesita espacio contiguo.
LIBROS_EJEMPLO = [(1, 8), (2, 6), (3, 8), (4, 4)]
RETIRADOS_EJEMPLO = [1, 3]


class VentanaPaginacion(tk.Toplevel):
    def __init__(self, padre, color_libro):
        super().__init__(padre)
        self.title("Paginación: tabla de páginas")
        self.configure(bg=COLOR_FONDO)
        self.resizable(False, False)
        self._color_libro = color_libro
        self.memoria = None
        self._siguiente_codigo = 1

        self.var_marcos = tk.StringVar(value=str(MARCOS_INICIAL))
        self.var_pagina = tk.StringVar(value=str(PAGINA_INICIAL))
        self.var_tamano = tk.StringVar(value="16")
        self.var_retirar = tk.StringVar()
        self.var_libro_dir = tk.StringVar(value="2")
        self.var_direccion = tk.StringVar(value="5")

        self._construir()
        self._reiniciar(mensaje_ejemplo=True)

    # ---------- Construcción de la pantalla ----------

    def _construir(self):
        # Configuración de la mesa
        config = ttk.LabelFrame(self, text="Mesa dividida en marcos")
        config.pack(fill="x", padx=12, pady=(12, 6))
        ttk.Label(config, text="Marcos").grid(row=0, column=0, padx=(10, 2), pady=6)
        ttk.Spinbox(config, from_=1, to=MAX_MARCOS, width=4,
                    textvariable=self.var_marcos).grid(row=0, column=1)
        ttk.Label(config, text="Tamaño de página").grid(row=0, column=2, padx=(14, 2))
        ttk.Spinbox(config, from_=1, to=MAX_PAGINA, width=4,
                    textvariable=self.var_pagina).grid(row=0, column=3)
        ttk.Button(config, text="Reiniciar mesa", style="Accion.TButton",
                   command=self._reiniciar).grid(row=0, column=4, padx=14, pady=6)

        self.canvas = tk.Canvas(self, width=ANCHO_MESA, height=100, bg=COLOR_FONDO,
                                highlightthickness=0)
        self.canvas.pack(padx=12, pady=4)

        # Cargar y retirar libros
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=12, pady=4)
        ttk.Label(ctrl, text="Tamaño del libro").grid(row=0, column=0)
        ttk.Spinbox(ctrl, from_=1, to=MAX_LIBRO, width=5,
                    textvariable=self.var_tamano).grid(row=0, column=1, padx=4)
        ttk.Button(ctrl, text="Cargar libro", style="Accion.TButton",
                   command=self._cargar).grid(row=0, column=2, padx=(4, 18))
        ttk.Label(ctrl, text="Retirar libro Nº").grid(row=0, column=3)
        ttk.Entry(ctrl, textvariable=self.var_retirar, width=5).grid(row=0, column=4, padx=4)
        ttk.Button(ctrl, text="Retirar", style="Accion.TButton",
                   command=self._retirar).grid(row=0, column=5, padx=4)

        self.lbl_estado = ttk.Label(self, font=("Arial", 9), wraplength=ANCHO_MESA)
        self.lbl_estado.pack(anchor="w", padx=14, pady=2)

        # Tabla de páginas y resumen de fragmentación
        medio = ttk.Frame(self)
        medio.pack(fill="x", padx=12, pady=4)
        medio.columnconfigure(1, weight=1)

        tabla = ttk.LabelFrame(medio, text="Tabla de páginas")
        tabla.grid(row=0, column=0, sticky="ns")
        self.tabla = ttk.Treeview(tabla, columns=("libro", "pagina", "marco"),
                                  show="headings", height=7)
        for col, texto in [("libro", "Libro"), ("pagina", "Página"), ("marco", "Marco")]:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=80, anchor="center")
        barra = ttk.Scrollbar(tabla, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", padx=(5, 0), pady=5)
        barra.pack(side="left", fill="y", padx=(0, 5), pady=5)

        frag = ttk.LabelFrame(medio, text="Fragmentación")
        frag.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.lbl_frag = ttk.Label(frag, font=("Arial", 9), justify="left", wraplength=360)
        self.lbl_frag.pack(anchor="w", padx=8, pady=6)

        # Traducción de direcciones
        trad = ttk.LabelFrame(self, text="Traducir una dirección lógica")
        trad.pack(fill="x", padx=12, pady=(6, 12))
        fila = ttk.Frame(trad)
        fila.pack(fill="x", padx=8, pady=(6, 2))
        ttk.Label(fila, text="Libro Nº").grid(row=0, column=0)
        ttk.Entry(fila, textvariable=self.var_libro_dir, width=5).grid(row=0, column=1, padx=4)
        ttk.Label(fila, text="Dirección lógica").grid(row=0, column=2, padx=(12, 2))
        ttk.Entry(fila, textvariable=self.var_direccion, width=6).grid(row=0, column=3, padx=4)
        ttk.Button(fila, text="Traducir", style="Accion.TButton",
                   command=self._traducir).grid(row=0, column=4, padx=10)
        self.lbl_traduccion = ttk.Label(trad, font=("Arial", 10, "bold"),
                                        foreground=COLOR_VERDE, wraplength=ANCHO_MESA - 30)
        self.lbl_traduccion.pack(anchor="w", padx=10, pady=(2, 8))

    # ---------- Utilidades ----------

    def _leer_entero(self, texto, nombre, minimo=1):
        try:
            valor = int(texto.strip())
        except ValueError:
            raise ValueError(f"{nombre} debe ser un número entero")
        if valor < minimo:
            raise ValueError(f"{nombre} debe ser {'mayor que 0' if minimo == 1 else 'mayor o igual a 0'}")
        return valor

    def _mensaje(self, texto, error=False):
        self.lbl_estado.configure(text=texto,
                                  foreground=COLOR_ROJO if error else COLOR_TEXTO)

    # ---------- Operaciones ----------

    def _reiniciar(self, mensaje_ejemplo=False):
        try:
            marcos = self._leer_entero(self.var_marcos.get(), "El número de marcos")
            pagina = self._leer_entero(self.var_pagina.get(), "El tamaño de página")
            if marcos > MAX_MARCOS or pagina > MAX_PAGINA:
                raise ValueError(f"Máximo {MAX_MARCOS} marcos y páginas de {MAX_PAGINA}")
        except ValueError as error:
            self._mensaje(str(error), error=True)
            return
        self.memoria = MemoriaPaginada(marcos, pagina)
        for codigo, tamano in LIBROS_EJEMPLO:
            self.memoria.cargar(codigo, tamano)
        for codigo in RETIRADOS_EJEMPLO:
            self.memoria.retirar(codigo)
        self._siguiente_codigo = max(c for c, _ in LIBROS_EJEMPLO) + 1
        self._mensaje("Los libros 1 y 3 ya se retiraron: los marcos libres quedaron "
                      "separados. Carga el Libro 5 (tamaño 16) y mira dónde caen "
                      "sus páginas.")
        self.lbl_traduccion.configure(text="")
        self._refrescar()

    def _cargar(self):
        try:
            tamano = self._leer_entero(self.var_tamano.get(), "El tamaño del libro")
        except ValueError as error:
            self._mensaje(str(error), error=True)
            return
        codigo = self._siguiente_codigo
        resultado = self.memoria.cargar(codigo, tamano)
        if resultado is None:
            n = paginas_necesarias(tamano, self.memoria.tam_pagina)
            libres = len(self.memoria.marcos_libres())
            self._mensaje(f"El Libro {codigo} necesita {n} marcos y solo hay {libres} libres.",
                          error=True)
        else:
            self._siguiente_codigo += 1
            marcos = ", ".join(str(m) for m in resultado["tabla"].values())
            self._mensaje(f"Libro {codigo} cargado en los marcos {marcos}.")
        self._refrescar()

    def _retirar(self):
        try:
            codigo = self._leer_entero(self.var_retirar.get(), "El número de libro")
        except ValueError as error:
            self._mensaje(str(error), error=True)
            return
        if self.memoria.retirar(codigo):
            self._mensaje(f"Libro {codigo} retirado: sus marcos quedaron libres.")
        else:
            self._mensaje(f"El Libro {codigo} no está en la mesa.", error=True)
        self._refrescar()

    def _traducir(self):
        try:
            codigo = self._leer_entero(self.var_libro_dir.get(), "El número de libro")
            direccion = self._leer_entero(self.var_direccion.get(),
                                          "La dirección", minimo=0)
            t = self.memoria.traducir(codigo, direccion)
        except ValueError as error:
            self.lbl_traduccion.configure(text=str(error), foreground=COLOR_ROJO)
            return
        tam = self.memoria.tam_pagina
        self.lbl_traduccion.configure(
            foreground=COLOR_VERDE,
            text=(f"Dirección {t['direccion_logica']} = página {t['pagina']}, "
                  f"desplazamiento {t['desplazamiento']}  →  la tabla dice marco "
                  f"{t['marco']}  →  física = {t['marco']}×{tam} + "
                  f"{t['desplazamiento']} = {t['direccion_fisica']}"))

    # ---------- Dibujo ----------

    def _refrescar(self):
        self._dibujar_marcos()
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        libros = self.memoria.libros_cargados()
        for codigo in libros:
            for pagina, marco in self.memoria.tabla_de(codigo).items():
                self.tabla.insert("", "end", values=(f"Libro {codigo}", pagina, marco))

        tam = self.memoria.tam_pagina
        lineas = []
        for codigo, tamano in libros.items():
            n = paginas_necesarias(tamano, tam)
            sobra = fragmentacion_interna(tamano, tam)
            palabra = "página" if n == 1 else "páginas"
            lineas.append(f"Libro {codigo}: tamaño {tamano} → {n} {palabra}, sobran {sobra}")
        if not lineas:
            lineas.append("No hay libros en la mesa.")
        libres = len(self.memoria.marcos_libres())
        lineas.append(f"Interna (desperdicio en la última página): "
                      f"{self.memoria.desperdicio_total()}")
        lineas.append(f"Externa: 0, cualquier marco libre sirve ({libres} libres "
                      f"de {self.memoria.num_marcos})")
        self.lbl_frag.configure(text="\n".join(lineas))

    def _dibujar_marcos(self):
        c = self.canvas
        c.delete("all")
        n = self.memoria.num_marcos
        celda = ANCHO_MESA / n
        for i, ocupante in enumerate(self.memoria.estado_marcos()):
            x0, x1 = i * celda + 3, (i + 1) * celda - 3
            if ocupante is None:
                c.create_rectangle(x0, 4, x1, 68, fill=COLOR_FONDO, outline=COLOR_MADERA)
                c.create_text((x0 + x1) / 2, 36, text="libre", fill=COLOR_TEXTO,
                              font=("Arial", 9))
            else:
                libro, pagina = ocupante
                c.create_rectangle(x0, 4, x1, 68, fill=self._color_libro(libro),
                                   outline=COLOR_TEXTO, width=2)
                c.create_text((x0 + x1) / 2, 36, text=f"Libro {libro}\npág {pagina}",
                              fill="white", font=("Arial", 9, "bold"), justify="center")
            c.create_text((x0 + x1) / 2, 84, text=f"Marco {i}", fill=COLOR_TEXTO,
                          font=("Arial", 8))