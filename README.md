# Biblioteca FIIS - Simulador de Sistema Operativo

Proyecto integrador del curso SW407 Sistemas Operativos (UNI - FIIS).

## La idea

Un simulador de sistema operativo ambientado en una biblioteca. Cada concepto
del curso se explica con una situación que cualquiera entiende:

| Módulo | Situación en la biblioteca | Tema de SO |
| --- | --- | --- |
| 1. Mostrador | Usuarios en cola con un solo bibliotecario | Planificación de procesos |
| 2. Catálogo | Varios usuarios consultando y un bibliotecario actualizando | Sincronización |
| 3. Estantes | Libros en estantes y una mesa de acceso rápido | Gestión de memoria |

## Arquitectura

- kernel/: la lógica de cada módulo, sin interfaz gráfica.
- ui/: la interfaz en Tkinter. Solo le pide cosas al kernel.
- main.py: arranca la aplicación.
- tests/: pruebas de cada módulo.
- docs/: mockups e informe.

## Cómo ejecutar

Requiere Python 3 con Tkinter, sin instalar nada más:

    python3 main.py

## Integrantes
Aramburu Muñoz Brad Justine 
De la Cruz Crispin Jhon Gabriel 
Espinoza Lozano Jhon Arnold
Huanchi Supo Daniel Angel
