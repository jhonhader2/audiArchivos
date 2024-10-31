import os
import shutil

def mover_archivos(ruta):
    # Verifica si la ruta existe
    if not os.path.exists(ruta):
        print("La ruta especificada no existe.")
        return

    # Crea una carpeta de destino dentro de la ruta especificada
    ruta_destino = os.path.join(ruta, 'archivos_movidos')
    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)

    # Recorre la ruta de origen
    for carpeta_raiz, _, archivos in os.walk(ruta):
        for archivo in archivos:
            # Construye la ruta completa del archivo
            ruta_archivo = os.path.join(carpeta_raiz, archivo)
            ruta_archivo_destino = os.path.join(ruta_destino, archivo)

            # Verifica si el archivo ya existe en la ruta de destino
            if not os.path.exists(ruta_archivo_destino):
                # Mueve el archivo a la ruta de destino
                shutil.move(ruta_archivo, ruta_destino)
            else:
                print(f"El archivo {archivo} ya existe en la ruta de destino. Se deja la copia en la ruta de origen.")

    # Elimina las carpetas vacías
    for carpeta_raiz, carpetas, _ in os.walk(ruta, topdown=False):
        for carpeta in carpetas:
            ruta_carpeta = os.path.join(carpeta_raiz, carpeta)
            try:
                os.rmdir(ruta_carpeta)  # Elimina la carpeta si está vacía
            except OSError:
                pass  # Ignora si la carpeta no está vacía

# Solicita la ruta al usuario
ruta = input("Ingresa la ruta donde se encuentran los archivos: ")
mover_archivos(ruta)
