import os
import pandas as pd
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
        numero_documento = str(numero_documento).replace('.0', '')  # Convertir a cadena y quitar ".0"

    if not nombre_profesional:
        print(f"Falta información en la fila {index + 1}: {row}")
        continue

    # Crear carpetas para cada municipio existente
    for municipio in municipios_existentes:
        # Verificar la existencia de las carpetas "ZONA 1" y "ZONA 2"
        ruta_zona1 = os.path.join(ruta_municipios, municipio, "ZONA 1")
        ruta_zona2 = os.path.join(ruta_municipios, municipio, "ZONA 2")

        # Buscar en ZONA 1
        if os.path.exists(ruta_zona1):
            encontrado_zona1 = False
            for carpeta_raiz, carpetas, _ in os.walk(ruta_zona1):
                # Verificar si la carpeta del número de documento existe
                ruta_familia_zona1 = os.path.join(carpeta_raiz, numero_documento)
                if os.path.exists(ruta_familia_zona1):
                    print(Fore.GREEN + f"La carpeta con el número de documento {numero_documento} existe en ZONA 1 para el profesional {nombre_profesional}.")
                    total_encontradas_zona1 += 1  # Incrementar contador
                    encontrado_zona1 = True
                    break  # Salir del bucle si se encuentra la carpeta

            if not encontrado_zona1:
                print(f"La carpeta con el número de documento {numero_documento} no existe en ZONA 1 para el profesional {nombre_profesional}.")

        # Buscar en ZONA 2
        if os.path.exists(ruta_zona2):
            encontrado_zona2 = False
            for carpeta_raiz, carpetas, _ in os.walk(ruta_zona2):
                # Verificar si la carpeta del número de documento existe
                ruta_familia_zona2 = os.path.join(carpeta_raiz, numero_documento)
                if os.path.exists(ruta_familia_zona2):
                    print(Fore.GREEN + f"La carpeta con el número de documento {numero_documento} existe en ZONA 2 para el profesional {nombre_profesional}.")
                    total_encontradas_zona2 += 1  # Incrementar contador
                    encontrado_zona2 = True
                    break  # Salir del bucle si se encuentra la carpeta

            if not encontrado_zona2:
                print(f"La carpeta con el número de documento {numero_documento} no existe en ZONA 2 para el profesional {nombre_profesional}.")

# Imprimir totales encontrados
print(f"\nTotal de carpetas encontradas en ZONA 1: {total_encontradas_zona1}")
print(f"Total de carpetas encontradas en ZONA 2: {total_encontradas_zona2}")
print("Verificación de carpetas completada.")
