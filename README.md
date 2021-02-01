# PROYECTO PHOTOCALL

    WARNING: Some bugs are known, dont use in an productión environment, you will experience a data lose.

### Lista de acciones
- ficheros
  - crear un directorio para guardar fotos
  - manejar pendrive
  - comprobar espacio
  - listar ficheros

- manejar botón externo
  - comprobar que está presente en un thread
  - leer estado del botón
  - encender el led

- display
  - esconder el cursor
  - manejar eventos de teclado
    - salir
    - hacer foto
    - pausar proceso
    - expulsar pendrive
  - crear carrusel [+]|[_]|[-]
  - cargar foto en el carrusel
  - eliminar foto del carrusel

- cámara
  - comprobar que está presente en un thread
  - hacer foto y guardarla

### Modos
- Primer inicio (Inicialización)
  - Pantalla de menú de configuración
    - Ir al slider (reproducción continua, sin fotos modo cover)
    - Selección de modos de reproducción
    - Reinicio|apagado del sistema
    - Selección de pendrive
      - Formateo
      - Marcado (se genera un fichero con un id para identificar el pendrive)
        - Si existe leer datos:
          {"event_id":"", "event_name":"", "event_description":"", "event_date":"", "cover_path":"./cover/"}
- Slider
  - Sin fotos, modo cover
  - Hacer foto
  - Carrusel en marcha (bucle infinito)
  - Excepciones
    - Teclado (detener)
    - Botón (detener: presión durante >10seg. + confirmación)
    - Error cámara
    - Error dispositivo botón
    - Error pendrive (montaje|lectura|escritura)
    - Error secuencia (el fichero existe)


- clase carousel:
  - Play
    - ff|rw|random
    - stop
  - transition
    - left|right


## TODO
- Refactoring:
  - Cambiar función por clase para manejar directorios ( createSaveFolder => Photopath )
    - Comprueba si existe
    - Crea uno si no existe
    - Devuelve los ficheros que contiene como un diccionario { "name":"", "extension":"", "resolution":(h, w)}
  - Cambiar función montar por clase pendrvive
    - Montar
    - Comprobar estado: {"device":"/dev/sd[x]" , "mounted":"True|False", "status":"RW|RO|None", "free":"0-100%"}
- Nuevas características:
  - Diferentes logs para info, warns, errors... eliminar prints del bucle principal, salida mínima por consola


*[HTML]: HyperText Markup Language