from modulo_1_cpu.proceso import Proceso
from modulo_1_cpu.planificador import ejecutar_round_robin
from modulo_3_memoria.memoria_ram import simular_fifo

def main():
    print("=== SISTEMA OPERATIVO SIMULADO (KERNEL DUMMY) ===")
    
    # Prueba rápida Módulo 1
    procesos = [Proceso("P1", 5), Proceso("P2", 3)]
    res_cpu = ejecutar_round_robin(procesos, quantum=2)
    print(f"[Módulo 1] Historial Round Robin: {res_cpu}")

    # Prueba rápida Módulo 3
    fallos = simular_fifo([7, 0, 1, 2, 0, 3], num_marcos=3)
    print(f"[Módulo 3] Fallos FIFO: {fallos}")

if __name__ == "__main__":
    main()