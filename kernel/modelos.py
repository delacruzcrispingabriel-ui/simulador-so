"""Modelos compartidos por los tres módulos del simulador.

Usuario: persona que llega a la biblioteca (proceso en el Módulo 1,
         lector o escritor en el Módulo 2).
Libro:   recurso de la biblioteca (recurso compartido en el Módulo 2,
         página en el Módulo 3).
"""

from dataclasses import dataclass

# Prioridad por tipo de usuario. Convención: 1 es la prioridad MÁS ALTA.
PRIORIDAD_POR_TIPO = {
    "Docente": 1,
    "Discapacidad": 1,
    "Estudiante": 2,
}


@dataclass
class Usuario:
    nombre: str
    tipo: str          # "Docente", "Estudiante" o "Discapacidad"
    llegada: int       # minuto en que entra a la cola
    duracion: int      # minutos que dura su trámite (burst)
    prioridad: int = 0  # si queda en 0, se calcula según el tipo

    def __post_init__(self):
        if self.tipo not in PRIORIDAD_POR_TIPO:
            raise ValueError(f"Tipo de usuario no válido: {self.tipo}")
        if self.duracion <= 0:
            raise ValueError("La duración debe ser mayor que 0")
        if self.llegada < 0:
            raise ValueError("La llegada no puede ser negativa")
        if self.prioridad == 0:
            self.prioridad = PRIORIDAD_POR_TIPO[self.tipo]


@dataclass
class Libro:
    codigo: int
    titulo: str
    ejemplares: int = 1

    def __post_init__(self):
        if self.ejemplares < 0:
            raise ValueError("Los ejemplares no pueden ser negativos")