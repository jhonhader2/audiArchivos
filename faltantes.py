import os
import re
import pandas as pd
from collections import defaultdict
from colorama import Fore, Style, init

# Inicializar colorama para colorear la salida en la consola
init(autoreset=True)

def verificar_archivos(rutas, archivo_excel):
    # Leer el archivo Excel y extraer los datos necesarios
    try:
        # Lee el archivo Excel, ajusta 'header' si los encabezados están en otra fila
        df = pd.read_excel(archivo_excel, header=9)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: No se encontró el archivo Excel '{archivo_excel}'.{Style.RESET_ALL}")
        return
    except Exception as e:
        print(f"{Fore.RED}Error al leer el archivo Excel: {e}{Style.RESET_ALL}")
        return

    # Eliminar espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()

    try:
        # Seleccionar las columnas necesarias
        df = df[["NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR", "NOMBRE COMPLETO DEL PROFESIONAL"]]
        # Eliminar filas donde falte el número de documento
        df.dropna(subset=["NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR"], inplace=True)
    except KeyError as e:
        print(f"{Fore.RED}Error: La columna '{e.args[0]}' no se encontró en el archivo Excel.{Style.RESET_ALL}")
        print("Verifique que las columnas tengan los nombres correctos.")
        return

    # Crear un diccionario que asocia cada profesional con sus identificadores (números de documento)
    profesionales_dict = defaultdict(list)
    for _, row in df.iterrows():
        identificador = str(row["NÚMERO DE DOCUMENTO DEL JEFE DE GRUPO FAMILIAR"]).strip()
        profesional = str(row["NOMBRE COMPLETO DEL PROFESIONAL"]).strip()
        profesionales_dict[profesional].append(identificador)

    # Variables para llevar el conteo de carpetas
    total_carpetas_esperadas = len(df)
    total_carpetas_encontradas = 0
    total_carpetas_no_encontradas = 0

    # Diccionarios para almacenar los pendientes por profesional
    archivos_faltantes = defaultdict(lambda: defaultdict(list))
    carpetas_no_encontradas = defaultdict(list)

    # Iterar sobre cada profesional y sus identificadores
    for profesional, identificadores in profesionales_dict.items():
        for identificador in identificadores:
            carpeta_encontrada = False
            ruta_carpeta_encontrada = ""

            # Buscar la carpeta correspondiente en las rutas proporcionadas
            for ruta in rutas:
                if not os.path.exists(ruta):
                    print(f"{Fore.RED}Error: La ruta '{ruta}' no existe.{Style.RESET_ALL}")
                    continue

                # Obtener las subcarpetas en la ruta actual
                subcarpetas = [d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))]

                # Buscar la carpeta que coincide con el identificador
                for nombre_carpeta in subcarpetas:
                    # Extraer el identificador de la carpeta
                    identificador_carpeta = re.split(r'[_ ]+', nombre_carpeta.strip())[0]

                    # Comparar el identificador de la carpeta con el del Excel
                    if identificador_carpeta == identificador:
                        carpeta_encontrada = True
                        ruta_carpeta_encontrada = os.path.join(ruta, nombre_carpeta)
                        break  # Se encontró la carpeta, salir del bucle

                if carpeta_encontrada:
                    break  # Se encontró la carpeta en alguna ruta, salir del bucle

            if not carpeta_encontrada:
                # Si no se encontró la carpeta, agregar a la lista de pendientes
                carpetas_no_encontradas[profesional].append(identificador)
                total_carpetas_no_encontradas += 1
                continue  # Continuar con el siguiente identificador

            total_carpetas_encontradas += 1

            # Listar los archivos en la carpeta encontrada
            archivos = os.listdir(ruta_carpeta_encontrada)
            # Normalizar los nombres de los archivos a minúsculas para comparaciones
            archivos_normalizados = [f.lower() for f in archivos]

            # Lista de archivos requeridos
            archivos_requeridos = [
                f"av_{identificador}.pdf",
                f"fc_{identificador}.pdf",
            ]

            # Verificar si existe la fotografía con cualquier extensión de imagen
            formatos_imagen = ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
            foto_encontrada = any(
                f"f_{identificador}{ext}".lower() in archivos_normalizados
                for ext in formatos_imagen
            )

            # Lista para almacenar los archivos faltantes en esta carpeta
            faltantes = []

            if not foto_encontrada:
                # Si no se encontró la foto, agregar a los faltantes
                faltantes.append(f"F_{identificador}.[ext]")

            # Verificar los otros archivos requeridos
            for archivo in archivos_requeridos:
                if archivo.lower() not in archivos_normalizados:
                    faltantes.append(archivo.upper())

            if faltantes:
                # Si hay archivos faltantes, agregarlos al diccionario correspondiente
                archivos_faltantes[profesional][identificador] = faltantes

    # Mostrar un resumen general
    print(f"\n{Fore.BLUE}Resumen General:{Style.RESET_ALL}")
    print(f"Total de carpetas esperadas según el Excel: {total_carpetas_esperadas}")
    print(f"Total de carpetas encontradas: {total_carpetas_encontradas}")
    print(f"Total de carpetas no encontradas: {total_carpetas_no_encontradas}")

    # Mostrar los pendientes agrupados por profesional
    print(f"\n{Fore.BLUE}Pendientes por Profesional:{Style.RESET_ALL}")
    for profesional in profesionales_dict.keys():
        print(f"\n{Fore.GREEN}Profesional: {profesional}{Style.RESET_ALL}")

        # Contador de archivos y carpetas faltantes
        total_carpetas_faltantes = 0
        total_archivos_faltantes = 0

        # Mostrar carpetas no encontradas
        if profesional in carpetas_no_encontradas and carpetas_no_encontradas[profesional]:
            print(f"{Fore.RED}Carpetas no encontradas:{Style.RESET_ALL}")
            for identificador in carpetas_no_encontradas[profesional]:
                print(f"  - {identificador}")
                total_carpetas_faltantes += 1  # Contar cada carpeta no encontrada
        else:
            if profesional in archivos_faltantes and archivos_faltantes[profesional]:
                print(f"{Fore.GREEN}Todas las carpetas fueron encontradas.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}No se encontraron carpetas para el profesional.{Style.RESET_ALL}")

        # Mostrar archivos faltantes en carpetas encontradas
        if profesional in archivos_faltantes and archivos_faltantes[profesional]:
            print(f"{Fore.YELLOW}Archivos faltantes en carpetas encontradas:{Style.RESET_ALL}")
            for identificador, faltantes in archivos_faltantes[profesional].items():
                print(f"  - En la carpeta {Fore.CYAN}{identificador}{Style.RESET_ALL} faltan los siguientes archivos:")
                total_archivos_faltantes += len(faltantes)  # Contar los archivos faltantes
                for archivo_faltante in faltantes:
                    print(f"    * {Fore.YELLOW}{archivo_faltante}{Style.RESET_ALL}")
        else:
            if profesional not in carpetas_no_encontradas or not carpetas_no_encontradas[profesional]:
                print(f"{Fore.GREEN}No hay archivos faltantes en las carpetas encontradas.{Style.RESET_ALL}")

        # Imprimir total de pendientes por profesional
        print(f"{Fore.YELLOW}Total de pendientes para {Fore.GREEN}{profesional}{Style.RESET_ALL}: {total_carpetas_faltantes} carpetas y {total_archivos_faltantes} archivos.{Style.RESET_ALL}")

    print(f"\n{Fore.BLUE}Proceso completado.{Style.RESET_ALL}")

# Solicitar al usuario las rutas y el archivo Excel
def main():
    print("=== Verificación de Archivos ===\n")
    rutas_input = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS\SAN JOSÉ DEL GUAVIARE\ZONA 1\Familias, C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS\SAN JOSÉ DEL GUAVIARE\ZONA 2\Familias"
    rutas = [ruta.strip() for ruta in rutas_input.split(",") if ruta.strip()]  # Limpiar espacios y eliminar rutas vacías

    # Verificar que se haya ingresado al menos una ruta
    if not rutas:
        print(f"{Fore.RED}Error: No se ingresó ninguna ruta válida.{Style.RESET_ALL}")
        return

    # Solicitar la ruta del archivo Excel
    archivo_excel = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\REPORTES NACIONAL\20241020\f4.mo31.pp_formato_seguimiento_sfsc_v2_20241010.xlsx"

    # Verificar que el archivo Excel exista
    if not os.path.isfile(archivo_excel):
        print(f"{Fore.RED}Error: El archivo Excel '{archivo_excel}' no existe.{Style.RESET_ALL}")
        return

    # Llamar a la función principal con las rutas y el archivo Excel
    verificar_archivos(rutas, archivo_excel)

if __name__ == "__main__":
    main()
