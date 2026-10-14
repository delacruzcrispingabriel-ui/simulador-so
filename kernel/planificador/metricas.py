"""Métricas del Mostrador (Módulo 1).

Espera    = fin - llegada - duración  (tiempo total en cola)
Respuesta = primer inicio - llegada   (cuánto tardó en empezar a ser atendido)
"""

from kernel.planificador.algoritmos import fcfs, sjf, round_robin, prioridad


def calcular_metricas(usuarios, linea):
    """Calcula espera y respuesta por usuario y sus promedios a partir de
    la línea de tiempo de un algoritmo."""
    if not usuarios:
        return {"detalle": {}, "espera_promedio": 0.0, "respuesta_promedio": 0.0}

    primer_inicio = {}
    fin = {}
    for nombre, inicio, fin_tramo in linea:
        primer_inicio.setdefault(nombre, inicio)  # solo el primer tramo
        fin[nombre] = fin_tramo                   # el último tramo es el fin

    detalle = {}
    for u in usuarios:
        detalle[u.nombre] = {
            "espera": fin[u.nombre] - u.llegada - u.duracion,
            "respuesta": primer_inicio[u.nombre] - u.llegada,
        }

    n = len(detalle)
    return {
        "detalle": detalle,
        "espera_promedio": round(sum(d["espera"] for d in detalle.values()) / n, 2),
        "respuesta_promedio": round(sum(d["respuesta"] for d in detalle.values()) / n, 2),
    }


def comparar_algoritmos(usuarios, quantum=3):
    """Corre los cuatro algoritmos con la MISMA lista de usuarios y devuelve
    un diccionario {algoritmo: {"linea": ..., "metricas": ...}}."""
    lineas = {
        "FCFS": fcfs(usuarios),
        "SJF": sjf(usuarios),
        "Round Robin": round_robin(usuarios, quantum),
        "Prioridad": prioridad(usuarios),
    }
    return {
        nombre: {"linea": linea, "metricas": calcular_metricas(usuarios, linea)}
        for nombre, linea in lineas.items()
    }