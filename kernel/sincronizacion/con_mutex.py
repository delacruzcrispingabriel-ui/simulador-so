"""Módulo 2 CON protección.

Dos demos:
1. ejecutar_con_mutex: el mismo préstamo de la demo anterior, pero con
   candado. Ya no hay condición de carrera.
2. ejecutar_lectores_escritores: el problema clásico de lectores-escritores
   sobre el catálogo, con un semáforo para las computadoras de la sala.

Orden de adquisición (evita el interbloqueo): todos toman PRIMERO una
computadora y DESPUÉS el acceso al catálogo. Como nadie pide los recursos
en orden inverso, no puede formarse un ciclo de espera.
"""

import threading
import time

from kernel.modelos import Libro
from kernel.sincronizacion.catalogo import Catalogo
from kernel.sincronizacion.sin_proteccion import NOMBRES

NUM_PCS = 3
TIEMPO_LECTURA = 0.05
TIEMPO_ESCRITURA = 0.05

# (nombre, rol) de la demo por defecto: 4 lectores y 2 escritores para 3 PCs
USUARIOS_DEMO = [
    ("Ana", "Lector"), ("Juan", "Lector"), ("Maria", "Escritor"),
    ("Pedro", "Escritor"), ("Luis", "Lector"), ("Rosa", "Lector"),
]


# ---------- 1. Préstamo con mutex ----------

def _usuario(catalogo, nombre, resultados):
    resultados.append(catalogo.prestar_con_mutex(nombre))


def ejecutar_con_mutex(ejemplares=1, usuarios=5):
    """Igual que ejecutar_sin_proteccion, pero con candado en el préstamo."""
    if usuarios > len(NOMBRES):
        raise ValueError(f"Máximo {len(NOMBRES)} usuarios")

    libro = Libro(1, "Sistemas Operativos Modernos", ejemplares)
    catalogo = Catalogo(libro)
    resultados = []

    hilos = [threading.Thread(target=_usuario, args=(catalogo, nombre, resultados))
             for nombre in NOMBRES[:usuarios]]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    prestamos = sum(resultados)
    return {
        "ejemplares_iniciales": ejemplares,
        "prestamos": prestamos,
        "ejemplares_finales": libro.ejemplares,
        "condicion_carrera": prestamos > ejemplares,
        "registro": catalogo.registro,
    }


# ---------- 2. Lectores-escritores con semáforo de computadoras ----------

class SalaCatalogo:
    """La sala con sus computadoras y el catálogo compartido.

    Lectores: varios pueden consultar a la vez.
    Escritores: actualizan el catálogo de a uno y sin lectores presentes.
    Computadoras: solo hay `num_pcs`; el resto espera (semáforo).
    """

    def __init__(self, num_pcs=NUM_PCS):
        self.version = 1                      # el "dato" del catálogo
        self.pcs = threading.Semaphore(num_pcs)
        self._pcs_libres = list(range(1, num_pcs + 1))
        self._candado_pcs = threading.Lock()  # protege la lista de PCs libres
        self.recurso = threading.Lock()       # acceso al catálogo
        self.candado_lectores = threading.Lock()
        self.lectores_activos = 0             # lectores registrados
        self.leyendo = 0                      # lectores con acceso concedido
        self.escribiendo = False
        # Evidencia para verificar la ejecución
        self.pcs_en_uso = 0
        self.max_pcs_en_uso = 0
        self.max_lectores = 0
        self.violaciones = 0
        self.registro = []
        self._candado_registro = threading.Lock()
        self._inicio = time.monotonic()

    # --- utilidades ---

    def anotar(self, mensaje):
        with self._candado_registro:
            t = time.monotonic() - self._inicio
            self.registro.append(f"[{t:5.2f}s] {mensaje}")

    def _violacion(self, texto):
        with self._candado_registro:
            self.violaciones += 1
        self.anotar(f"VIOLACIÓN: {texto}")

    def _tomar_pc(self):
        self.pcs.acquire()  # si las 3 están ocupadas, el hilo espera aquí
        with self._candado_pcs:
            numero = self._pcs_libres.pop(0)
            self.pcs_en_uso += 1
            self.max_pcs_en_uso = max(self.max_pcs_en_uso, self.pcs_en_uso)
        return numero

    def _soltar_pc(self, numero):
        with self._candado_pcs:
            self._pcs_libres.append(numero)
            self._pcs_libres.sort()
            self.pcs_en_uso -= 1
        self.pcs.release()

    # --- roles ---

    def leer(self, nombre):
        self.anotar(f"{nombre} (Lector) pide una computadora")
        pc = self._tomar_pc()
        self.anotar(f"{nombre} (Lector) usa la PC {pc}")

        with self.candado_lectores:           # entrada: el primero cierra la puerta
            self.lectores_activos += 1
            if self.lectores_activos == 1:
                self.recurso.acquire()        # espera si hay un escritor
            self.leyendo += 1
            self.max_lectores = max(self.max_lectores, self.leyendo)

        self.anotar(f"{nombre} (Lector) consulta el catálogo")
        if self.escribiendo:
            self._violacion(f"{nombre} lee mientras alguien escribe")
        time.sleep(TIEMPO_LECTURA)
        if self.escribiendo:
            self._violacion(f"{nombre} lee mientras alguien escribe")

        with self.candado_lectores:           # salida: el último abre la puerta
            self.leyendo -= 1
            self.lectores_activos -= 1
            if self.lectores_activos == 0:
                self.recurso.release()

        self.anotar(f"{nombre} (Lector) termina y libera la PC {pc}")
        self._soltar_pc(pc)

    def escribir(self, nombre):
        self.anotar(f"{nombre} (Escritor) pide una computadora")
        pc = self._tomar_pc()
        self.anotar(f"{nombre} (Escritor) usa la PC {pc} y espera acceso exclusivo")

        self.recurso.acquire()                # espera a que no haya nadie más
        self.anotar(f"{nombre} (Escritor) actualiza el catálogo")
        if self.escribiendo or self.leyendo > 0:
            self._violacion(f"{nombre} escribe con otros dentro del catálogo")
        self.escribiendo = True
        leido = self.version                  # leer-modificar-escribir: si dos
        time.sleep(TIEMPO_ESCRITURA)          # escritores coincidieran, uno
        self.version = leido + 1              # pisaría el cambio del otro
        self.escribiendo = False
        self.recurso.release()

        self.anotar(f"{nombre} (Escritor) termina y libera la PC {pc}")
        self._soltar_pc(pc)


def ejecutar_lectores_escritores(usuarios=None, num_pcs=NUM_PCS):
    """Lanza un hilo por usuario y devuelve la evidencia de la ejecución."""
    usuarios = usuarios or USUARIOS_DEMO
    for _, rol in usuarios:
        if rol not in ("Lector", "Escritor"):
            raise ValueError(f"Rol no válido: {rol}")

    sala = SalaCatalogo(num_pcs)
    hilos = []
    for nombre, rol in usuarios:
        objetivo = sala.leer if rol == "Lector" else sala.escribir
        hilos.append(threading.Thread(target=objetivo, args=(nombre,)))
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    escrituras = sum(1 for _, rol in usuarios if rol == "Escritor")
    return {
        "version_inicial": 1,
        "version_final": sala.version,
        "escrituras": escrituras,
        "max_pcs_en_uso": sala.max_pcs_en_uso,
        "max_lectores_simultaneos": sala.max_lectores,
        "violaciones": sala.violaciones,
        # Correcto = sin violaciones, sin cambios perdidos y sin pasar de 3 PCs
        "correcto": (sala.violaciones == 0
                     and sala.version == 1 + escrituras
                     and sala.max_pcs_en_uso <= num_pcs),
        "registro": sala.registro,
    }