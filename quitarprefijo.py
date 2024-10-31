import os

def quitar_prefijo_f(ruta):
    # Verifica si la ruta existe
    if not os.path.exists(ruta):
        print("La ruta especificada no existe.")
        return

    # Recorre la ruta de origen
    for carpeta_raiz, carpetas, _ in os.walk(ruta):
        for carpeta in carpetas:
            # Verifica si la carpeta comienza con 'F_' o 'f_'
            if carpeta.startswith(('F_', 'f_')):
                nueva_carpeta = carpeta[2:]  # Elimina 'F_' o 'f_'
                ruta_antigua = os.path.join(carpeta_raiz, carpeta)
                ruta_nueva = os.path.join(carpeta_raiz, nueva_carpeta)

                # Renombra la carpeta
                os.rename(ruta_antigua, ruta_nueva)
                print(f"Renombrada: {ruta_antigua} a {ruta_nueva}")

# Solicita la ruta al usuario
ruta = input("Ingresa la ruta donde se encuentran las carpetas: ")
quitar_prefijo_f(ruta)
