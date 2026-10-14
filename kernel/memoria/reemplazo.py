"""Reemplazo de páginas (Módulo 3): FIFO, LRU y Óptimo.

La mesa de acceso rápido tiene N marcos (la RAM). Cuando piden un libro que
no está en la mesa hay un FALLO: hay que traerlo de los estantes y, si la mesa
está llena, sacar uno. Cada algoritmo decide a cuál sacar:

- FIFO:   el que lleva más tiempo en la mesa (el primero que entró).
- LRU:    el que hace más tiempo que no se usa.
- Óptimo: el que tardará más en volver a pedirse (necesita ver el futuro,
          así que sirve solo como referencia para comparar).

Todos devuelven lo mismo: los fallos totales y un paso a paso, para que la
interfaz pueda reproducir la simulación pedido por pedido.
"""

FIFO = "FIFO"
LRU = "LRU"
OPTIMO = "Óptimo"
ALGORITMOS = (FIFO, LRU, OPTIMO)


def _validar(secuencia, marcos):
    if marcos <= 0:
        raise ValueError("Los marcos deben ser mayores que 0")
    if not secuencia:
        raise ValueError("La secuencia de pedidos está vacía")


def _elegir_victima(algoritmo, ocupados, secuencia, i, orden_carga, ultimo_uso):
    """Devuelve el libro que se saca de la mesa (uno de `ocupados`)."""
    if algoritmo == FIFO:
        return min(ocupados, key=lambda p: orden_carga[p])
    if algoritmo == LRU:
        return min(ocupados, key=lambda p: ultimo_uso[p])
    # Óptimo: el que tarda más en volver a pedirse; si no vuelve, es el ideal.
    futuro = secuencia[i + 1:]

    def distancia(pagina):
        return futuro.index(pagina) if pagina in futuro else len(futuro) + 1

    return max(ocupados, key=distancia)


def simular(algoritmo, secuencia, marcos):
    """Corre un algoritmo sobre la secuencia de pedidos.

    Devuelve un diccionario:
      algoritmo, marcos, fallos, aciertos y
      pasos: lista con un diccionario por pedido:
        pedido   -> libro pedido
        marcos   -> estado de la mesa tras el pedido (None = marco vacío)
        fallo    -> True si hubo fallo
        victima  -> libro que se sacó (None si no se sacó ninguno)
    """
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo no válido: {algoritmo}")
    secuencia = list(secuencia)
    _validar(secuencia, marcos)

    mesa = [None] * marcos     # cada posición es un marco; se reemplaza en el mismo lugar
    orden_carga = {}           # libro -> en qué pedido entró a la mesa (para FIFO)
    ultimo_uso = {}            # libro -> último pedido en que se usó (para LRU)
    pasos = []
    fallos = 0

    for i, pedido in enumerate(secuencia):
        victima = None
        if pedido in mesa:
            fallo = False
        else:
            fallo = True
            fallos += 1
            if None in mesa:
                mesa[mesa.index(None)] = pedido
            else:
                victima = _elegir_victima(algoritmo, mesa, secuencia, i,
                                          orden_carga, ultimo_uso)
                mesa[mesa.index(victima)] = pedido
                orden_carga.pop(victima, None)
                ultimo_uso.pop(victima, None)
            orden_carga[pedido] = i
        ultimo_uso[pedido] = i  # un acierto también cuenta como uso (importa en LRU)

        pasos.append({
            "pedido": pedido,
            "marcos": list(mesa),
            "fallo": fallo,
            "victima": victima,
        })

    return {
        "algoritmo": algoritmo,
        "marcos": marcos,
        "fallos": fallos,
        "aciertos": len(secuencia) - fallos,
        "pasos": pasos,
    }


def fifo(secuencia, marcos):
    return simular(FIFO, secuencia, marcos)


def lru(secuencia, marcos):
    return simular(LRU, secuencia, marcos)


def optimo(secuencia, marcos):
    return simular(OPTIMO, secuencia, marcos)


def comparar(secuencia, marcos):
    """Los tres algoritmos con la misma secuencia y los mismos marcos.

    Devuelve {nombre_del_algoritmo: resultado}.
    """
    return {nombre: simular(nombre, secuencia, marcos) for nombre in ALGORITMOS}


def texto_marcos(marcos):
    """Formato para la tabla de resultados: [7,0,–]."""
    return "[" + ",".join("–" if m is None else str(m) for m in marcos) + "]"