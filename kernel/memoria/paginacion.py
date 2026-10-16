"""Paginación (Módulo 3): tablas de páginas y fragmentación interna.

Analogía de la biblioteca:
- Un libro se corta en CAPÍTULOS del mismo tamaño: son las páginas.
- La mesa de acceso rápido tiene LUGARES del mismo tamaño: son los marcos.
- La TABLA DE PÁGINAS es el índice que dice en qué lugar de la mesa quedó
  cada capítulo. Los capítulos de un mismo libro pueden quedar en lugares
  no vecinos: por eso la paginación NO sufre fragmentación externa.
- Pero el último capítulo casi nunca llena su lugar: lo que sobra es la
  FRAGMENTACIÓN INTERNA.

Esta lógica no usa Tkinter: la interfaz solo le pide los datos para dibujar.
"""

import math


def paginas_necesarias(tamano, tam_pagina):
    """Cuántas páginas hacen falta para guardar `tamano` unidades."""
    if tamano <= 0:
        raise ValueError("El tamaño debe ser mayor que 0")
    if tam_pagina <= 0:
        raise ValueError("El tamaño de página debe ser mayor que 0")
    return math.ceil(tamano / tam_pagina)


def fragmentacion_interna(tamano, tam_pagina):
    """Unidades que sobran en la última página (se desperdician)."""
    return paginas_necesarias(tamano, tam_pagina) * tam_pagina - tamano


class MemoriaPaginada:
    """La mesa de acceso rápido dividida en marcos de tamaño fijo."""

    def __init__(self, num_marcos=8, tam_pagina=4):
        if num_marcos <= 0:
            raise ValueError("Los marcos deben ser mayores que 0")
        if tam_pagina <= 0:
            raise ValueError("El tamaño de página debe ser mayor que 0")
        self.num_marcos = num_marcos
        self.tam_pagina = tam_pagina
        # Cada marco guarda (nombre_del_libro, numero_de_pagina) o None si está libre.
        self._marcos = [None] * num_marcos
        # nombre -> {"tamano": int, "tabla": {pagina: marco}}
        self._libros = {}

    # ---------- Consultas ----------

    def marcos_libres(self):
        """Números de los marcos libres, de menor a mayor."""
        return [i for i, ocupante in enumerate(self._marcos) if ocupante is None]

    def tabla_de(self, nombre):
        """Tabla de páginas del libro: {pagina: marco}, o None si no está."""
        info = self._libros.get(nombre)
        return dict(info["tabla"]) if info else None

    def libros_cargados(self):
        """Libros en la mesa: {nombre: tamano}, en el orden en que se cargaron."""
        return {nombre: info["tamano"] for nombre, info in self._libros.items()}

    def estado_marcos(self):
        """Estado de la mesa, para dibujarla: lista de (nombre, pagina) o None."""
        return list(self._marcos)

    def traducir(self, nombre, direccion_logica):
        """Traduce una dirección lógica (posición dentro del libro) a física.

        direccion_logica = pagina * tam_pagina + desplazamiento
        direccion_fisica = marco  * tam_pagina + desplazamiento

        Devuelve un diccionario con cada paso, para mostrarlo en pantalla.
        """
        info = self._libros.get(nombre)
        if info is None:
            raise ValueError(f"El libro {nombre} no está en la mesa")
        if not 0 <= direccion_logica < info["tamano"]:
            raise ValueError(
                f"Dirección fuera del libro (0 a {info['tamano'] - 1})")

        pagina = direccion_logica // self.tam_pagina
        desplazamiento = direccion_logica % self.tam_pagina
        marco = info["tabla"][pagina]
        return {
            "direccion_logica": direccion_logica,
            "pagina": pagina,
            "desplazamiento": desplazamiento,
            "marco": marco,
            "direccion_fisica": marco * self.tam_pagina + desplazamiento,
        }

    # ---------- Operaciones ----------

    def cargar(self, nombre, tamano):
        """Carga un libro de `tamano` unidades usando marcos libres cualquiera.

        Devuelve un diccionario con la tabla de páginas y la fragmentación
        interna, o None si no hay marcos libres suficientes.
        """
        if nombre in self._libros:
            raise ValueError(f"El libro {nombre} ya está en la mesa")
        n = paginas_necesarias(tamano, self.tam_pagina)

        libres = self.marcos_libres()
        if len(libres) < n:
            return None

        tabla = {}
        for pagina, marco in enumerate(libres[:n]):
            self._marcos[marco] = (nombre, pagina)
            tabla[pagina] = marco
        self._libros[nombre] = {"tamano": tamano, "tabla": tabla}
        return {
            "tabla": dict(tabla),
            "paginas": n,
            "fragmentacion_interna": fragmentacion_interna(tamano, self.tam_pagina),
        }

    def retirar(self, nombre):
        """Retira el libro y libera sus marcos. False si no estaba."""
        info = self._libros.pop(nombre, None)
        if info is None:
            return False
        for marco in info["tabla"].values():
            self._marcos[marco] = None
        return True

    def desperdicio_total(self):
        """Fragmentación interna sumada de todos los libros cargados."""
        return sum(fragmentacion_interna(i["tamano"], self.tam_pagina)
                   for i in self._libros.values())