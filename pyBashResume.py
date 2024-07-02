#!/bin/python3
from custom_logging import build_logger
from custom_parser import CustomParser

import subprocess
import os
import signal
import json
import sys
import time
import argparse


# Obtiene el directorio donde está ubicado el scripit
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
log_file_path = os.path.join(script_dir, 'migration.log')
logger = build_logger(log_file_path)


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        # Convertir el tiempo de ejecución a horas, minutos y segundos
        horas = int(execution_time // 3600)
        minutos = int((execution_time % 3600) // 60)
        segundos = int(execution_time % 60)
        logger.warning(f"Tiempo de ejecución: {horas}:{minutos}:{segundos}")
        return result
    return wrapper


@timing_decorator
def execute_commands(cmd):
    logger.info(f"Ejecutando comando: {cmd}")
    # EJECUCIÓN CON RUN SIN CAPTURAR SALIDA
    # result = subprocess.run(
    #     cmd, shell=True, stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE, universal_newlines=True)
    # execution_time = end_time - start_time
    # if result.returncode != 0:
    #     logger.error(
    #         f"Error al ejecutar '{cmd}': {result.stderr.strip()}")
    #     logger.info(f"Tiempo de ejecución: {execution_time}")
    #     with open(state_file, "w") as f:
    #         f.write(cmd)
    #     logger.info("Estado guardado en el archivo 'state'")
    #     exit(1)
    # else:
    #     logger.info(f"Completado '{cmd}' correctamente.")
    #     logger.info(f"Tiempo de ejecución: {execution_time}")

    # Ejecutar el comando con subprocess.Popen y leer la salida línea
    # por línea
    with subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT) as p:
        for salida in iter(p.stdout.readline, b''):
            sys.stdout.buffer.write(salida)
            sys.stdout.buffer.flush()
        p.wait()
        if p.returncode != 0:
            logger.error(f"Error en la ejecución del comando ${cmd}")
            return False
        logger.info(f"Se ha ejecutado el comando: $ {cmd}")
    return True


def read_state(state_file):
    """Lee el estado desde un archivo JSON y devuelve un diccionario"""
    if not os.path.exists(state_file):
        with open(state_file, 'w') as f:
            json.dump({}, f, indent=4)
        logger.debug(
            f"Archivo '{state_file}' no existía, creado nuevo archivo.")
        return {}

    with open(state_file, 'r') as f:
        return json.load(f)


def write_state(state_file, state):
    """Escribe el estado a un archivo JSON"""
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=4)

def read_user_confirmation(current_file, last_command):
    while True:
        question = f"¿Reanudar en el fichero {current_file} el comando {last_command}. Si (y) No (n)?\n"
        res = input(question)
        res = res.strip().lower()

        match res:
            case "y":
                return True
            case "n":
                logger.info("ABORTANDO REAUNDAR")
                return False
            case _:
                print("Introduce (y) para continuar (n) para salir")


@timing_decorator
def run_steps():
    state_file = os.path.join(script_dir, 'state.json')
    dir_steps = os.path.join(script_dir, 'migration-steps')
    # Leer el estado actual
    state = read_state(state_file)
    # current_dir = state.get("current_dir")
    current_file = state.get("current_file")
    last_command = state.get("last_command")

    mig_route = f"{dir_steps}"
    file_steps = sorted([name for name in os.listdir(mig_route)])

    # logger.info("\033[34m" + subdir + "\033[0m")

    start_file = (
        file_steps.index(current_file) if current_file else 0
    )
    if current_file:
        confirm = read_user_confirmation(current_file, last_command)
        if not confirm:
            exit(1)
        logger.warning(f"Reaunudando fichero: {current_file}")


    for file in file_steps[start_file:]:
        file_route = f"{mig_route}/{file}"
        logger.debug(f"Ejecutando {file_route}")
        rules = {
            "#>": "log",
            "#": "comment",
        }
        parser = CustomParser(file_route, rules)
        line_data_list = parser.parse_line()
        if not line_data_list:
            continue

        # Restablecer el estado antes de ejecutar
        state.update({
            # 'current_dir': subdir,
            'current_file': file,
        })
        write_state(state_file, state)
        for line_data in line_data_list:
            cmd = line_data.get('line')
            type = line_data.get('type')
            if type == 'comment':
                logger.debug(f'Comentario {cmd} ignorado')
                continue
            elif type == 'log':
                logger.debug('Detectado ,mensaje LOG')
                logger.info(cmd)
                continue

            # Es un comando, compruebo si lo skipeo
            if last_command:
                if cmd != last_command:
                    logger.debug(f"Skip del comando {cmd}")
                    continue
                logger.info(f"REANUDANDO EJECUCIÓN DE {cmd}")
                last_command = False

            # Ejecutar comandos y manejar errores
            success = execute_commands(cmd)
            if not success:
                # Guardar el estado y salir
                state["last_command"] = cmd
                write_state(state_file, state)

                # Leer el archivo onerror y ejecutar la primera linea pasandosela a execute_commands
                onerror_file = os.path.join(script_dir, 'onerror')
                if os.path.exists(onerror_file):
                    with open(onerror_file, 'r') as f:
                        onerror_cmd = f.readline().strip()
                        logger.info(f"Ejecutando comando onerror: {onerror_cmd}")
                        success = execute_commands(onerror_cmd)
                        if not success:
                            logger.error("Error al ejecutar el comando onerror.")
                            exit(1)

                logger.error("Deteniendo ejecución por error en el comando.")
                exit(1)

def set_doodba_dir(doodba_path):
    try:
        os.chdir(doodba_path)
    except FileNotFoundError:
        logger.error(f"El directorio '{doodba_path}' no existe.")
        exit(1)
    except Exception as e:
        logger.error(f"Error al cambiar al directorio '{doodba_path}': {e}")
        exit(1)


# Función para manejar la interrupción por CTRL+C
def signal_handler(sig, frame):
    logger.warning("Interrumpido por el usuario.")
    exit(0)

# Función principal
def main(doodba_path):
    set_doodba_dir(doodba_path)
    run_steps()




if __name__ == "__main__":
    # Capturar la señal de CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    # Configurar el manejo de la señal SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Script para cambiar al directorio especificado y ejecutar pasos.')
    parser.add_argument('doodba_path', type=str, help='La ruta al directorio doodba')
    args = parser.parse_args()

    main(args.doodba_path)
