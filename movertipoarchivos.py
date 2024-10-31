import os
import shutil

def mover_archivos(ruta):
    # Verifica si la ruta existe
    if not os.path.exists(ruta):
        print("La ruta especificada no existe.")
        return

    # Solicita las rutas de destino para fotos y videos
    ruta_fotos = input("Ingresa la ruta donde deseas mover las fotos: ")
    ruta_videos = input("Ingresa la ruta donde deseas mover los videos: ")

    # Crea las carpetas de destino si no existen
    if not os.path.exists(ruta_fotos):
        os.makedirs(ruta_fotos)
    if not os.path.exists(ruta_videos):
        os.makedirs(ruta_videos)

    # Extensiones de archivos de imagen y video
    extensiones_fotos = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    extensiones_videos = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}

    # Recorre la ruta de origen
    for carpeta_raiz, _, archivos in os.walk(ruta):
        for archivo in archivos:
            # Construye la ruta completa del archivo
            ruta_archivo = os.path.join(carpeta_raiz, archivo)
            _, extension = os.path.splitext(archivo)

            # Mueve el archivo a la ruta correspondiente según su tipo
            if extension.lower() in extensiones_fotos:
                ruta_archivo_destino = os.path.join(ruta_fotos, archivo)
                if not os.path.exists(ruta_archivo_destino):
                    shutil.move(ruta_archivo, ruta_fotos)
                else:
                    print(f"El archivo {archivo} ya existe en la ruta de fotos. Se deja la copia en la ruta de origen.")
            elif extension.lower() in extensiones_videos:
                ruta_archivo_destino = os.path.join(ruta_videos, archivo)
                if not os.path.exists(ruta_archivo_destino):
                    shutil.move(ruta_archivo, ruta_videos)
                else:
                    print(f"El archivo {archivo} ya existe en la ruta de videos. Se deja la copia en la ruta de origen.")

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

