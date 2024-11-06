import os

def renombrar_archivos(ruta):
    # Verifica si la ruta existe
    if not os.path.exists(ruta):
        print("La ruta especificada no existe.")
        return

    # Recorre la ruta de origen
    for carpeta_raiz, _, archivos in os.walk(ruta):
        for archivo in archivos:
            # Verifica si el archivo tiene la extensión ".jpeg.jpeg"
            if archivo.endswith('.jpeg.jpeg'):
                # Construye las rutas completas
                ruta_antigua = os.path.join(carpeta_raiz, archivo)
                nuevo_nombre = archivo[:-10] + '.jpeg'  # Cambia ".jpeg.jpeg" a ".jpeg"
                ruta_nueva = os.path.join(carpeta_raiz, nuevo_nombre)

                # Verifica si el archivo nuevo ya existe
                if not os.path.exists(ruta_nueva):
                    # Renombra el archivo
                    os.rename(ruta_antigua, ruta_nueva)
                    print(f"Renombrado: {ruta_antigua} a {ruta_nueva}")
                else:
                    print(f"El archivo {ruta_nueva} ya existe. Omitiendo cambio.")

# Ruta donde se buscarán los archivos
ruta_busqueda = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS"
renombrar_archivos(ruta_busqueda)
