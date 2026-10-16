"""Pruebas de procesos (Módulo 1). Ejecutar: python3 -m unittest discover tests"""

import os
import unittest

from kernel.modelos import Usuario
from kernel.planificador.algoritmos import fcfs, round_robin
from kernel.procesos.creacion import demo_fork, fork_exec
from kernel.procesos.estados import (
    EJECUTANDO, LISTO, NUEVO, TERMINADO, ProcesoSim,
    cambios_de_contexto, historial_estados)


@unittest.skipUnless(hasattr(os, "fork"), "requiere Linux o macOS")
class TestCreacion(unittest.TestCase):
    def test_fork_crea_un_hijo_distinto(self):
        r = demo_fork()
        self.assertNotEqual(r["pid_padre"], r["pid_hijo"])
        self.assertEqual(r["pid_hijo"], r["pid_propio_del_hijo"])
        self.assertEqual(r["ppid_del_hijo"], r["pid_padre"])
        self.assertEqual(r["codigo_salida"], 0)

    def test_fork_exec_ejecuta_otro_programa(self):
        r = fork_exec(["echo", "hola biblioteca"])
        self.assertEqual(r["salida"], "hola biblioteca\n")
        self.assertEqual(r["codigo_salida"], 0)

    def test_exec_de_comando_inexistente(self):
        r = fork_exec(["programa_que_no_existe_xyz"])
        self.assertEqual(r["codigo_salida"], 127)

    def test_comando_vacio(self):
        with self.assertRaises(ValueError):
            fork_exec([])


class TestEstados(unittest.TestCase):
    def test_transicion_invalida(self):
        p = ProcesoSim("Ana")
        with self.assertRaises(ValueError):
            p.cambiar(EJECUTANDO, 0)       # Nuevo no puede ir directo a Ejecutando

    def test_historial_con_round_robin(self):
        usuarios = [Usuario("Ana", "Estudiante", 0, 5),
                    Usuario("Juan", "Docente", 1, 3)]
        h = historial_estados(usuarios, round_robin(usuarios, 2))
        self.assertEqual(h["Ana"][0], (0, NUEVO))
        self.assertEqual(h["Ana"][1], (0, LISTO))
        self.assertEqual(h["Ana"][-1][1], TERMINADO)
        # Ana no termina en su primer turno: vuelve a Listo antes de acabar
        self.assertIn(LISTO, [e for _, e in h["Ana"][2:-1]])

    def test_cambios_de_contexto(self):
        usuarios = [Usuario("A", "Estudiante", 0, 2),
                    Usuario("B", "Estudiante", 0, 2),
                    Usuario("C", "Estudiante", 0, 2)]
        self.assertEqual(cambios_de_contexto(fcfs(usuarios)), 2)
        # Round Robin con quantum 1 alterna mucho más que FCFS
        self.assertGreater(cambios_de_contexto(round_robin(usuarios, 1)), 2)


if __name__ == "__main__":
    unittest.main()