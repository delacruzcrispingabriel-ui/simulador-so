import tkinter as tk
from tkinter import ttk, messagebox

# Importamos las funciones de cada módulo que creaste
from modulo_1_cpu.proceso import Proceso
from modulo_1_cpu.planificador import ejecutar_round_robin
from modulo_2_sincronizacion.cocineros_mutex import cocinero_task
from modulo_3_memoria.memoria_ram import simular_fifo

class DashboardSO(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Operativo Simulado - Panel de Control")
        self.geometry("650x450")

        # Crear contenedor de pestañas
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear las 3 pestañas para cada integrante/módulo
        self.tab1 = ttk.Frame(notebook)
        self.tab2 = ttk.Frame(notebook)
        self.tab3 = ttk.Frame(notebook)

        notebook.add(self.tab1, text="1. Planificador CPU")
        notebook.add(self.tab2, text="2. Concurrencia/Mutex")
        notebook.add(self.tab3, text="3. Paginación RAM")

        # Construir contenido de cada pestaña
        self.setup_modulo1()
        self.setup_modulo2()
        self.setup_modulo3()

    # --- PESTAÑA MÓDULO 1 ---
    def setup_modulo1(self):
        lbl = ttk.Label(self.tab1, text="Simulación de Planificación Round Robin", font=("Arial", 12, "bold"))
        lbl.pack(pady=10)

        btn = ttk.Button(self.tab1, text="Ejecutar Planificador", command=self.ejecutar_m1)
        btn.pack(pady=5)

        self.txt_m1 = tk.Text(self.tab1, height=12, width=65)
        self.txt_m1.pack(pady=10)

    def ejecutar_m1(self):
        procesos = [Proceso("P1", 5), Proceso("P2", 3), Proceso("P3", 4)]
        resultado = ejecutar_round_robin(procesos, quantum=2)
        
        self.txt_m1.delete("1.0", tk.END)
        self.txt_m1.insert(tk.END, "--- RESULTADO PLANIFICACIÓN ROUND ROBIN (Quantum = 2) ---\n\n")
        for item in resultado:
            self.txt_m1.insert(tk.END, f"Proceso: {item[0]} | Tiempo de ejecución final: {item[1]}s\n")

    # --- PESTAÑA MÓDULO 2 ---
    def setup_modulo2(self):
        lbl = ttk.Label(self.tab2, text="Simulación de Concurrencia (Filósofos / Cocineros)", font=("Arial", 12, "bold"))
        lbl.pack(pady=10)

        btn = ttk.Button(self.tab2, text="Iniciar Hilos & Mutex", command=self.ejecutar_m2)
        btn.pack(pady=5)

        self.txt_m2 = tk.Text(self.tab2, height=12, width=65)
        self.txt_m2.pack(pady=10)

    def ejecutar_m2(self):
        import threading
        utensilios = [threading.Lock() for _ in range(5)]
        
        self.txt_m2.delete("1.0", tk.END)
        self.txt_m2.insert(tk.END, "--- EJECUTANDO HILOS CON EXCLUSIÓN MUTUA ---\n\n")
        for i in range(5):
            u_izq = utensilios[i]
            u_der = utensilios[(i + 1) % 5]
            res = cocinero_task(i, u_izq, u_der)
            self.txt_m2.insert(tk.END, f"{res}\n")

    # --- PESTAÑA MÓDULO 3 ---
    def setup_modulo3(self):
        lbl = ttk.Label(self.tab3, text="Simulador de Paginación y Fallos de Memoria", font=("Arial", 12, "bold"))
        lbl.pack(pady=10)

        btn = ttk.Button(self.tab3, text="Calcular Fallos FIFO", command=self.ejecutar_m3)
        btn.pack(pady=5)

        self.txt_m3 = tk.Text(self.tab3, height=12, width=65)
        self.txt_m3.pack(pady=10)

    def ejecutar_m3(self):
        secuencia = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3]
        fallos = simular_fifo(secuencia, num_marcos=3)
        
        self.txt_m3.delete("1.0", tk.END)
        self.txt_m3.insert(tk.END, f"Secuencia de accesos: {secuencia}\n")
        self.txt_m3.insert(tk.END, f"Marcos de memoria disponibles: 3\n\n")
        self.txt_m3.insert(tk.END, f"Total de Fallos de Página (FIFO): {fallos}\n")

if __name__ == "__main__":
    app = DashboardSO()
    app.mainloop()
