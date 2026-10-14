"""Catálogo de la biblioteca: el recurso compartido del Módulo 2.

Aquí vive el libro con sus ejemplares y el registro de lo que pasó.
Este commit solo tiene el préstamo SIN protección; el préstamo con
mutex se agrega en el siguiente.
"""

import time

# Lo que tarda el trámite de préstamo (segundos). Es la ventana en la que
# otro hilo puede colarse entre "revisar" y "actuar".
PAUSA_TRAMITE = 0.01


class Catalogo:
    def __init__(self, libro):
        self.libro = libro
        self.registro = []  # mensajes en el orden en que ocurrieron

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