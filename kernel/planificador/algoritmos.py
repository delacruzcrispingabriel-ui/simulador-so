"""Algoritmos de planificación del Mostrador (Módulo 1).

Cada algoritmo recibe una lista de Usuario y devuelve la línea de tiempo:
una lista de tramos (nombre, inicio, fin) en el orden en que se atendió.
No modifica los usuarios recibidos.
"""

from collections import deque

def fcfs(usuarios):
    """First Come, First Served: se atiende por orden de llegada."""
    linea = []
    reloj = 0
    # sorted es estable: ante una llegada igual, respeta el orden original
    for u in sorted(usuarios, key=lambda u: u.llegada):
        inicio = max(reloj, u.llegada)  # si el mostrador está vacío, espera
        fin = inicio + u.duracion
        linea.append((u.nombre, inicio, fin))
        reloj = fin
    return linea


def sjf(usuarios):
    """Shortest Job First (sin interrupción): entre los usuarios que ya
    llegaron, se atiende primero al de trámite más corto."""
    pendientes = sorted(usuarios, key=lambda u: u.llegada)
    linea = []
    reloj = 0
    while pendientes:
        listos = [u for u in pendientes if u.llegada <= reloj]
        if not listos:
            # Nadie en la cola: el reloj salta a la próxima llegada
            reloj = pendientes[0].llegada
            continue
        elegido = min(listos, key=lambda u: u.duracion)
        pendientes.remove(elegido)
        inicio = reloj
        fin = inicio + elegido.duracion
        linea.append((elegido.nombre, inicio, fin))
        reloj = fin
    return linea



def round_robin(usuarios, quantum):
    """Round Robin: cada usuario recibe como máximo `quantum` minutos por turno
    y, si no termina, vuelve al final de la cola.

    Convención: los que llegan durante un turno entran a la cola ANTES que el
    usuario interrumpido. Un mismo usuario puede aparecer en varios tramos.
    """
    if quantum <= 0:
        raise ValueError("El quantum debe ser mayor que 0")

    por_llegar = sorted(usuarios, key=lambda u: u.llegada)
    restante = {u.nombre: u.duracion for u in usuarios}
    cola = deque()
    linea = []
    reloj = 0

    while por_llegar or cola:
        # Pasan a la cola los que ya llegaron
        while por_llegar and por_llegar[0].llegada <= reloj:
            cola.append(por_llegar.pop(0))
        if not cola:
            # Mostrador vacío: el reloj salta a la próxima llegada
            reloj = por_llegar[0].llegada
            continue

        u = cola.popleft()
        tramo = min(quantum, restante[u.nombre])
        inicio = reloj
        reloj += tramo
        restante[u.nombre] -= tramo
        linea.append((u.nombre, inicio, reloj))

        # Los que llegaron durante este turno entran antes que el interrumpido
        while por_llegar and por_llegar[0].llegada <= reloj:
            cola.append(por_llegar.pop(0))
        if restante[u.nombre] > 0:
            cola.append(u)
    return linea


def prioridad(usuarios):
    """Por prioridad (sin interrupción): entre los que ya llegaron se atiende
    al de prioridad más alta (1 es la más alta). Si empatan, al que llegó antes."""
    pendientes = sorted(usuarios, key=lambda u: u.llegada)
    linea = []
    reloj = 0
    while pendientes:
        listos = [u for u in pendientes if u.llegada <= reloj]
        if not listos:
            reloj = pendientes[0].llegada
            continue
        elegido = min(listos, key=lambda u: (u.prioridad, u.llegada))
        pendientes.remove(elegido)
        inicio = reloj
        fin = inicio + elegido.duracion
        linea.append((elegido.nombre, inicio, fin))
        reloj = fin
    return linea