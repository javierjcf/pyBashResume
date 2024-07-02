# pyBashResume
Ejecutar comandos shell desde ficheros de texto, logueando y recordando el estado de ejecución, pudiendo resumir la ejecución desde el último paso ejecutado

## COMO USAR
- Descargar el repositorio
- Colocar los comandos en ficheros ordenados por nombre por ejemplo, 01-paso1, 02-paso2...
- Ejecutar `./pyBashResume /ruta/directorio/aplicar/steps`
- Se ejecutarán los comandos de los ficheros de la carpeta migration-steps línea a línea
- Si una línea es un comentario de bash empezando po `#` se ignora
- Si una línea es un comentario de bash empezando po `#>` se hará loging del comentario.

## CONSIDRACIONES
- Cada línea se ejecuta en un proceso bash separado
- No se puede hacer un cambio de directorio y que se recuerde en la siguiente línea. De ser el caso el cambio de directorio y los
  sucesivos comandos deben ser en la misma línea, separados po `;`o `&&`
- Si occurre algún error se ejecutan los comandos del fichero especial `onerror`
- El script recuerda el estado gracias al fichero `state.json` el cual puede editarse para controlar donde se resume el script