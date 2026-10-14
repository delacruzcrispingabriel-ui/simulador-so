"""Anomalía de Belady (Módulo 3).

Lo normal es que con más marcos (más espacio en la mesa de acceso rápido)
haya menos fallos. FIFO rompe esa regla con ciertas secuencias: al darle más
memoria, falla MÁS. LRU y Óptimo nunca lo hacen.

Esta demo corre la secuencia clásica con distintas cantidades de marcos y
señala en cuáles aumentaron los fallos.
"""

from kernel.memoria.reemplazo import FIFO, LRU, simular

# Secuencia clásica: FIFO da 9 fallos con 3 marcos y 10 con 4.
SECUENCIA_BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def fallos_por_marcos(algoritmo, secuencia, max_marcos):
    """Fallos del algoritmo con 1, 2, ..., max_marcos marcos.

    Devuelve una lista de (marcos, fallos).
    """
    if max_marcos < 1:
        raise ValueError("max_marcos debe ser al menos 1")
    return [(m, simular(algoritmo, secuencia, m)["fallos"])
            for m in range(1, max_marcos + 1)]


def demostrar_belady(secuencia=None, max_marcos=6):
    """Compara FIFO y LRU al ir aumentando los marcos.

    Devuelve un diccionario:
      secuencia   -> la secuencia usada
      fifo, lru   -> listas de (marcos, fallos)
      anomalias   -> lista de (marcos_antes, fallos_antes, marcos_despues,
                     fallos_despues) donde FIFO empeoró al recibir más marcos
      hay_anomalia-> True si FIFO tuvo al menos una
      lru_anomalias -> lo mismo para LRU (debe quedar vacía)
    """
    secuencia = list(secuencia) if secuencia is not None else list(SECUENCIA_BELADY)
    fifo = fallos_por_marcos(FIFO, secuencia, max_marcos)
    lru = fallos_por_marcos(LRU, secuencia, max_marcos)

    return {
        "secuencia": secuencia,
        "fifo": fifo,
        "lru": lru,
        "anomalias": _anomalias(fifo),
        "hay_anomalia": bool(_anomalias(fifo)),
        "lru_anomalias": _anomalias(lru),
    }


def _anomalias(serie):
    """Pares consecutivos donde más marcos produjeron más fallos."""
    return [(m1, f1, m2, f2)
            for (m1, f1), (m2, f2) in zip(serie, serie[1:])
            if f2 > f1]


def texto_anomalia(anomalia):
    """Frase lista para mostrar en la interfaz."""
    m1, f1, m2, f2 = anomalia
    return f"Con {m1} marcos: {f1} fallos. Con {m2} marcos: {f2} fallos."