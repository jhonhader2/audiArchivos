import os
import pandas as pd

# Ruta del archivo Excel
ruta_excel = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Bases\FH_CONSOLIDADO.xlsx"

# Ruta donde se crearán las nuevas carpetas para la regional
ruta_regional = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SUPERVISIÓN\Carpeta_2\Evidencias Fotográficas\GUAVIARE"
os.makedirs(ruta_regional, exist_ok=True)

# Ruta donde se encuentran las carpetas de los municipios
ruta_municipios = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS"

# Leer el archivo Excel
df = pd.read_excel(ruta_excel)

# Obtener la lista de carpetas existentes en la ruta de municipios
municipios_existentes = os.listdir(ruta_municipios)

# Iterar sobre cada fila del DataFrame
for index, row in df.iterrows():
    # Obtener el nombre del profesional
    nombre_profesional = row['NOMBRE COMPLETO (NOMBRES APELLIDOS) DEL RESPONSABLE DE LA BUSQUEDA Y VINCULACIÓN DE LA FAMILIA']

    # Crear carpetas para cada municipio existente
    for municipio in municipios_existentes:
        # Crear la carpeta para el municipio en la ruta de la regional
        ruta_municipio = os.path.join(ruta_regional, municipio)
        os.makedirs(ruta_municipio, exist_ok=True)

        # Crear la carpeta para el profesional dentro de la carpeta del municipio
        ruta_profesional = os.path.join(ruta_municipio, nombre_profesional)
        os.makedirs(ruta_profesional, exist_ok=True)

        # Aquí puedes agregar el código para mover o guardar las fotos en la carpeta correspondiente
        # Por ejemplo: shutil.move(foto_path, ruta_profesional)

print("Estructura de carpetas creada con éxito.")
