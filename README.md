<div align="center">

# 📚 Biblioteca FIIS
### Simulador de Sistema Operativo

*Los conceptos de SO explicados como los vive cualquiera: en una biblioteca.*

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-informational)
![Curso](https://img.shields.io/badge/Curso-SW407-8A2BE2)
![UNI](https://img.shields.io/badge/UNI-FIIS-C8102E)

</div>

---

## 💡 La idea

Proyecto integrador del curso **SW407 Sistemas Operativos** (UNI - FIIS).

En vez de explicar un planificador o un semáforo con diagramas abstractos, lo hacemos con algo que todos hemos vivido: **sacar un libro de la biblioteca**. Cada módulo del simulador es una situación cotidiana que, por debajo, es un concepto real de SO.

| # | Módulo | 📖 En la biblioteca | ⚙️ En el SO |
| :-: | --- | --- | --- |
| 1 | **Mostrador** 🛎️ | Usuarios haciendo cola con un solo bibliotecario | Planificación de procesos |
| 2 | **Catálogo** 🗂️ | Varios usuarios consultando mientras el bibliotecario actualiza | Sincronización |
| 3 | **Estantes** 📦 | Libros en estantes y una mesa de acceso rápido | Gestión de memoria |

---

## 🏗️ Arquitectura

La regla de oro: **el kernel no sabe que existe una interfaz**, y la interfaz **solo le pide cosas al kernel**.

```
┌──────────────┐   pide / consulta   ┌────────────────┐
│   ui/        │ ──────────────────► │   kernel/      │
│  (Tkinter)   │ ◄────────────────── │ (lógica pura)  │
└──────────────┘     estado          └────────────────┘
        ▲
        │ arranca
   ┌────┴────┐
   │ main.py │
   └─────────┘
```

```
📁 proyecto/
├── 🧠 kernel/   → lógica de cada módulo, sin interfaz gráfica
├── 🖼️ ui/       → interfaz en Tkinter
├── 🧪 tests/    → pruebas de cada módulo
├── 📄 docs/     → mockups e informe
└── 🚀 main.py   → punto de entrada
```

> Separar así permite probar toda la lógica con `tests/` sin abrir una sola ventana.

---

## ▶️ Cómo ejecutar

Solo necesitas **Python 3 con Tkinter** (ya viene en la mayoría de instalaciones). Nada de `pip install`.

```bash
python3 main.py
```

---

## 👥 Integrantes

| Nombre |
| --- |
| Aramburu Muñoz, Brad Justine |
| De la Cruz Crispin, Jhon Gabriel |
| Espinoza Lozano, Jhon Arnold |
| Huanchi Supo, Daniel Angel |

---

<div align="center">

*Hecho con 🧠 y bastante café en la FIIS - UNI*

</div>
