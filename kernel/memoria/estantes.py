"""Estantes de la biblioteca (Módulo 3): asignación contigua y fragmentación.

El estante es una fila de posiciones. Cada libro ocupa varias posiciones
SEGUIDAS (asignación contigua). Al colocar y retirar libros van quedando
huecos sueltos: eso es la fragmentación externa.

Dos estrategias para elegir el hueco:
- first fit: el primer hueco donde quepa.
- best fit:  el hueco más pequeño donde quepa.

Esta lógica no usa Tkinter: la interfaz solo le pide los bloques para dibujarlos.
"""

FIRST_FIT = "first_fit"
BEST_FIT = "best_fit"
ESTRATEGIAS = (FIRST_FIT, BEST_FIT)


class Estante:
    def __init__(self, capacidad=20):
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que 0")
        self.capacidad = capacidad
        # Cada posición guarda el código del libro que la ocupa, o None si está libre.
        self._posiciones = [None] * capacidad
        # codigo -> (libro, inicio, tamano)
        self._colocados = {}

    # ---------- Consultas ----------

    def huecos(self):
        """Lista de (inicio, tamano) de cada hueco libre, de izquierda a derecha."""
        huecos = []
        inicio = None
        for i, ocupante in enumerate(self._posiciones):
            if ocupante is None and inicio is None:
                inicio = i
            elif ocupante is not None and inicio is not None:
                huecos.append((inicio, i - inicio))
                inicio = None
        if inicio is not None:
            huecos.append((inicio, self.capacidad - inicio))
        return huecos

    def bloques(self):
        """Estante completo en orden, para dibujarlo.

        Devuelve una lista de diccionarios con inicio, tamano y libro
        (el objeto Libro, o None si el bloque es un hueco libre).
        """
        bloques = []
        for inicio, tamano in self.huecos():
            bloques.append({"inicio": inicio, "tamano": tamano, "libro": None})
        for libro, inicio, tamano in self._colocados.values():
            bloques.append({"inicio": inicio, "tamano": tamano, "libro": libro})
        bloques.sort(key=lambda b: b["inicio"])
        return bloques

    def fragmentacion(self):
        """Mide qué tan partido está el espacio libre.

        Puede haber espacio libre de sobra y aun así no caber un libro grande,
        porque está repartido en pedazos. Por eso importa el hueco MÁS GRANDE.
        """
        huecos = self.huecos()
        libre_total = sum(tamano for _, tamano in huecos)
        hueco_mayor = max((tamano for _, tamano in huecos), default=0)
        if libre_total == 0:
            externa = 0.0
        else:
            externa = round(100 * (1 - hueco_mayor / libre_total), 1)
        return {
            "libre_total": libre_total,
            "hueco_mayor": hueco_mayor,
            "num_huecos": len(huecos),
            "fragmentacion_externa": externa,  # % del libre que no está en el hueco mayor
        }

    # ---------- Operaciones ----------

    def colocar(self, libro, tamano, estrategia=FIRST_FIT):
        """Coloca el libro con la estrategia elegida.

        Devuelve la posición de inicio, o None si no cabe en ningún hueco
        (aunque el espacio libre total alcance, si está fragmentado).
        """
        if estrategia not in ESTRATEGIAS:
            raise ValueError(f"Estrategia no válida: {estrategia}")
        if tamano <= 0:
            raise ValueError("El tamaño debe ser mayor que 0")
        if libro.codigo in self._colocados:
            raise ValueError(f"El libro {libro.codigo} ya está en el estante")

        candidatos = [(inicio, t) for inicio, t in self.huecos() if t >= tamano]
        if not candidatos:
            return None

        if estrategia == FIRST_FIT:
            inicio = candidatos[0][0]
        else:
            # El hueco más pequeño donde quepa; si hay empate, el de más a la izquierda.
            inicio = min(candidatos, key=lambda h: (h[1], h[0]))[0]

        for i in range(inicio, inicio + tamano):
            self._posiciones[i] = libro.codigo
        self._colocados[libro.codigo] = (libro, inicio, tamano)
        return inicio

    def retirar(self, codigo):
        """Retira un libro y deja su espacio libre. Devuelve False si no estaba."""
        if codigo not in self._colocados:
            return False
        _, inicio, tamano = self._colocados.pop(codigo)
        for i in range(inicio, inicio + tamano):
            self._posiciones[i] = None
        return True