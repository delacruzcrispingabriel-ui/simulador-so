"""Algoritmos de planificación del Mostrador (Módulo 1).

Cada algoritmo recibe una lista de Usuario y devuelve la línea de tiempo:
una lista de tramos (nombre, inicio, fin) en el orden en que se atendió.
No modifica los usuarios recibidos.
"""


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