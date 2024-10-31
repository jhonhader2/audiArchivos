import os
import re
import pandas as pd
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

def verificar_archivos(rutas, archivo_excel):
    # Leer el archivo Excel y extraer los nombres de las carpetas
    try:
        df = pd.read_excel(archivo_excel, header=9)  # Ajusta 'header' según corresponda
    except FileNotFoundError:
        print(Fore.RED + f"Error: El archivo Excel '{archivo_excel}' no se encontró." + Style.RESET_ALL)
        return
    except Exception as e:
        print(Fore.RED + f"Ocurrió un error al leer el archivo Excel: {e}" + Style.RESET_ALL)
        return

    df.columns = df.columns.str.strip()  # Eliminar espacios en blanco de los nombres de las columnas

    try:
        nombres_carpetas = df["NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR"].dropna().astype(str).tolist()
    except KeyError:
        print(Fore.RED + "Error: La columna 'NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR' no se encontró en el archivo Excel." + Style.RESET_ALL)
        print("Las columnas disponibles son:", df.columns.tolist())
        return

    # Normalizar nombres de carpetas del Excel
    nombres_carpetas = [nombre.strip() for nombre in nombres_carpetas]

    total_carpetas_esperadas = len(nombres_carpetas)
    total_carpetas_encontradas = 0
    total_carpetas_no_encontradas = 0
    archivos_faltantes = {}
    carpetas_no_encontradas = []

    for nombre_carpeta_excel in nombres_carpetas:
        carpeta_encontrada = False
        ruta_carpeta_encontrada = ""

        # Buscar la carpeta en las rutas proporcionadas
        for ruta in rutas:
            if not os.path.exists(ruta):
                print(Fore.RED + f"Error: La ruta '{ruta}' no existe." + Style.RESET_ALL)
                continue

            # Obtener subcarpetas inmediatas
            subcarpetas = [d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))]

            for nombre_carpeta in subcarpetas:
                # Extraer el identificador de la carpeta (parte numérica)
                identificador = re.split(r'[_ ]+', nombre_carpeta.strip())[0]

                # Comprobar si el identificador coincide con el nombre de carpeta del Excel
                if identificador == nombre_carpeta_excel:
                    carpeta_encontrada = True
                    ruta_carpeta_encontrada = os.path.join(ruta, nombre_carpeta)
                    break  # Salir del bucle de subcarpetas

            if carpeta_encontrada:
                break  # Salir del bucle de rutas

        if not carpeta_encontrada:
            # Si no se encontró la carpeta en ninguna ruta
            print(Fore.RED + f"Error: No se encontró la carpeta para '{nombre_carpeta_excel}' en las rutas proporcionadas." + Style.RESET_ALL)
            total_carpetas_no_encontradas += 1
            carpetas_no_encontradas.append(nombre_carpeta_excel)
            continue  # Pasar al siguiente nombre_carpeta_excel

        total_carpetas_encontradas += 1
        archivos_faltantes[nombre_carpeta_excel] = []

        archivos = os.listdir(ruta_carpeta_encontrada)
        archivos_normalizados = [f.lower() for f in archivos]

        # Archivos requeridos
        archivos_requeridos = [
            f"av_{nombre_carpeta_excel}.pdf",
            f"fc_{nombre_carpeta_excel}.pdf",
        ]

        # Verificar fotografía
        formatos_imagen = ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
        foto_encontrada = any(
            f"f_{nombre_carpeta_excel}{ext}".lower() in archivos_normalizados
            for ext in formatos_imagen
        )

        if not foto_encontrada:
            archivos_faltantes[nombre_carpeta_excel].append(f"F_{nombre_carpeta_excel}.[ext]")

        # Verificar otros archivos
        for archivo in archivos_requeridos:
            if archivo.lower() not in archivos_normalizados:
                archivos_faltantes[nombre_carpeta_excel].append(archivo.upper())

    # Mostrar resultados
    print(f"\nTotal de carpetas esperadas según el Excel: {total_carpetas_esperadas}")
    print(f"Total de carpetas encontradas: {total_carpetas_encontradas}")
    print(f"Total de carpetas no encontradas: {total_carpetas_no_encontradas}")

    if carpetas_no_encontradas:
        print(Fore.RED + "\nLas siguientes carpetas no se encontraron:" + Style.RESET_ALL)
        for nombre in carpetas_no_encontradas:
            print(Fore.RED + f" - {nombre}" + Style.RESET_ALL)

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
rutas = [ruta.strip() for ruta in rutas if ruta.strip()]  # Limpiar espacios y eliminar rutas vacías
archivo_excel = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\REPORTES NACIONAL\20241020\f4.mo31.pp_formato_seguimiento_sfsc_v2_20241010.xlsx"
verificar_archivos(rutas, archivo_excel)
