import threading
import time

def cocinero_task(id_cocinero, utensilio_izq, utensilio_der):
    # Evitar interbloqueo invirtiendo orden para el último cocinero
    primero, segundo = (utensilio_izq, utensilio_der) if id_cocinero != 4 else (utensilio_der, utensilio_izq)

    with primero:
        with segundo:
            time.sleep(0.1) # Simulación de cocinar
            return f"Cocinero {id_cocinero} cocinó con éxito."