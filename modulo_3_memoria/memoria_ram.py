def simular_fifo(secuencia, num_marcos):
    memoria = []
    fallos = 0
    for pagina in secuencia:
        if pagina not in memoria:
            fallos += 1
            if len(memoria) >= num_marcos:
                memoria.pop(0)
            memoria.append(pagina)
    return fallos