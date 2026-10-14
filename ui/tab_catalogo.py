"""Pestaña 2: Catálogo (sincronización).

Corre una simulación del kernel y luego la reproduce evento por evento:
así se ve quién ocupa cada computadora, en qué estado está cada hilo y
cómo cambia el contador, en vez de ver solo el resultado final.
"""

import re
import tkinter as tk
from tkinter import ttk

from kernel.sincronizacion.sin_proteccion import NOMBRES, ejecutar_sin_proteccion
from kernel.sincronizacion.con_mutex import (
    NUM_PCS, USUARIOS_DEMO, ejecutar_con_mutex, ejecutar_lectores_escritores)
from ui.estilos import (COLOR_FONDO, COLOR_MADERA, COLOR_MADERA_CLARA,
                        COLOR_ROJO, COLOR_TEXTO, COLOR_VERDE)

PASO_MS = 350                 # pausa entre eventos al reproducir la simulación
USUARIOS_PRESTAMO = 5
EJEMPLARES_INICIALES = 1
TITULO_LIBRO = "Sistemas Operativos Modernos"

# Formato de los mensajes del kernel (kernel/sincronizacion). Esta pestaña
# los interpreta con estos patrones: si cambias un mensaje allá, cámbialo aquí.
PATRON_SALA = re.compile(r"^\[\s*[\d.]+s\] (\S+) \((Lector|Escritor)\) (.+)$")
PATRON_PRESTAMO = re.compile(
    r"^(\S+) (?:se llevó el libro \(quedan (-?\d+)\)|no encontró ejemplares)$")
PATRON_PC = re.compile(r"PC (\d+)")


class TabCatalogo(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self._modo = None            # "sin", "con" o "rw"
        self._pendientes = []        # eventos por reproducir
        self._resultado = None
        self._filas = {}             # nombre -> fila de la tabla
        self._version = 1
        self._ejemplares = EJEMPLARES_INICIALES

        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=5)
        self.rowconfigure(0, weight=1)
        self._construir_izquierda()
        self._construir_derecha()

        for i in range(1, NUM_PCS + 1):
            self._poner_pc(i, None)
        self._actualizar_contador()
        self.lbl_carrera.configure(text="Condición de carrera: (ejecuta una simulación)")

    # ---------- Construcción de la pantalla ----------

    def _construir_izquierda(self):
        izq = ttk.Frame(self)
        izq.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        izq.columnconfigure(0, weight=1)
        izq.rowconfigure(1, weight=1)

        recurso = ttk.LabelFrame(izq, text="Recurso compartido")
        recurso.grid(row=0, column=0, sticky="ew")
        libro = tk.Canvas(recurso, width=120, height=110, bg=COLOR_FONDO,
                          highlightthickness=0)
        libro.pack(pady=(8, 0))
        libro.create_rectangle(15, 8, 105, 102, fill="#34495E",
                               outline=COLOR_TEXTO, width=2)
        libro.create_rectangle(15, 8, 25, 102, fill=COLOR_MADERA, outline=COLOR_TEXTO)
        libro.create_text(67, 55, text=TITULO_LIBRO, fill="white", width=70,
                          justify="center", font=("Arial", 8, "bold"))
        self.lbl_contador = ttk.Label(recurso, font=("Arial", 14, "bold"))
        self.lbl_contador.pack(pady=(4, 8))

        pcs = ttk.LabelFrame(izq, text="Computadoras")
        pcs.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        pcs.rowconfigure(0, weight=1)
        self.cajas_pc = []
        for i in range(NUM_PCS):
            pcs.columnconfigure(i, weight=1, uniform="pc")
            caja = tk.Label(pcs, relief="solid", bd=1, wraplength=95,
                            justify="center", font=("Arial", 9), fg=COLOR_TEXTO)
            caja.grid(row=0, column=i, sticky="nsew", padx=4, pady=8)
            self.cajas_pc.append(caja)

    def _construir_derecha(self):
        der = ttk.Frame(self)
        der.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        der.columnconfigure(0, weight=1)
        der.rowconfigure(2, weight=1)

        hilos = ttk.LabelFrame(der, text="Hilos activos")
        hilos.grid(row=0, column=0, sticky="ew")
        self.tabla = ttk.Treeview(hilos, columns=("usuario", "rol", "estado"),
                                  show="headings", height=6)
        for col, texto, ancho in [("usuario", "Usuario", 80), ("rol", "Rol", 90),
                                  ("estado", "Estado", 170)]:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.pack(fill="x", padx=5, pady=5)

        botones = ttk.Frame(der)
        botones.grid(row=1, column=0, sticky="ew", pady=8)
        botones.columnconfigure((0, 1), weight=1)
        self.btn_sin = ttk.Button(botones, text="Ejecutar SIN protección",
                                  style="Peligro.TButton",
                                  command=lambda: self._ejecutar("sin"))
        self.btn_con = ttk.Button(botones, text="Ejecutar CON mutex",
                                  style="Accion.TButton",
                                  command=lambda: self._ejecutar("con"))
        self.btn_rw = ttk.Button(botones, text="Lectores-escritores (3 PCs)",
                                 style="Accion.TButton",
                                 command=lambda: self._ejecutar("rw"))
        self.btn_sin.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        self.btn_con.grid(row=0, column=1, sticky="ew", padx=(3, 0))
        self.btn_rw.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        registro = ttk.LabelFrame(der, text="Registro de eventos")
        registro.grid(row=2, column=0, sticky="nsew")
        registro.rowconfigure(0, weight=1)
        registro.columnconfigure(0, weight=1)
        self.txt = tk.Text(registro, height=5, wrap="word", state="disabled",
                           bg=COLOR_FONDO, fg=COLOR_TEXTO, font=("Arial", 9),
                           relief="flat")
        barra = ttk.Scrollbar(registro, command=self.txt.yview)
        self.txt.configure(yscrollcommand=barra.set)
        self.txt.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        barra.grid(row=0, column=1, sticky="ns", pady=5)
        self.lbl_carrera = ttk.Label(registro, font=("Arial", 9, "bold"))
        self.lbl_carrera.grid(row=1, column=0, columnspan=2, sticky="w",
                              padx=5, pady=(0, 5))

    # ---------- Piezas de la pantalla ----------

    def _actualizar_contador(self):
        if self._modo == "rw":
            self.lbl_contador.configure(text=f"Versión del catálogo: {self._version}")
        else:
            self.lbl_contador.configure(
                text=f"Ejemplares disponibles: {self._ejemplares}")

    def _poner_pc(self, numero, ocupante):
        caja = self.cajas_pc[numero - 1]
        if ocupante is None:
            caja.configure(text=f"PC {numero}:\nLibre", bg=COLOR_FONDO)
        else:
            caja.configure(text=f"PC {numero}: Ocupada\n({ocupante})",
                           bg=COLOR_MADERA_CLARA)

    def _cargar_tabla(self, usuarios):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        self._filas = {}
        for nombre, rol in usuarios:
            self._filas[nombre] = self.tabla.insert(
                "", "end", values=(nombre, rol, "Esperando"))

    def _estado(self, nombre, texto):
        if nombre in self._filas:
            self.tabla.set(self._filas[nombre], "estado", texto)

    def _limpiar_registro(self):
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.configure(state="disabled")

    def _agregar_registro(self, linea):
        self.txt.configure(state="normal")
        self.txt.insert("end", linea + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _botones(self, estado):
        for boton in (self.btn_sin, self.btn_con, self.btn_rw):
            boton.configure(state=estado)

    # ---------- Simulación ----------

    def _ejecutar(self, modo):
        self._botones("disabled")
        self._modo = modo
        self._version = 1
        self._ejemplares = EJEMPLARES_INICIALES
        self._limpiar_registro()
        self.lbl_carrera.configure(text="Condición de carrera: simulando...",
                                   foreground=COLOR_TEXTO)
        for i in range(1, NUM_PCS + 1):
            self._poner_pc(i, None)

        # El kernel crea sus propios hilos y espera a que terminen (< 1 s),
        # así que se puede llamar desde aquí sin congelar la ventana.
        if modo == "rw":
            resultado = ejecutar_lectores_escritores()
            usuarios = USUARIOS_DEMO
        else:
            ejecutar = ejecutar_sin_proteccion if modo == "sin" else ejecutar_con_mutex
            resultado = ejecutar(EJEMPLARES_INICIALES, USUARIOS_PRESTAMO)
            usuarios = [(n, "Prestatario") for n in NOMBRES[:USUARIOS_PRESTAMO]]

        self._resultado = resultado
        self._pendientes = list(resultado["registro"])
        self._cargar_tabla(usuarios)
        self._actualizar_contador()
        self.after(PASO_MS, self._paso)

    def _paso(self):
        """Reproduce un evento del registro y programa el siguiente."""
        if not self._pendientes:
            self._terminar()
            return
        linea = self._pendientes.pop(0)
        self._agregar_registro(linea)
        if self._modo == "rw":
            self._aplicar_sala(linea)
        else:
            self._aplicar_prestamo(linea)
        self.after(PASO_MS, self._paso)

    def _aplicar_prestamo(self, linea):
        m = PATRON_PRESTAMO.match(linea)
        if not m:
            return
        nombre, quedan = m.groups()
        if quedan is not None:
            self._ejemplares = int(quedan)
            self._estado(nombre, "Se llevó el libro")
        else:
            self._estado(nombre, "Sin ejemplares")
        self._actualizar_contador()

    def _aplicar_sala(self, linea):
        m = PATRON_SALA.match(linea)
        if not m:
            return
        nombre, rol, accion = m.groups()
        pc = PATRON_PC.search(accion)
        numero = int(pc.group(1)) if pc else None

        if "pide una computadora" in accion:
            self._estado(nombre, "Esperando PC")
        elif "espera acceso exclusivo" in accion:
            self._poner_pc(numero, f"{nombre} - {rol}")
            self._estado(nombre, f"En PC {numero}: espera acceso")
        elif "usa la PC" in accion:
            self._poner_pc(numero, f"{nombre} - {rol}")
            self._estado(nombre, f"En PC {numero}")
        elif "consulta" in accion:
            self._estado(nombre, "Consultando")
        elif "actualiza" in accion:
            self._estado(nombre, "Actualizando")
        elif "termina" in accion:
            self._poner_pc(numero, None)
            self._estado(nombre, "Terminó")
            if rol == "Escritor":
                self._version += 1
                self._actualizar_contador()

    def _terminar(self):
        r = self._resultado
        if self._modo == "rw":
            resumen = (f"Resultado: versión final {r['version_final']} "
                       f"(esperada {1 + r['escrituras']}), máximo "
                       f"{r['max_pcs_en_uso']} PCs en uso, "
                       f"{r['violaciones']} violaciones.")
            hubo_carrera = not r["correcto"]
            self._version = r["version_final"]
        else:
            resumen = (f"Resultado: {r['prestamos']} préstamos con "
                       f"{r['ejemplares_iniciales']} ejemplar(es); "
                       f"quedan {r['ejemplares_finales']}.")
            hubo_carrera = r["condicion_carrera"]
            self._ejemplares = r["ejemplares_finales"]
        self._agregar_registro(resumen)
        self._actualizar_contador()

        if hubo_carrera:
            self.lbl_carrera.configure(text="Condición de carrera: DETECTADA",
                                       foreground=COLOR_ROJO)
        else:
            nota = ("esta vez no coincidieron; repite" if self._modo == "sin"
                    else "mutex activo")
            self.lbl_carrera.configure(
                text=f"Condición de carrera: NO DETECTADA ({nota})",
                foreground=COLOR_VERDE)
        self._botones("normal")