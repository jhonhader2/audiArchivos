import os
import pytesseract
from PIL import Image, ImageFilter
import shutil
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm 

# Especifica la ruta de instalación de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Solicitar rutas de las carpetas por consola
carpeta_imagenes = input("Introduce la ruta de la carpeta con las imágenes: ")
carpeta_meme = r'D:\BackUp\Memes'
carpeta_fotos_reales = r'D:\BackUp\Fotos'

# Comprobar que las rutas existen
if not os.path.exists(carpeta_meme):
    os.makedirs(carpeta_meme, exist_ok=True)

if not os.path.exists(carpeta_fotos_reales):
    os.makedirs(carpeta_fotos_reales, exist_ok=True)

def preprocesar_imagen(imagen):
    # Convertir a escala de grises
    imagen = imagen.convert('L')
    # Aplicar un filtro de desenfoque para reducir ruido
    imagen = imagen.filter(ImageFilter.MedianFilter(size=3))
    # Aplicar umbralización
    imagen = imagen.point(lambda x: 0 if x < 128 else 255, '1')
    return imagen

# Inicializar contadores
total_archivos = 0
archivos_movidos = 0
archivos_omitidos = 0

def procesar_imagen(archivo):
    global archivos_movidos, archivos_omitidos  # Usar contadores globales
    ruta_imagen = os.path.join(carpeta_imagenes, archivo)
    
    # Cargar y preprocesar la imagen
    imagen = Image.open(ruta_imagen)
    imagen = preprocesar_imagen(imagen)
    
    # Usar Tesseract para extraer texto
    texto_extraido = pytesseract.image_to_string(imagen)
    
    # Analizar el texto (cualquier tipo de letra o palabra)
    if texto_extraido.strip():  # Verifica si hay texto extraído
        destino = os.path.join(carpeta_meme, archivo)
        shutil.move(ruta_imagen, destino)
        archivos_movidos += 1  # Incrementar contador de archivos movidos
    else:
        destino = os.path.join(carpeta_fotos_reales, archivo)
        shutil.move(ruta_imagen, destino)
        archivos_omitidos += 1  # Incrementar contador de archivos omitidos

# Procesar cada imagen en la carpeta en paralelo
with ThreadPoolExecutor() as executor:
    archivos = []
    for root, dirs, files in os.walk(carpeta_imagenes):
        for f in files:
            if f.endswith(('.jpg', '.jpeg', '.png')):
                archivos.append(os.path.join(root, f))
    
    # Verificar si hay imágenes para procesar
    total_archivos = len(archivos)  # Contar archivos revisados
    if total_archivos == 0:
        print("No hay imágenes para procesar.")
    else:
        # Usar tqdm para mostrar el progreso con una descripción y tiempo estimado
        for _ in tqdm(executor.map(procesar_imagen, archivos), total=total_archivos, desc="Procesando imágenes", unit="imagen"):
            pass  # Solo se necesita para mostrar la barra de progreso

# Mostrar resultados finales
print(f"Total de archivos revisados: {total_archivos}")
print(f"Archivos movidos: {archivos_movidos}")
print(f"Archivos omitidos: {archivos_omitidos}")
