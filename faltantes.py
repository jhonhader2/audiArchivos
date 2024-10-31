import os
import re  # Importar el módulo re
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

def verificar_archivos(rutas):
    for ruta in rutas:
        if not os.path.exists(ruta):
            print(Fore.RED + f"Error: La ruta '{Fore.CYAN}{ruta}{Style.RESET_ALL}' no existe.")
            continue

        total_carpetas_revisadas = 0
        archivos_faltantes = {}

        # Obtener subcarpetas inmediatas
        subcarpetas = [d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))]

        for nombre_carpeta in subcarpetas:
            ruta_carpeta = os.path.join(ruta, nombre_carpeta)
            total_carpetas_revisadas += 1

            # Obtener el nombre de la carpeta y procesar
            NombreCarpeta = re.split(r'[_ ]+', nombre_carpeta.strip())[0]

            # Comprobar si el nombre de la carpeta no es numérico
            if not NombreCarpeta.isnumeric():
                print(Fore.RED + f"Error: El nombre de la carpeta '{nombre_carpeta}' debe comenzar con un identificador numérico." + Style.RESET_ALL)
                continue

            archivos_faltantes[NombreCarpeta] = []

            archivos = os.listdir(ruta_carpeta)

            # Archivos requeridos
            archivos_requeridos = [
                f"AV_{NombreCarpeta}.pdf",
                f"FC_{NombreCarpeta}.pdf",
            ]

            # Verificar fotografía
            formatos_imagen = ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
            foto_encontrada = any(
                any(f"F_{NombreCarpeta}{ext}".lower() == f.lower() for f in archivos)
                for ext in formatos_imagen
            )

            if not foto_encontrada:
                archivos_faltantes[NombreCarpeta].append(f"F_{NombreCarpeta}.[ext]")

            # Verificar otros archivos
            for archivo in archivos_requeridos:
                if not any(archivo.lower() == f.lower() for f in archivos):
                    archivos_faltantes[NombreCarpeta].append(archivo)

        # Mostrar resultados
        print(f"\nTotal de carpetas revisadas en '{ruta}': {total_carpetas_revisadas}")
        for nombre, faltantes in archivos_faltantes.items():
            if faltantes:
                total_faltantes = len(faltantes)
                print(f"\nEn la carpeta {Fore.CYAN}{nombre}{Style.RESET_ALL} faltan {total_faltantes} archivo(s):")
                for archivo_faltante in faltantes:
                    print(f"{Fore.YELLOW} - {archivo_faltante} no se encontró{Style.RESET_ALL}")
            else:
                print(f"\nLa carpeta {Fore.CYAN}{nombre}{Style.RESET_ALL} tiene todos los archivos requeridos.")

# Ejemplo de uso
rutas = input("Introduce las rutas a verificar (separadas por comas): ").split(",")
verificar_archivos([ruta.strip() for ruta in rutas])
