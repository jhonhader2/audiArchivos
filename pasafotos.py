import os
import pandas as pd
import re
from colorama import init, Fore

# Inicializar colorama
init(autoreset=True)

# Ruta del archivo Excel
ruta_excel = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Bases\FH_CONSOLIDADO.xlsx"

# Ruta donde se encuentran las carpetas de los municipios
ruta_municipios = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS"

# Leer el archivo Excel
df = pd.read_excel(ruta_excel)

# Filtrar el DataFrame para solo incluir filas donde "¿ACEPTÓ PERTENECER AL PROGRAMA?" es "SI"
df = df[df['¿ACEPTÓ PERTENECER AL PROGRAMA?'] == 'SI']

# Obtener la lista de carpetas existentes en la ruta de municipios
municipios_existentes = os.listdir(ruta_municipios)

# Inicializar contadores
total_encontradas_zona1 = 0
total_encontradas_zona2 = 0

# Iterar sobre cada fila del DataFrame filtrado
for index, row in df.iterrows():
    # Obtener el nombre del profesional
    nombre_profesional = row['NOMBRE COMPLETO (NOMBRES APELLIDOS) DEL RESPONSABLE DE LA BUSQUEDA Y VINCULACIÓN DE LA FAMILIA']
    
    # Determinar el número de documento a utilizar
    numero_documento = row['NÚMERO DE DOCUMENTO DE IDENTIDAD'] if pd.notna(row['NÚMERO DE DOCUMENTO DE IDENTIDAD']) else row['NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR']

    # Verificar si el número de documento es NaN
    if pd.isna(numero_documento):
        print(f"Falta el número de documento en la fila {index + 1}: {row}")
        continue
    else:
        # Extraer solo la parte numérica del número de documento
        numero_documento = str(numero_documento).replace('.0', '')  # Convertir a cadena y quitar ".0"
        numero_documento = re.match(r'(\d+)', numero_documento)  # Extraer solo la parte numérica
        if numero_documento:
            numero_documento = numero_documento.group(1)  # Obtener el grupo numérico
        else:
            print(f"Número de documento no válido en la fila {index + 1}: {row}")
            continue

    if not nombre_profesional:
        print(f"Falta información en la fila {index + 1}: {row}")
        continue

    # Crear carpetas para cada municipio existente
    for municipio in municipios_existentes:
        # Verificar la existencia de las carpetas "ZONA 1" y "ZONA 2"
        ruta_zona1 = os.path.join(ruta_municipios, municipio, "ZONA 1")
        ruta_zona2 = os.path.join(ruta_municipios, municipio, "ZONA 2")

        # Inicializar banderas de encontrado
        encontrado_zona1 = False
        encontrado_zona2 = False

        # Buscar en ZONA 1
        if os.path.exists(ruta_zona1):
            for carpeta_raiz, carpetas, _ in os.walk(ruta_zona1):
                # Verificar si alguna carpeta comienza con el número de documento
                for carpeta in carpetas:
                    if carpeta.startswith(numero_documento):
                        print(Fore.GREEN + f"La carpeta con el número de documento {numero_documento} existe en ZONA 1 para el profesional {nombre_profesional}.")
                        total_encontradas_zona1 += 1  # Incrementar contador
                        encontrado_zona1 = True
                        
                        # Buscar el archivo de imagen en la carpeta encontrada
                        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:  # Lista de extensiones de imagen
                            archivo_imagen = os.path.join(carpeta_raiz, carpeta, f"F_{numero_documento}{ext}")
                            if os.path.exists(archivo_imagen):
                                print(Fore.CYAN + f"El archivo de imagen {archivo_imagen} se encontró para el profesional {nombre_profesional}.")
                                break  # Salir del bucle si se encuentra el archivo
                        else:
                            print(f"No se encontró el archivo de imagen para el profesional {nombre_profesional}.")
                        
                        break  # Salir del bucle si se encuentra la carpeta
                if encontrado_zona1:
                    break  # Salir del bucle de os.walk si se encontró

        # Buscar en ZONA 2 solo si no se encontró en ZONA 1
        if not encontrado_zona1 and os.path.exists(ruta_zona2):
            for carpeta_raiz, carpetas, _ in os.walk(ruta_zona2):
                # Verificar si alguna carpeta comienza con el número de documento
                for carpeta in carpetas:
                    if carpeta.startswith(numero_documento):
                        print(Fore.GREEN + f"La carpeta con el número de documento {numero_documento} existe en ZONA 2 para el profesional {nombre_profesional}.")
                        total_encontradas_zona2 += 1  # Incrementar contador
                        encontrado_zona2 = True
                        
                        # Buscar el archivo de imagen en la carpeta encontrada
                        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:  # Lista de extensiones de imagen
                            archivo_imagen = os.path.join(carpeta_raiz, carpeta, f"F_{numero_documento}{ext}")
                            if os.path.exists(archivo_imagen):
                                print(Fore.CYAN + f"El archivo de imagen {archivo_imagen} se encontró para el profesional {nombre_profesional}.")
                                break  # Salir del bucle si se encuentra el archivo
                        else:
                            print(f"No se encontró el archivo de imagen para el profesional {nombre_profesional}.")
                        
                        break  # Salir del bucle si se encuentra la carpeta
                if encontrado_zona2:
                    break  # Salir del bucle de os.walk si se encontró

        # Si no se encontró en ninguna zona, mostrar mensaje de error
        if not encontrado_zona1 and not encontrado_zona2:
            print(Fore.RED + f"La carpeta con el número de documento {numero_documento} no existe en ninguna de las zonas para el profesional {nombre_profesional}.")

# Imprimir totales encontrados
print(f"\nTotal de carpetas encontradas en ZONA 1: {total_encontradas_zona1}")
print(f"Total de carpetas encontradas en ZONA 2: {total_encontradas_zona2}")
print("Verificación de carpetas completada.")
