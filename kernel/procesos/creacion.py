"""Creación de procesos (Módulo 1): fork, exec y wait sobre Linux/macOS.

Analogía de la biblioteca:
- fork:  un usuario se CLONA. Ahora hay dos personas idénticas: el padre
         (el original) y el hijo (la copia). Cada uno tiene su propio PID.
- exec:  el clon CAMBIA DE TRÁMITE: deja lo que hacía y pasa a ejecutar
         otro programa completamente distinto, conservando su PID.
- wait:  el padre ESPERA en el mostrador a que su hijo termine y recoge
         cómo le fue (el código de salida).

Nota: os.fork() no existe en Windows. En ese caso se lanza OSError.
"""

import os


def _exigir_fork():
    if not hasattr(os, "fork"):
        raise OSError("fork no está disponible en este sistema (usa Linux o macOS)")


def _leer_todo(fd):
    """Lee un descriptor hasta que el otro extremo se cierre."""
    partes = []
    while True:
        bloque = os.read(fd, 4096)
        if not bloque:
            break
        partes.append(bloque)
    return b"".join(partes).decode(errors="replace")


def demo_fork():
    """El padre se clona con fork; el hijo avisa su PID y el de su padre.

    Devuelve los PIDs y el código de salida del hijo.
    """
    _exigir_fork()
    lectura, escritura = os.pipe()   # canal para que el hijo le cuente al padre
    pid = os.fork()

    if pid == 0:
        # --- Aquí corre el HIJO ---
        os.close(lectura)
        os.write(escritura, f"{os.getpid()},{os.getppid()}".encode())
        os.close(escritura)
        os._exit(0)                  # termina sin tocar el estado del padre

    # --- Aquí corre el PADRE (pid es el PID del hijo) ---
    os.close(escritura)
    datos = _leer_todo(lectura)
    os.close(lectura)
    _, estado = os.waitpid(pid, 0)   # wait: espera a que el hijo termine

    pid_hijo_visto, ppid_del_hijo = (int(x) for x in datos.split(","))
    return {
        "pid_padre": os.getpid(),
        "pid_hijo": pid,
        "pid_propio_del_hijo": pid_hijo_visto,   # debe coincidir con pid_hijo
        "ppid_del_hijo": ppid_del_hijo,          # debe ser el pid del padre
        "codigo_salida": os.waitstatus_to_exitcode(estado),
    }


def fork_exec(comando):
    """fork + exec + wait: el hijo se transforma en `comando` (lista de texto).

    Ejemplo: fork_exec(["echo", "hola"]). Devuelve el PID del hijo, lo que
    imprimió el programa y su código de salida (127 si el comando no existe).
    """
    _exigir_fork()
    if not comando:
        raise ValueError("El comando no puede estar vacío")

    lectura, escritura = os.pipe()
    pid = os.fork()

    if pid == 0:
        # --- HIJO: su salida va al canal y luego exec reemplaza su programa ---
        try:
            os.close(lectura)
            os.dup2(escritura, 1)    # lo que imprima irá al padre
            os.close(escritura)
            os.execvp(comando[0], comando)   # si funciona, NUNCA regresa
        except OSError:
            pass
        os._exit(127)                # exec falló: el comando no existe

    os.close(escritura)
    salida = _leer_todo(lectura)
    os.close(lectura)
    _, estado = os.waitpid(pid, 0)
    return {
        "pid_hijo": pid,
        "comando": list(comando),
        "salida": salida,
        "codigo_salida": os.waitstatus_to_exitcode(estado),
    }