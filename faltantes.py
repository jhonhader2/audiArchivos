import os
import re
import pandas as pd
from collections import defaultdict
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

def verificar_archivos(rutas, archivo_excel):
    # Leer el archivo Excel y extraer los nombres de las carpetas y los profesionales
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
        df = df[["NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR", "NOMBRE COMPLETO DEL PROFESIONAL"]]
        df.dropna(subset=["NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR"], inplace=True)
    except KeyError as e:
        print(Fore.RED + f"Error: La columna '{e.args[0]}' no se encontró en el archivo Excel." + Style.RESET_ALL)
        print("Las columnas disponibles son:", df.columns.tolist())
        return

    # Crear un diccionario que asocia cada profesional con una lista de identificadores
    profesionales_dict = defaultdict(list)
    for _, row in df.iterrows():
        identificador = str(row["NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR"]).strip()
        profesional = str(row["NOMBRE COMPLETO DEL PROFESIONAL"]).strip()
        profesionales_dict[profesional].append(identificador)

    total_carpetas_esperadas = len(df)
    total_carpetas_encontradas = 0
    total_carpetas_no_encontradas = 0
    archivos_faltantes = defaultdict(lambda: defaultdict(list))
    carpetas_no_encontradas = defaultdict(list)

    for profesional, identificadores in profesionales_dict.items():
        for identificador in identificadores:
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
                    identificador_carpeta = re.split(r'[_ ]+', nombre_carpeta.strip())[0]

                    # Comprobar si el identificador coincide con el del Excel
                    if identificador_carpeta == identificador:
                        carpeta_encontrada = True
                        ruta_carpeta_encontrada = os.path.join(ruta, nombre_carpeta)
                        break  # Salir del bucle de subcarpetas

                if carpeta_encontrada:
                    break  # Salir del bucle de rutas

            if not carpeta_encontrada:
                # Si no se encontró la carpeta en ninguna ruta
                carpetas_no_encontradas[profesional].append(identificador)
                total_carpetas_no_encontradas += 1
                continue  # Pasar al siguiente identificador

            total_carpetas_encontradas += 1

            archivos = os.listdir(ruta_carpeta_encontrada)
            archivos_normalizados = [f.lower() for f in archivos]

            # Archivos requeridos
            archivos_requeridos = [
                f"av_{identificador}.pdf",
                f"fc_{identificador}.pdf",
            ]

            # Verificar fotografía
            formatos_imagen = ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
            foto_encontrada = any(
                f"f_{identificador}{ext}".lower() in archivos_normalizados
                for ext in formatos_imagen
            )

            faltantes = []

            if not foto_encontrada:
                faltantes.append(f"F_{identificador}.[ext]")

            # Verificar otros archivos
            for archivo in archivos_requeridos:
                if archivo.lower() not in archivos_normalizados:
                    faltantes.append(archivo.upper())

            if faltantes:
                archivos_faltantes[profesional][identificador] = faltantes

    # Mostrar resultados
    print(f"\nTotal de carpetas esperadas según el Excel: {total_carpetas_esperadas}")
    print(f"Total de carpetas encontradas: {total_carpetas_encontradas}")
    print(f"Total de carpetas no encontradas: {total_carpetas_no_encontradas}")

    # Mostrar pendientes por profesional
    for profesional in profesionales_dict.keys():
        print(f"\n{Fore.GREEN}Pendientes para el profesional: {profesional}{Style.RESET_ALL}")

        # Carpetas no encontradas
        if profesional in carpetas_no_encontradas and carpetas_no_encontradas[profesional]:
            print(Fore.RED + " - Carpetas no encontradas:" + Style.RESET_ALL)
            for identificador in carpetas_no_encontradas[profesional]:
                print(Fore.RED + f"   * {identificador}" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + " - Todas las carpetas fueron encontradas." + Style.RESET_ALL)

        # Archivos faltantes
        if profesional in archivos_faltantes and archivos_faltantes[profesional]:
            print(Fore.YELLOW + " - Archivos faltantes en carpetas encontradas:" + Style.RESET_ALL)
            for identificador, faltantes in archivos_faltantes[profesional].items():
                print(f"   * En la carpeta {identificador} faltan {len(faltantes)} archivo(s):")
                for archivo_faltante in faltantes:
                    print(f"{Fore.YELLOW}     - {archivo_faltante} no se encontró{Style.RESET_ALL}")
        else:
            print(Fore.GREEN + " - No hay archivos faltantes en las carpetas encontradas." + Style.RESET_ALL)

    print("\nProceso completado.")

# Ejemplo de uso
rutas = input("Introduce las rutas a verificar (separadas por comas): ").split(",")
rutas = [ruta.strip() for ruta in rutas if ruta.strip()]  # Limpiar espacios y eliminar rutas vacías
archivo_excel = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\REPORTES NACIONAL\20241020\f4.mo31.pp_formato_seguimiento_sfsc_v2_20241010.xlsx"
verificar_archivos(rutas, archivo_excel)
