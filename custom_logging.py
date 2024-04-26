import logging

# Clase para formato con color
class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = {
            "DEBUG": "\033[34m",
            "INFO": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
            "CRITICAL": "\033[41m",
        }
        self.reset = "\033[0m"

    def formatTime(self, record, datefmt=None):
        res = super().formatTime(record, datefmt)
        return f"{self.colors['DEBUG']}{res}{self.reset}"

    def format(self, record):
        color = self.colors.get(record.levelname, self.reset)
        record.msg = f"{color}{record.msg}{self.reset}"
        record.levelname = f"{color}{record.levelname}{self.reset}"
        return super().format(record)

# Función para construir el logger
def build_logger(log_file):
    # Crear un logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # logger.setLevel(logging.DEBUG)

    # Configurar el handler para el archivo de log
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)-8s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    # Configurar el handler para la consola con color
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s - %(levelname)-22s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    console_handler.setLevel(logging.DEBUG)

    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
