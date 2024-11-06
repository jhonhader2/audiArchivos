import os
import pandas as pd
import re
from colorama import init, Fore
from abc import ABC, abstractmethod
from typing import List
from concurrent.futures import ThreadPoolExecutor

# Inicializar colorama
init(autoreset=True)

# Rutas de configuración
RUTA_EXCEL = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Bases\FH_CONSOLIDADO.xlsx"
RUTA_MUNICIPIOS = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS"

# Ruta donde se crearán las nuevas carpetas para la regional
ruta_regional = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SUPERVISIÓN\Carpeta_2\Evidencias Fotográficas\GUAVIARE"
os.makedirs(ruta_regional, exist_ok=True)

# Ruta donde se encuentran las carpetas de los municipios
ruta_municipios = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS"

# Función para crear carpetas
def crear_carpetas(municipio, nombre_profesional):
    # Crear la carpeta para el municipio en la ruta de la regional
    ruta_municipio = os.path.join(ruta_regional, municipio)
    os.makedirs(ruta_municipio, exist_ok=True)

    # Crear la carpeta para el profesional dentro de la carpeta del municipio
    ruta_profesional = os.path.join(ruta_municipio, nombre_profesional)
    os.makedirs(ruta_profesional, exist_ok=True)

# Leer el archivo Excel
df = pd.read_excel(RUTA_EXCEL)

# Obtener la lista de carpetas existentes en la ruta de municipios
municipios_existentes = os.listdir(ruta_municipios)

# Iterar sobre cada fila del DataFrame
for index, row in df.iterrows():
    # Obtener el nombre del profesional
    nombre_profesional = row['NOMBRE COMPLETO (NOMBRES APELLIDOS) DEL RESPONSABLE DE LA BUSQUEDA Y VINCULACIÓN DE LA FAMILIA']

    # Usar ThreadPoolExecutor para crear carpetas en paralelo
    with ThreadPoolExecutor() as executor:
        # Crear carpetas para cada municipio existente
        executor.map(lambda municipio: crear_carpetas(municipio, nombre_profesional), municipios_existentes)

print("Estructura de carpetas creada con éxito.")

# Interfaces para manejo de Excel
class IExcelReader(ABC):
    @abstractmethod
    def leer_excel(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def filtrar_aceptados(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

# Implementación del manejador de Excel
class ExcelHandler(IExcelReader):
    def __init__(self, ruta_excel: str):
        self.ruta_excel = ruta_excel

    def leer_excel(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.ruta_excel)
            return df
        except Exception as e:
            raise IOError(f"Error al leer el archivo Excel: {e}")

    def filtrar_aceptados(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            filtrado = df[df['¿ACEPTÓ PERTENECER AL PROGRAMA?'] == 'SI']
            return filtrado
        except KeyError:
            raise ValueError("La columna '¿ACEPTÓ PERTENECER AL PROGRAMA?' no existe en el DataFrame.")

# Interfaces para manejo de archivos
class IMunicipioHandler(ABC):
    @abstractmethod
    def obtener_municipios(self) -> list:
        pass

class IBusquedaHandler(ABC):
    @abstractmethod
    def buscar_carpeta_documento(self, ruta_zona: str, numero_documento: str) -> str:
        pass

    @abstractmethod
    def buscar_archivo_imagen(self, ruta_carpeta: str, numero_documento: str) -> str:
        pass

    @abstractmethod
    def existe_zona(self, municipio: str, zona_nombre: str) -> bool:
        pass

# Nueva interfaz que combina IMunicipioHandler e IBusquedaHandler
class IFileSystemHandler(IMunicipioHandler, IBusquedaHandler, ABC):
    pass

# Implementación del manejador de sistema de archivos
class FileSystemHandler(IFileSystemHandler):
    def __init__(self, ruta_municipios: str):
        self.ruta_municipios = ruta_municipios

    def obtener_municipios(self) -> list:
        try:
            return os.listdir(self.ruta_municipios)
        except Exception as e:
            raise IOError(f"Error al listar los municipios: {e}")

    def buscar_carpeta_documento(self, ruta_zona: str, numero_documento: str) -> str:
        for carpeta_raiz, carpetas, _ in os.walk(ruta_zona):
            for carpeta in carpetas:
                if carpeta.startswith(numero_documento):
                    return os.path.join(carpeta_raiz, carpeta)
        return ""

    def buscar_archivo_imagen(self, ruta_carpeta: str, numero_documento: str) -> str:
        extensiones = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        for ext in extensiones:
            archivo = os.path.join(ruta_carpeta, f"F_{numero_documento}{ext}")
            if os.path.exists(archivo):
                return archivo
        return ""

    def existe_zona(self, municipio: str, zona_nombre: str) -> bool:
        ruta_zona = os.path.join(self.ruta_municipios, municipio, zona_nombre)
        return os.path.exists(ruta_zona)

# Interfaces para el logging
class ILogger(ABC):
    @abstractmethod
    def info(self, mensaje: str) -> None:
        pass

    @abstractmethod
    def success(self, mensaje: str) -> None:
        pass

    @abstractmethod
    def error(self, mensaje: str) -> None:
        pass

    @abstractmethod
    def cyan(self, mensaje: str) -> None:
        pass

    @abstractmethod
    def yellow(self, mensaje: str) -> None:
        pass

# Implementación del logger usando colorama
class ColoramaLogger(ILogger):
    def info(self, mensaje: str) -> None:
        print(mensaje)

    def success(self, mensaje: str) -> None:
        print(Fore.GREEN + mensaje)

    def error(self, mensaje: str) -> None:
        print(Fore.RED + mensaje)

    def cyan(self, mensaje: str) -> None:
        print(Fore.CYAN + mensaje)

    def yellow(self, mensaje: str) -> None:
        print(Fore.YELLOW + mensaje)

# Interfaces para manejo de zonas
class IZona(ABC):
    @property
    @abstractmethod
    def nombre(self) -> str:
        pass

    @abstractmethod
    def buscar_carpeta(self, fs_handler: IBusquedaHandler, municipio: str, numero_documento: str) -> str:
        pass

class ZonaBase(IZona):
    def __init__(self, nombre: str):
        self._nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    def buscar_carpeta(self, fs_handler: IBusquedaHandler, municipio: str, numero_documento: str) -> str:
        ruta_zona = os.path.join(fs_handler.ruta_municipios, municipio, self.nombre)
        return fs_handler.buscar_carpeta_documento(ruta_zona, numero_documento)

class Zona1(ZonaBase):
    def __init__(self):
        super().__init__("ZONA 1")

class Zona2(ZonaBase):
    def __init__(self):
        super().__init__("ZONA 2")

# Interfaces para procesar documentos
class IProcessor(ABC):
    @abstractmethod
    def procesar(self) -> None:
        pass

# Clase que procesa la lógica de negocio
class Processor(IProcessor):
    def __init__(
        self,
        excel_reader: IExcelReader,
        fs_handler: IFileSystemHandler,
        logger: ILogger,
        zonas: List[IZona]
    ):
        self.excel_reader = excel_reader
        self.fs_handler = fs_handler
        self.logger = logger
        self.zonas = zonas
        self.total_por_zona = {zona.nombre: 0 for zona in zonas}

    def procesar(self) -> None:
        try:
            df = self.excel_reader.leer_excel()
            df = self.excel_reader.filtrar_aceptados(df)
            municipios = self.fs_handler.obtener_municipios()
        except Exception as e:
            self.logger.error(f"Error en la preparación de datos: {e}")
            return

        # Usar ThreadPoolExecutor para procesar las filas en paralelo
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.procesar_fila, row, index, municipios)
                for index, row in df.iterrows()
            ]
            # Esperar a que todas las tareas se completen
            for future in futures:
                future.result()  # Esto también manejará excepciones

        # Imprimir totales encontrados
        self.logger.info(f"\nTotal de carpetas encontradas por zona:")
        for zona, total in self.total_por_zona.items():
            self.logger.info(f"  {zona}: {total}")
        self.logger.info("Verificación de carpetas completada.")

    def procesar_fila(self, row: pd.Series, index: int, municipios: list) -> None:
        nombre_profesional = row.get(
            'NOMBRE COMPLETO (NOMBRES APELLIDOS) DEL RESPONSABLE DE LA BUSQUEDA Y VINCULACIÓN DE LA FAMILIA',
            ''
        ).strip()
        numero_documento = self.obtener_numero_documento(row)

        if not numero_documento:
            self.logger.error(
                f"Falta el número de documento en la fila {index + 1}: {row.to_dict()}"
            )
            return

        if not nombre_profesional:
            self.logger.error(
                f"Falta el nombre del profesional en la fila {index + 1}: {row.to_dict()}"
            )
            return

        self.buscar_en_zonas(municipios, numero_documento, nombre_profesional, row, index)

    def obtener_numero_documento(self, row: pd.Series) -> str:
        numero = row.get('NÚMERO DE DOCUMENTO DE IDENTIDAD')
        if pd.notna(numero):
            numero = str(numero).replace('.0', '').strip()
            match = re.match(r'(\d+)', numero)
            if match:
                return match.group(1)

        numero = row.get('NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR')
        if pd.notna(numero):
            numero = str(numero).replace('.0', '').strip()
            match = re.match(r'(\d+)', numero)
            if match:
                return match.group(1)

        return ""

    def buscar_en_zonas(
        self,
        municipios: list,
        numero_documento: str,
        nombre_profesional: str,
        row: pd.Series,
        index: int
    ) -> None:
        for zona in self.zonas:
            for municipio in municipios:
                if self.fs_handler.existe_zona(municipio, zona.nombre):
                    carpeta = zona.buscar_carpeta(self.fs_handler, municipio, numero_documento)
                    if carpeta:
                        self.logger.success(
                            f"La carpeta con el número de documento {numero_documento} existe en {zona.nombre} para el profesional {nombre_profesional}."
                        )
                        self.total_por_zona[zona.nombre] += 1
                        archivo = self.fs_handler.buscar_archivo_imagen(carpeta, numero_documento)
                        if archivo:
                            primer_nombre = str(
                                row.get('PRIMER NOMBRE DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR', '')
                            ).strip()
                            primer_apellido = str(
                                row.get('PRIMER APELLIDO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR', '')
                            ).strip()

                            if not primer_nombre:
                                primer_nombre = nombre_profesional.split()[0]
                            if not primer_apellido:
                                primer_apellido = nombre_profesional.split()[-1]

                            nuevo_nombre_archivo = f"{primer_nombre}_{primer_apellido}{os.path.splitext(archivo)[1]}"
                            self.logger.yellow(f"El nuevo nombre del archivo sería: {nuevo_nombre_archivo}")
                        else:
                            self.logger.error(
                                f"No se encontró el archivo de imagen para el profesional {nombre_profesional} en la carpeta: {carpeta}."
                            )
                        return

        self.logger.error(
            f"La carpeta con el número de documento {numero_documento} no existe en ninguna de las zonas para el profesional {nombre_profesional} en la fila {index + 1}."
        )

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
