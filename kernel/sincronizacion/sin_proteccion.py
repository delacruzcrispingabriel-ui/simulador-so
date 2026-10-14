"""Demo de la condición de carrera (Módulo 2, versión SIN protección)."""

import threading

from kernel.modelos import Libro
from kernel.sincronizacion.catalogo import Catalogo

NOMBRES = ["Ana", "Juan", "Pedro", "Maria", "Luis", "Rosa", "Carlos", "Lucia"]


def _usuario(catalogo, nombre, resultados):
    """Lo que hace cada hilo: intenta llevarse el libro."""
    resultados.append(catalogo.prestar_sin_proteccion(nombre))


def ejecutar_sin_proteccion(ejemplares=1, usuarios=5):
    """Lanza `usuarios` hilos que piden el mismo libro a la vez.

    Devuelve un diccionario con los números de la ejecución y el registro.
    """
    if usuarios > len(NOMBRES):
        raise ValueError(f"Máximo {len(NOMBRES)} usuarios")

    libro = Libro(1, "Sistemas Operativos Modernos", ejemplares)
    catalogo = Catalogo(libro)
    resultados = []

    hilos = [threading.Thread(target=_usuario, args=(catalogo, nombre, resultados))
             for nombre in NOMBRES[:usuarios]]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    prestamos = sum(resultados)
    return {
        "ejemplares_iniciales": ejemplares,
        "prestamos": prestamos,
        "ejemplares_finales": libro.ejemplares,
        # Más préstamos que ejemplares = hubo carrera
        "condicion_carrera": prestamos > ejemplares,
        "registro": catalogo.registro,
    }