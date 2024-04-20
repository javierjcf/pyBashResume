#!/bin/python3
from custom_logging import build_logger
from custom_parser import CustomParser  

import subprocess
import os
import signal
from datetime import datetime

import sys
import time

log_file_path = "/opt/doodba-openupgrade/cmnt-migrate/migration.log"
logger = build_logger(log_file_path)


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.warning(f"Tiempo de ejecución de '{func.__name__}': {execution_time:.6f} segundos")
        # Convertir el tiempo de ejecución a horas, minutos y segundos
        horas = int(execution_time // 3600)
        minutos = int((execution_time % 3600) // 60)
        segundos = int(execution_time % 60)
        logger.warning(f"Tiempo de ejecución de '{func.__name__}': {horas} horas, {minutos} minutos, {segundos:.0f} segundos")
        return result
    return wrapper

@timing_decorator
def execute_commands(line_data_list):
    for line_data in line_data_list:
        cmd = line_data.get('line')
        type = line_data.get('type')
        if type == 'comment':
            logger.debug(f'Comentario {cmd} ignorado')
        elif type == 'log':
            logger.debug('Detectado ,mensaje LOG')
            logger.info(cmd)

        logger.info(f"Ejecutando comando: {cmd}")
        # Ejecutar el comando con subprocess.Popen y leer la salida línea por línea
        with subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT) as p:
            for salida in iter(p.stdout.readline, b''):
                sys.stdout.buffer.write(salida)
                sys.stdout.buffer.flush()
            p.wait()
            if p.returncode != 0:
                logger.error(f"Error en la ejecución del comando ${cmd}")
                exit(1)
            else:
                logger.info(f"Se ha ejecutado el comando: $ {cmd}")

    
    


# Función para ejecutar los comandos y manejar el estado de la migración
@timing_decorator
def run_steps():    
    state_file = "/opt/doodba-openupgrade/cmnt-migrate/migrate.state"
    dir_steps = "/opt/doodba-openupgrade/cmnt-migrate/migration-steps"
    subdirs = sorted([name for name in os.listdir(dir_steps)])
    logger.info(subdirs)
    for subdir in subdirs:
        mig_route = f"{dir_steps}/{subdir}"
        file_steps = sorted([name for name in os.listdir(mig_route)])
        logger.info("\033[34m" + subdir + "\033[0m")
        for file in file_steps:
            file_route = f"{mig_route}/{file}"
            logger.debug(f'Ejecutando {file_route}')            
            rules = {
                "#>": "log",
                "#": "comment",
            }
            parser = CustomParser(file_route, rules)
            line_data = parser.parse_line()
            if not line_data:
                continue
            
            execute_commands(line_data)
            
            # with open(file_route, 'r') as f:
            #     for linea in f:
            #         cmd = linea.strip()
            #         logger.info(f"Ejecutando comando: {cmd}")

                    # EJECUCIÓN CON RUN SIN CAPTURAR SALIDA

                    # start_time = datetime.now()
                    # result = subprocess.run(
                    #     cmd, shell=True, stdout=subprocess.PIPE, 
                    #     stderr=subprocess.PIPE, universal_newlines=True)
                    # end_time = datetime.now()
                    # execution_time = end_time - start_time
                    # if result.returncode != 0:
                    #     logger.error(f"Error al ejecutar '{cmd}': {result.stderr.strip()}")
                    #     logger.info(f"Tiempo de ejecución: {execution_time}")
                    #     with open(state_file, "w") as f:
                    #         f.write(cmd)
                    #     logger.info("Estado guardado en el archivo 'state'")
                    #     exit(1)
                    # else:
                    #     logger.info(f"Completado '{cmd}' correctamente.")
                    #     logger.info(f"Tiempo de ejecución: {execution_time}")


                    # Ejecutar el comando con subprocess.Popen y leer la salida línea por línea
                    # with subprocess.Popen(
                    #         cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
                    #     for salida in iter(p.stdout.readline, b''):
                    #         sys.stdout.buffer.write(salida)
                    #         sys.stdout.buffer.flush()
                    #     p.wait()
                    #     if p.returncode != 0:
                    #         logger.error(f"Error en la ejecución del comando ${cmd}")
                    #         exit(1)
                    #     else:
                    #         logger.info(f"Se ha ejecutado el comando: $ {cmd}")

def set_doodba_dir():
    doodba_path = "/opt/doodba-openupgrade/elnogal-migration"
    try:
        os.chdir(doodba_path)
    except FileNotFoundError:
        logger.error("El directorio 'elnogal-migration' no existe.")
        exit(1)
    except Exception as e:
        logger.error(f"Error al cambiar al directorio 'elnogal-migration': {e}")
        exit(1)



# Función principal
def main():
    # example_usage()
    set_doodba_dir()
    run_steps()

    # if os.path.exists(state_file):
    #     with open(state_file, "r") as f:
    #         last_command = f.read().strip()
    #         logger.info(f"Continuando desde el estado anterior: {last_command}")
    # else:
    #     last_command = None
    # # Cambiar al directorio adecuado solo si no se ha hecho antes
    # if last_command is None or not last_command.startswith("cd"):
    #     logger.warning("Cambiando al directorio 'elnogal-migration'")
    
  

    # Ejecutar comandos comunes



    # Eliminar el archivo de estado al finalizar
    # if os.path.exists(state_file):
    #     os.remove(state_file)
    #     logger.info("Archivo 'state' eliminado.")

# Función para manejar la interrupción por CTRL+C
def signal_handler(sig, frame):
    logger.warning("Interrumpido por el usuario.")
    exit(0)

if __name__ == "__main__":
    # Capturar la señal de CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    main()

