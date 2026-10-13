from collections import deque

def ejecutar_round_robin(procesos, quantum):
    cola = deque([p for p in procesos])
    tiempo_actual = 0
    historial = []

    while cola:
        p = cola.popleft()
        tiempo_ejecutado = min(p.tiempo_restante, quantum)
        p.tiempo_restante -= tiempo_ejecutado
        tiempo_actual += tiempo_ejecutado
        historial.append((p.pid, tiempo_actual))

        if p.tiempo_restante > 0:
            cola.append(p)

    return historial