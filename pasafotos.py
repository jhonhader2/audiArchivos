import os
import pandas as pd
import re
from colorama import init, Fore
from abc import ABC, abstractmethod

# Inicializar colorama
init(autoreset=True)

# Rutas de configuración
RUTA_EXCEL = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Bases\FH_CONSOLIDADO.xlsx"
RUTA_MUNICIPIOS = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS"

# Clases de manejo de Excel
class ExcelHandler:
    def __init__(self, ruta_excel):
        self.ruta_excel = ruta_excel
        self.df = None

    def leer_excel(self):
        try:
            self.df = pd.read_excel(self.ruta_excel)
            return self.df
        except Exception as e:
            raise IOError(f"Error al leer el archivo Excel: {e}")

    def filtrar_aceptados(self):
        if self.df is not None:
            self.df = self.df[self.df['¿ACEPTÓ PERTENECER AL PROGRAMA?'] == 'SI']
            return self.df
        else:
            raise ValueError("El DataFrame está vacío. Debe leer el Excel primero.")

# Interfaces para manejo de archivos
class IMunicipioHandler(ABC):
    @abstractmethod
    def obtener_municipios(self):
        pass

class IBusquedaHandler(ABC):
    @abstractmethod
    def buscar_carpeta_documento(self, ruta_zona, numero_documento):
        pass

    @abstractmethod
    def buscar_archivo_imagen(self, ruta_carpeta, numero_documento):
        pass

    @abstractmethod
    def existe_zona(self, municipio, zona_nombre):
        pass

# Implementación del manejador de sistema de archivos
class FileSystemHandler(IMunicipioHandler, IBusquedaHandler):
    def __init__(self, ruta_municipios):
        self.ruta_municipios = ruta_municipios

    def obtener_municipios(self):
        try:
            return os.listdir(self.ruta_municipios)
        except Exception as e:
            raise IOError(f"Error al listar los municipios: {e}")

    def buscar_carpeta_documento(self, ruta_zona, numero_documento):
        for carpeta_raiz, carpetas, _ in os.walk(ruta_zona):
            for carpeta in carpetas:
                if carpeta.startswith(str(numero_documento)):
                    return os.path.join(carpeta_raiz, carpeta)
        return None

    def buscar_archivo_imagen(self, ruta_carpeta, numero_documento):
        extensiones = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        for ext in extensiones:
            archivo = os.path.join(ruta_carpeta, f"F_{numero_documento}{ext}")
            if os.path.exists(archivo):
                return archivo
        return None

    def existe_zona(self, municipio, zona_nombre):
        ruta_zona = os.path.join(self.ruta_municipios, municipio, zona_nombre)
        return os.path.exists(ruta_zona)

# Interfaces para el logging
class ILogger(ABC):
    @abstractmethod
    def info(self, mensaje):
        pass

    @abstractmethod
    def success(self, mensaje):
        pass

    @abstractmethod
    def error(self, mensaje):
        pass

    @abstractmethod
    def cyan(self, mensaje):
        pass

    @abstractmethod
    def yellow(self, mensaje):
        pass

# Implementación del logger usando colorama
class ColoramaLogger(ILogger):
    def info(self, mensaje):
        print(mensaje)

    def success(self, mensaje):
        print(Fore.GREEN + mensaje)

    def error(self, mensaje):
        print(Fore.RED + mensaje)

    def cyan(self, mensaje):
        print(Fore.CYAN + mensaje)

    def yellow(self, mensaje):
        print(Fore.YELLOW + mensaje)

# Clases para manejar diferentes zonas
class Zona(ABC):
    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def buscar_carpeta(self, fs_handler, municipio, numero_documento):
        pass

class Zona1(Zona):
    def __init__(self):
        super().__init__("ZONA 1")

    def buscar_carpeta(self, fs_handler, municipio, numero_documento):
        ruta_zona = os.path.join(fs_handler.ruta_municipios, municipio, self.nombre)
        return fs_handler.buscar_carpeta_documento(ruta_zona, numero_documento)

class Zona2(Zona):
    def __init__(self):
        super().__init__("ZONA 2")

    def buscar_carpeta(self, fs_handler, municipio, numero_documento):
        ruta_zona = os.path.join(fs_handler.ruta_municipios, municipio, self.nombre)
        return fs_handler.buscar_carpeta_documento(ruta_zona, numero_documento)

# Clase que procesa la lógica de negocio
class Processor:
    def __init__(self, excel_handler: ExcelHandler, fs_handler: FileSystemHandler, logger: ILogger, zonas: list):
        self.excel_handler = excel_handler
        self.fs_handler = fs_handler
        self.logger = logger
        self.zonas = zonas
        self.total_por_zona = {zona.nombre: 0 for zona in zonas}

    def procesar(self):
        try:
            df = self.excel_handler.leer_excel()
            df = self.excel_handler.filtrar_aceptados()
            municipios = self.fs_handler.obtener_municipios()
        except Exception as e:
            self.logger.error(f"Error en la preparación de datos: {e}")
            return

        for index, row in df.iterrows():
            nombre_profesional = row.get('NOMBRE COMPLETO (NOMBRES APELLIDOS) DEL RESPONSABLE DE LA BUSQUEDA Y VINCULACIÓN DE LA FAMILIA', '').strip()
            numero_documento = self.obtener_numero_documento(row)

            if not numero_documento:
                self.logger.error(f"Falta el número de documento en la fila {index + 1}: {row.to_dict()}")
                continue

            if not nombre_profesional:
                self.logger.error(f"Falta el nombre del profesional en la fila {index + 1}: {row.to_dict()}")
                continue

            self.buscar_en_zonas(municipios, numero_documento, nombre_profesional, row, index)

        # Imprimir totales encontrados
        self.logger.info(f"\nTotal de carpetas encontradas por zona:")
        for zona, total in self.total_por_zona.items():
            self.logger.info(f"  {zona}: {total}")
        self.logger.info("Verificación de carpetas completada.")

    def obtener_numero_documento(self, row):
        # Priorizar 'NÚMERO DE DOCUMENTO DE IDENTIDAD' si está disponible
        numero = row.get('NÚMERO DE DOCUMENTO DE IDENTIDAD')
        if pd.notna(numero):
            numero = str(numero).replace('.0', '').strip()
            match = re.match(r'(\d+)', numero)
            if match:
                return match.group(1)
        
        # Si no está disponible, usar 'NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR'
        numero = row.get('NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR')
        if pd.notna(numero):
            numero = str(numero).replace('.0', '').strip()
            match = re.match(r'(\d+)', numero)
            if match:
                return match.group(1)
        
        return None

    def buscar_en_zonas(self, municipios, numero_documento, nombre_profesional, row, index):
        encontrado = False
        for zona in self.zonas:
            for municipio in municipios:
                if self.fs_handler.existe_zona(municipio, zona.nombre):
                    carpeta = zona.buscar_carpeta(self.fs_handler, municipio, numero_documento)
                    if carpeta:
                        self.logger.success(f"La carpeta con el número de documento {numero_documento} existe en {zona.nombre} para el profesional {nombre_profesional}.")
                        self.total_por_zona[zona.nombre] += 1
                        archivo = self.fs_handler.buscar_archivo_imagen(carpeta, numero_documento)
                        if archivo:
                            #self.logger.cyan(f"El archivo de imagen {archivo} se encontró para el profesional {nombre_profesional}.")
                            
                            # Obtener los nombres del beneficiario, priorizando los campos
                            primer_nombre = str(row.get('PRIMER NOMBRE DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR', '')).strip()
                            primer_apellido = str(row.get('PRIMER APELLIDO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR', '')).strip()
                            
                            # Si no se encuentra el primer nombre o apellido, se puede usar el nombre profesional
                            if not primer_nombre:
                                primer_nombre = nombre_profesional.split()[0]  # Usar el primer nombre del profesional si no hay
                            if not primer_apellido:
                                primer_apellido = nombre_profesional.split()[-1]  # Usar el último apellido del profesional si no hay
                            
                            # Construir el nuevo nombre del archivo
                            nuevo_nombre_archivo = f"{primer_nombre}_{primer_apellido}{os.path.splitext(archivo)[1]}"
                            self.logger.yellow(f"El nuevo nombre del archivo sería: {nuevo_nombre_archivo}")
                        else:
                            self.logger.error(f"No se encontró el archivo de imagen para el profesional {nombre_profesional} en la carpeta: {carpeta}.")
                        encontrado = True
                        break  # Salir del loop de municipios si se encuentra
            if encontrado:
                break  # Salir del loop de zonas si se encuentra

        if not encontrado:
            self.logger.error(f"La carpeta con el número de documento {numero_documento} no existe en ninguna de las zonas para el profesional {nombre_profesional} en la fila {index + 1}.")

# Función principal
def main():
    # Instanciar las clases
    excel_handler = ExcelHandler(RUTA_EXCEL)
    fs_handler = FileSystemHandler(RUTA_MUNICIPIOS)
    logger = ColoramaLogger()
    zonas = [Zona1(), Zona2()]

    # Instanciar el procesador
    processor = Processor(excel_handler, fs_handler, logger, zonas)

    # Ejecutar el procesamiento
    processor.procesar()

if __name__ == "__main__":
    main()
