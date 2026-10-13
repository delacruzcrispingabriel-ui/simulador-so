class Proceso:
    def __init__(self, pid, burst_time, prioridad=0):
        self.pid = pid
        self.burst_time = burst_time
        self.tiempo_restante = burst_time
        self.prioridad = prioridad
        self.tiempo_espera = 0
        self.tiempo_respuesta = 0

    def __repr__(self):
        return f"Proceso({self.pid}, Burst={self.burst_time})"