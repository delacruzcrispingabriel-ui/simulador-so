"""Estados de un proceso y cambios de contexto (Módulo 1).

Un proceso (el Usuario de la biblioteca) pasa por estos estados:

  Nuevo      -> acaba de llegar a la biblioteca.
  Listo      -> está en la cola, esperando que lo atiendan.
  Ejecutando -> el bibliotecario (CPU) lo está atendiendo.
  Esperando  -> detenido hasta que termine algo externo (ej. una E/S).
  Terminado  -> ya terminó su trámite.

Cambio de contexto: cada vez que el bibliotecario deja a un usuario y pasa
a otro, guarda dónde iba (como un marcador) y retoma el del otro.
"""

NUEVO = "Nuevo"
LISTO = "Listo"
EJECUTANDO = "Ejecutando"
ESPERANDO = "Esperando"
TERMINADO = "Terminado"

# Transiciones permitidas: estado actual -> estados a los que puede pasar
TRANSICIONES = {
    NUEVO: {LISTO},
    LISTO: {EJECUTANDO},
    EJECUTANDO: {LISTO, ESPERANDO, TERMINADO},
    ESPERANDO: {LISTO},
    TERMINADO: set(),
}


class ProcesoSim:
    """Un proceso con su estado actual y su historial de cambios."""

    def __init__(self, nombre, tiempo=0):
        self.nombre = nombre
        self.estado = NUEVO
        self.historial = [(tiempo, NUEVO)]   # (minuto, estado)

    def cambiar(self, nuevo, tiempo):
        if nuevo not in TRANSICIONES[self.estado]:
            raise ValueError(
                f"{self.nombre}: no se puede pasar de {self.estado} a {nuevo}")
        self.estado = nuevo
        self.historial.append((tiempo, nuevo))


def historial_estados(usuarios, linea):
    """Estados de cada usuario a partir de la línea de tiempo de un algoritmo.

    `linea` es la lista de tramos (nombre, inicio, fin) que devuelven los
    algoritmos del planificador. Devuelve {nombre: [(minuto, estado), ...]}.
    """
    tramos = {}
    for nombre, inicio, fin in linea:
        tramos.setdefault(nombre, []).append((inicio, fin))

    resultado = {}
    for u in usuarios:
        proceso = ProcesoSim(u.nombre, u.llegada)
        proceso.cambiar(LISTO, u.llegada)
        lista = tramos[u.nombre]
        for i, (inicio, fin) in enumerate(lista):
            proceso.cambiar(EJECUTANDO, inicio)
            ultimo = i == len(lista) - 1
            proceso.cambiar(TERMINADO if ultimo else LISTO, fin)
        resultado[u.nombre] = proceso.historial
    return resultado


def cambios_de_contexto(linea):
    """Cuántas veces el bibliotecario pasó de un usuario a otro distinto."""
    return sum(1 for anterior, actual in zip(linea, linea[1:])
               if anterior[0] != actual[0])