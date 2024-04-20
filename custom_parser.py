class CustomParser:
    def __init__(self, file_path, rules):
        """
        Inicializa el CustomParser con el archivo a leer y un diccionario de reglas.
        """
        self._file_path = file_path
        self._rules = rules

    def parse_line(self):
        """
        Lee una línea del archivo y determina su tipo según las reglas.
        """
        parsed_lines = []
        if self._file_path is None:
            raise RuntimeError("Ruta del fichero a leer no extablecida.")
        
        with open( self._file_path, 'r') as file:
            for line in file:
                if not line:
                    return None  # Indica el final del archivo

                stripped_line = line.strip()

                # Aplicar reglas para determinar el tipo de línea
                for key, value in self._rules.items():
                    if stripped_line.startswith(key):
                        stripped_line.replace(key, '')
                        line_type = value
                        break
                else:
                    line_type = "cmd"  # Valor predeterminado si no coincide con ninguna regla
                line_data = {
                    "line": stripped_line,
                    "type": line_type,
                }
                parsed_lines.append(line_data)
        return parsed_lines



# Ejemplo de uso (no parte del módulo, solo para demostrar cómo usar el CustomParser)
# def example_usage():
#     # Diccionario de reglas para interpretar líneas
#     rules = {
#         "#>": "log",
#         "#": "comment",
#     }

#     file_path = "input.txt"  # Cambia a tu archivo de interés
#     parser = CustomParser(file_path, rules)

#     while True:
#         result = parser.parse_line()
#         if result is None:
#             break  # Final del archivo

#         print(f"Tipo: {result['type']}, Línea: {result['line']}")

#     parser.close()
