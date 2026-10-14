"""Catálogo de la biblioteca: el recurso compartido del Módulo 2.

Aquí vive el libro con sus ejemplares y el registro de lo que pasó.
Tiene dos versiones del préstamo para poder compararlas:
- prestar_sin_proteccion: revisa y descuenta sin candado (condición de carrera).
- prestar_con_mutex: el mismo trámite, pero revisar y descontar ocurren
  dentro de una sección crítica protegida por un Lock.
"""

import threading
import time

# Lo que tarda el trámite de préstamo (segundos). Es la ventana en la que
# otro hilo puede colarse entre "revisar" y "actuar".
PAUSA_TRAMITE = 0.01


class Catalogo:
    def __init__(self, libro):
        self.libro = libro
        self.registro = []  # mensajes en el orden en que ocurrieron
        self.candado = threading.Lock()  # mutex del préstamo con protección

    def anotar(self, mensaje):
        self.registro.append(mensaje)

    def prestar_sin_proteccion(self, usuario):
        """Préstamo sin candado: revisa, espera y recién entonces descuenta.

        Entre la revisión y el descuento otro usuario puede hacer lo mismo,
        y entonces dos o más se llevan el mismo ejemplar.
        """
        if self.libro.ejemplares > 0:            # 1. revisa
            time.sleep(PAUSA_TRAMITE)            # 2. el trámite tarda
            self.libro.ejemplares -= 1           # 3. actúa
            self.anotar(f"{usuario} se llevó el libro "
                        f"(quedan {self.libro.ejemplares})")
            return True
        self.anotar(f"{usuario} no encontró ejemplares")
        return False

    def prestar_con_mutex(self, usuario):
        """Mismo trámite, pero revisar y descontar son una sola operación
        indivisible: ningún otro hilo entra a la sección crítica a la vez."""
        with self.candado:
            if self.libro.ejemplares > 0:        # 1. revisa
                time.sleep(PAUSA_TRAMITE)        # 2. el trámite tarda
                self.libro.ejemplares -= 1       # 3. actúa
                self.anotar(f"{usuario} se llevó el libro "
                            f"(quedan {self.libro.ejemplares})")
                return True
            self.anotar(f"{usuario} no encontró ejemplares")
            return False