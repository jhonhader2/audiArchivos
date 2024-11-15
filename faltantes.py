import os
import re
from typing import List, Dict, DefaultDict
from collections import defaultdict
import pandas as pd
from colorama import Fore, Style, init

# Inicializar colorama para colorear la salida en la consola
init(autoreset=True)


class ExcelDataLoader:
    """
    Clase responsable de cargar y procesar los datos del archivo Excel.
    """

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.profesionales_dict: DefaultDict[str, List[str]] = defaultdict(list)

    
    def load_data(self) -> bool:
        try:
            # Cargar la hoja 'Consolidado'
            df = pd.read_excel(self.excel_path, sheet_name='CONSOLIDADO')
            df.columns = df.columns.str.strip()
            
            # Mantener las columnas relevantes, incluyendo el nuevo campo
            df = df[
                [
                    "NÚMERO DE DOCUMENTO DE IDENTIDAD",
                    "NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR",
                    "NOMBRE COMPLETO (NOMBRES APELLIDOS) DEL RESPONSABLE DE LA BUSQUEDA Y VINCULACIÓN DE LA FAMILIA",
                    "¿ACEPTÓ PERTENECER AL PROGRAMA?"
                ]
            ]
            
            # Eliminar filas donde ambas columnas clave son NaN
            df.dropna(subset=[
                "NÚMERO DE DOCUMENTO DE IDENTIDAD",
                "NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR"
            ], how='all', inplace=True)
            
            # Filtrar los registros donde "¿ACEPTÓ PERTENECER AL PROGRAMA?" es "SI"
            df["¿ACEPTÓ PERTENECER AL PROGRAMA?"] = df["¿ACEPTÓ PERTENECER AL PROGRAMA?"].astype(str).str.strip().str.upper()
            df = df[df["¿ACEPTÓ PERTENECER AL PROGRAMA?"] == "SI"]
            
            # Asegurarse de que los números de documento sean cadenas sin decimales
            df["NÚMERO DE DOCUMENTO DE IDENTIDAD"] = df["NÚMERO DE DOCUMENTO DE IDENTIDAD"].astype(str).str.split('.').str[0]
            df["NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR"] = df["NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR"].astype(str).str.split('.').str[0]
            
            # Contadores para los registros
            contador_identidad = 0
            contador_beneficiario = 0
            
            # Poblar el diccionario de profesionales
            for _, row in df.iterrows():
                identificador_identidad = str(row["NÚMERO DE DOCUMENTO DE IDENTIDAD"]).strip()
                identificador_beneficiario = str(row["NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR"]).strip()
                profesional = str(row["NOMBRE COMPLETO (NOMBRES APELLIDOS) DEL RESPONSABLE DE LA BUSQUEDA Y VINCULACIÓN DE LA FAMILIA"]).strip()
        
                if identificador_identidad and identificador_identidad.lower() != 'nan':
                    identificador = identificador_identidad
                    contador_identidad += 1
                elif identificador_beneficiario and identificador_beneficiario.lower() != 'nan':
                    identificador = identificador_beneficiario
                    contador_beneficiario += 1
                else:
                    continue  # No hay identificador válido
        
                # Agregar al diccionario de profesionales
                self.profesionales_dict[profesional].append(identificador)
        
            # Mostrar los contadores
            print(f"Total de registros con 'NÚMERO DE DOCUMENTO DE IDENTIDAD': {contador_identidad}")
            print(f"Total de registros con 'NUMERO DE DOCUMENTO DEL BENEFICIARIO QUE EJERCE LA JEFATURA DEL SISTEMA FAMILIAR': {contador_beneficiario}")
        
            return True
        except FileNotFoundError:
            print(
                f"{Fore.RED}Error: No se encontró el archivo Excel '{self.excel_path}'.{Style.RESET_ALL}"
            )
        except KeyError as e:
            print(
                f"{Fore.RED}Error: La columna '{e.args[0]}' no se encontró en el archivo Excel.{Style.RESET_ALL}"
            )
            print("Verifique que las columnas tengan los nombres correctos.")
        except Exception as e:
            print(f"{Fore.RED}Error al leer el archivo Excel: {e}{Style.RESET_ALL}")
        return False

    def get_profesionales_dict(self) -> DefaultDict[str, List[str]]:
        return self.profesionales_dict


class FileSystemChecker:
    """
    Clase responsable de verificar la existencia de carpetas y archivos en el sistema de archivos.
    """

    def __init__(self, rutas: List[str], profesionales_dict: DefaultDict[str, List[str]]):
        self.rutas = rutas
        self.profesionales_dict = profesionales_dict
        self.total_carpetas_esperadas = sum(len(ids) for ids in profesionales_dict.values())
        self.total_carpetas_encontradas = 0
        self.total_carpetas_no_encontradas = 0
        self.archivos_faltantes: DefaultDict[str, Dict[str, List[str]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.carpetas_no_encontradas: DefaultDict[str, List[str]] = defaultdict(list)

    def verificar_archivos(self):
        for profesional, identificadores in self.profesionales_dict.items():
            for identificador in identificadores:
                carpeta_encontrada, ruta_carpeta_encontrada = self._buscar_carpeta(identificador)
                if not carpeta_encontrada:
                    self.carpetas_no_encontradas[profesional].append(identificador)
                    self.total_carpetas_no_encontradas += 1
                    continue
                self.total_carpetas_encontradas += 1
                self._verificar_archivos_en_carpeta(
                    profesional, identificador, ruta_carpeta_encontrada
                )

    def _buscar_carpeta(self, identificador: str):
        for ruta in self.rutas:
            if not os.path.exists(ruta):
                print(f"{Fore.RED}Error: La ruta '{ruta}' no existe.{Style.RESET_ALL}")
                continue
            subcarpetas = [
                d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))
            ]
            for nombre_carpeta in subcarpetas:
                identificador_carpeta = re.split(r"[_ ]+", nombre_carpeta.strip())[0]
                if identificador_carpeta == identificador:
                    return True, os.path.join(ruta, nombre_carpeta)
        return False, ""

    def _verificar_archivos_en_carpeta(
        self, profesional: str, identificador: str, ruta_carpeta: str
    ):
        archivos = os.listdir(ruta_carpeta)
        archivos_normalizados = [f.lower() for f in archivos]
        # Nombres de archivos según su código original
        archivos_requeridos = [
            f"av_{identificador}.pdf",
            f"fc_{identificador}.pdf",
        ]
        formatos_imagen = [".jpeg", ".jpg", ".png", ".gif", ".bmp"]
        foto_encontrada = any(
            f"f_{identificador}{ext}".lower() in archivos_normalizados
            for ext in formatos_imagen
        )
        faltantes = []
        if not foto_encontrada:
            faltantes.append(f"F_{identificador}.[ext]")
        for archivo in archivos_requeridos:
            if archivo.lower() not in archivos_normalizados:
                faltantes.append(archivo.upper())

        # Registrar los archivos faltantes, incluso si no hay ninguno
        self.archivos_faltantes[profesional][identificador] = faltantes


class ReportGenerator:
    """
    Clase responsable de generar y mostrar el reporte de verificación.
    """

    def __init__(
        self,
        total_carpetas_esperadas: int,
        total_carpetas_encontradas: int,
        total_carpetas_no_encontradas: int,
        profesionales_dict: DefaultDict[str, List[str]],
        archivos_faltantes: DefaultDict[str, Dict[str, List[str]]],
        carpetas_no_encontradas: DefaultDict[str, List[str]],
    ):
        self.total_carpetas_esperadas = total_carpetas_esperadas
        self.total_carpetas_encontradas = total_carpetas_encontradas
        self.total_carpetas_no_encontradas = total_carpetas_no_encontradas
        self.profesionales_dict = profesionales_dict
        self.archivos_faltantes = archivos_faltantes
        self.carpetas_no_encontradas = carpetas_no_encontradas

    def generar_reporte(self):
        self._mostrar_resumen_general()
        self._generar_mensajes_pendientes()
        print(f"\n{Fore.BLUE}Proceso completado.{Style.RESET_ALL}")

    def _mostrar_resumen_general(self):
        print(f"\n{Fore.BLUE}Resumen General:{Style.RESET_ALL}")
        print(f"Total de carpetas esperadas según el Excel: {self.total_carpetas_esperadas}")
        print(f"Total de carpetas encontradas: {self.total_carpetas_encontradas}")
        print(f"Total de carpetas no encontradas: {self.total_carpetas_no_encontradas}")

    def _generar_mensajes_pendientes(self):
        print(f"\n{Fore.BLUE}Pendientes agrupados por Profesional:{Style.RESET_ALL}")
        for profesional in self.profesionales_dict.keys():
            print(f"\n{Style.RESET_ALL}Profesional: {profesional}{Style.RESET_ALL}")
            total_carpetas_faltantes = 0
            total_archivos_faltantes = 0

            # Manejar carpetas no encontradas
            if self.carpetas_no_encontradas.get(profesional):
                print(
                    f"{Fore.RED}Carpetas no encontradas para {profesional}:{Style.RESET_ALL}"
                )
                for identificador in self.carpetas_no_encontradas[profesional]:
                    print(f"  - {identificador}")
                    total_carpetas_faltantes += 1

            # Manejar archivos faltantes o completos
            if self.archivos_faltantes.get(profesional):
                for identificador, faltantes in self.archivos_faltantes[profesional].items():
                    if not faltantes:
                        print(
                            f"{Fore.GREEN}Todos los archivos están presentes para la carpeta {Fore.CYAN}{identificador}{Style.RESET_ALL}."
                        )
                    else:
                        print(
                            f"{Fore.YELLOW}Archivos faltantes en la carpeta {Fore.CYAN}{identificador}{Style.RESET_ALL}:"
                        )
                        total_archivos_faltantes += len(faltantes)
                        for archivo_faltante in faltantes:
                            print(f"    * {Fore.YELLOW}{archivo_faltante}{Style.RESET_ALL}")

            if not total_carpetas_faltantes and not total_archivos_faltantes:
                print(
                    f"{Fore.GREEN}No hay pendientes para el profesional {profesional}.{Style.RESET_ALL}"
                )

            print(
                f"{Fore.YELLOW}Total de pendientes para {Style.RESET_ALL}{profesional}{Fore.YELLOW}{Style.RESET_ALL}: "
                f"{total_carpetas_faltantes} carpetas y {total_archivos_faltantes} archivos.{Style.RESET_ALL}"
            )


class VerificadorArchivos:
    """
    Clase principal que coordina la carga de datos, verificación y generación de reportes.
    """

    def __init__(self, rutas: List[str], archivo_excel: str):
        self.rutas = rutas
        self.archivo_excel = archivo_excel

    def ejecutar(self):
        loader = ExcelDataLoader(self.archivo_excel)
        if not loader.load_data():
            return
        checker = FileSystemChecker(self.rutas, loader.get_profesionales_dict())
        checker.verificar_archivos()
        report = ReportGenerator(
            checker.total_carpetas_esperadas,
            checker.total_carpetas_encontradas,
            checker.total_carpetas_no_encontradas,
            loader.get_profesionales_dict(),
            checker.archivos_faltantes,
            checker.carpetas_no_encontradas,
        )
        report.generar_reporte()


def main():
    print("=== Verificación de Archivos ===\n")
    rutas_input = (
        r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS\SAN JOSÉ DEL GUAVIARE\ZONA 1\Familias, "
        r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS\SAN JOSÉ DEL GUAVIARE\ZONA 2\Familias,  "
        r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS\CALAMAR\ZONA 1\Familias, "
        r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Repositorio\MUNICIPIOS\EL RETORNO\ZONA 1\Familias"
    )
    rutas = [ruta.strip() for ruta in rutas_input.split(",") if ruta.strip()]
    if not rutas:
        print(f"{Fore.RED}Error: No se ingresó ninguna ruta válida.{Style.RESET_ALL}")
        return
    archivo_excel = r"C:\Users\jhonh\OneDrive - Instituto Colombiano de Bienestar Familiar\SFSC\2024\Bases\FH_CONSOLIDADO.xlsx"
    if not os.path.isfile(archivo_excel):
        print(f"{Fore.RED}Error: El archivo Excel '{archivo_excel}' no existe.{Style.RESET_ALL}")
        return
    verificador = VerificadorArchivos(rutas, archivo_excel)
    verificador.ejecutar()


if __name__ == "__main__":
    main()
