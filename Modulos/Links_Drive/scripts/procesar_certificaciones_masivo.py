"""
PROCESAMIENTO MASIVO DE CERTIFICACIONES
=========================================
Script batch que procesa TODAS las certificaciones de forma automatica:
1. Escanea todas las certificaciones en AyN, RyC y Transversal
2. Extrae el numero de HU de cada archivo
3. Busca las carpetas en Drive y extrae links de CPs
4. Actualiza cada Excel con los links correspondientes
5. Genera reporte final de resultados

Uso: py procesar_certificaciones_masivo.py
"""

import sys
import time
import os
import re
import json
import win32com.client
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Importar configuracion
from configuracion_drive import (
    DRIVE_ROOT_URL,
    TIEMPO_CARGA_PAGINA,
    TIEMPO_SCROLL,
    TIEMPO_BUSQUEDA,
    MAX_INTENTOS_SCROLL,
    INTENTOS_SIN_CAMBIO,
    get_chrome_options,
    verificar_sesion_guardada,
    BASE_DIR
)

# Obtener la raiz del proyecto AutCert
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Agregar al path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuracion centralizada de rutas
from config_paths import CERTIFICACIONES_ROOT_STR

# ============================================
# CONFIGURACION
# ============================================

RUTA_CERTIFICACIONES = CERTIFICACIONES_ROOT_STR
CATEGORIAS = ['AyN', 'RyC', 'Transversal']

# Archivo de reporte
REPORTE_DIR = os.path.join(BASE_DIR, "datos", "reportes")
os.makedirs(REPORTE_DIR, exist_ok=True)

# ============================================
# CLASE PRINCIPAL
# ============================================

class ProcesadorMasivo:
    def __init__(self):
        self.driver = None
        self.resultados = []
        self.errores = []
        self.procesadas = 0
        self.exitosas = 0
        self.fallidas = 0
        self.inicio = datetime.now()

    def log(self, mensaje, nivel="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        simbolo = {"INFO": " ", "OK": "+", "ERROR": "!", "WARN": "?"}
        print(f"[{timestamp}] [{simbolo.get(nivel, ' ')}] {mensaje}")

    def log_progreso(self, actual, total, mensaje=""):
        """Muestra barra de progreso"""
        porcentaje = (actual / total) * 100 if total > 0 else 0
        barra_len = 30
        lleno = int(barra_len * actual / total) if total > 0 else 0
        barra = "=" * lleno + "-" * (barra_len - lleno)
        print(f"\r[{barra}] {actual}/{total} ({porcentaje:.1f}%) {mensaje}", end="", flush=True)

    def escanear_certificaciones(self):
        """Escanea todas las certificaciones disponibles"""
        self.log("Escaneando certificaciones...")
        certificaciones = []

        for categoria in CATEGORIAS:
            ruta_cat = os.path.join(RUTA_CERTIFICACIONES, categoria)
            if not os.path.exists(ruta_cat):
                self.log(f"Categoria {categoria} no existe", "WARN")
                continue

            for archivo in os.listdir(ruta_cat):
                if archivo.startswith("Certificacion_QA_") and archivo.endswith(".xlsx"):
                    # Extraer numero de HU
                    match = re.search(r'Certificacion_QA_(\d+)\.xlsx', archivo)
                    if match:
                        numero_hu = match.group(1)
                        ruta_completa = os.path.join(ruta_cat, archivo)
                        certificaciones.append({
                            'numero_hu': numero_hu,
                            'categoria': categoria,
                            'archivo': archivo,
                            'ruta': ruta_completa
                        })

        # Ordenar por numero de HU
        certificaciones.sort(key=lambda x: int(x['numero_hu']))

        self.log(f"Encontradas {len(certificaciones)} certificaciones")
        return certificaciones

    def iniciar_navegador(self):
        """Inicia el navegador Chrome"""
        self.log("Iniciando Chrome...")
        chrome_options = get_chrome_options()
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.log("Chrome iniciado", "OK")

    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()
            self.log("Chrome cerrado", "OK")

    def navegar_a_drive(self):
        """Navega a la URL raiz de Drive"""
        self.log("Navegando a Google Drive...")
        self.driver.get(DRIVE_ROOT_URL)
        time.sleep(TIEMPO_CARGA_PAGINA)

    def scroll_cargar_todo(self, max_intentos=30):
        """Scroll agresivo para cargar todos los elementos en Google Drive"""
        elementos_anteriores = 0
        intentos_sin_cambio = 0
        max_sin_cambio = 8  # Mas intentos antes de rendirse

        for i in range(max_intentos):
            # Metodo 1: Scroll en el contenedor principal de Drive
            try:
                # Buscar el contenedor scrolleable de Drive
                contenedor = self.driver.find_element(By.CSS_SELECTOR, "div.WYuW0e")
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", contenedor)
            except:
                pass

            time.sleep(0.3)

            # Metodo 2: Enviar teclas PAGE_DOWN multiples veces
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                for _ in range(3):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.2)
            except:
                pass

            # Metodo 3: Scroll con JavaScript en window
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(TIEMPO_SCROLL)

            # Contar elementos con data-tooltip que contengan "CP"
            elementos = self.driver.find_elements(By.CSS_SELECTOR, "[data-tooltip]")
            elementos_cp = [e for e in elementos if 'CP' in (e.get_attribute('data-tooltip') or '')]
            elementos_actuales = len(elementos_cp)

            if elementos_actuales == elementos_anteriores:
                intentos_sin_cambio += 1
                if intentos_sin_cambio >= max_sin_cambio:
                    break
            else:
                intentos_sin_cambio = 0

            elementos_anteriores = elementos_actuales

        # Volver arriba
        self.driver.execute_script("window.scrollTo(0, 0);")
        try:
            contenedor = self.driver.find_element(By.CSS_SELECTOR, "div.WYuW0e")
            self.driver.execute_script("arguments[0].scrollTop = 0", contenedor)
        except:
            pass

        time.sleep(0.5)

        return elementos_actuales

    def buscar_y_entrar_carpeta_hu(self, numero_hu):
        """Busca la carpeta de una HU en Drive y entra haciendo doble clic"""
        from selenium.webdriver.common.action_chains import ActionChains

        try:
            # Buscar caja de busqueda
            search_box = None
            selectores = [
                ("xpath", "//input[@aria-label='Buscar en Drive']"),
                ("xpath", "//input[@placeholder='Buscar en Drive']"),
                ("css", "input[aria-label='Buscar en Drive']"),
                ("css", "input[type='search']"),
            ]

            for tipo, selector in selectores:
                try:
                    if tipo == "xpath":
                        search_box = self.driver.find_element(By.XPATH, selector)
                    else:
                        search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if not search_box:
                return False

            # Limpiar y buscar
            search_box.click()
            time.sleep(0.3)
            search_box.clear()
            time.sleep(0.2)
            search_box.send_keys(numero_hu)
            time.sleep(0.5)
            search_box.send_keys(Keys.RETURN)
            time.sleep(TIEMPO_BUSQUEDA)

            # Buscar carpeta y hacer doble clic para entrar
            elementos = self.driver.find_elements(By.CSS_SELECTOR, "[data-tooltip]")

            for elem in elementos:
                try:
                    tooltip = elem.get_attribute('data-tooltip')
                    if tooltip and f"Evidencias HU{numero_hu}" in tooltip and "Carpeta" in tooltip:
                        # Hacer doble clic para entrar a la carpeta
                        actions = ActionChains(self.driver)
                        actions.double_click(elem).perform()
                        time.sleep(TIEMPO_CARGA_PAGINA + 2)
                        return True
                except:
                    continue

            return False

        except Exception as e:
            return False

    def extraer_cps_de_carpeta(self):
        """Extrae todas las carpetas CP con sus links"""
        # Scroll muy agresivo para cargar todas las CPs
        total_cps = self.scroll_cargar_todo(max_intentos=30)

        # Esperar a que se estabilice
        time.sleep(2)

        # Hacer un segundo pase de scroll por si acaso
        self.scroll_cargar_todo(max_intentos=10)
        time.sleep(1)

        elementos = self.driver.find_elements(By.CSS_SELECTOR, "[data-tooltip]")
        cps = {}

        for elem in elementos:
            try:
                tooltip = elem.get_attribute('data-tooltip')
                if tooltip and 'CP' in tooltip and 'Carpeta' in tooltip:
                    match = re.search(r'CP\s*(\d+)', tooltip, re.IGNORECASE)
                    if match:
                        numero_cp = match.group(1)
                        data_id = elem.get_attribute("data-id")
                        if data_id:
                            link = f"https://drive.google.com/drive/folders/{data_id}"
                            cps[numero_cp] = link
            except:
                continue

        return cps

    def actualizar_excel(self, ruta_excel, cps_links, numero_hu):
        """Actualiza el Excel con los links"""
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            excel.Visible = False

            workbook = excel.Workbooks.Open(ruta_excel)
            worksheet = workbook.Worksheets(1)

            completados = 0
            no_encontrados = 0

            fila = 21
            while True:
                tc_id = worksheet.Cells(fila, 3).Value

                if tc_id is None:
                    break

                tc_id_str = str(tc_id).strip()

                try:
                    if '.' in tc_id_str and tc_id_str.replace('.', '').isdigit():
                        tc_id_str = str(int(float(tc_id_str)))
                except:
                    pass

                if len(tc_id_str) > 10 or "CONCLUSION" in tc_id_str.upper():
                    break

                if tc_id_str in cps_links:
                    link = cps_links[tc_id_str]
                    worksheet.Cells(fila, 6).Value = link
                    completados += 1
                else:
                    no_encontrados += 1

                fila += 1

            workbook.Save()
            workbook.Close(False)
            excel.Quit()

            return {
                'completados': completados,
                'no_encontrados': no_encontrados,
                'exito': True
            }

        except Exception as e:
            try:
                workbook.Close(False)
                excel.Quit()
            except:
                pass
            return {
                'completados': 0,
                'no_encontrados': 0,
                'exito': False,
                'error': str(e)
            }

    def procesar_certificacion(self, cert):
        """Procesa una certificacion individual"""
        numero_hu = cert['numero_hu']

        try:
            # Volver a Drive raiz para buscar
            self.navegar_a_drive()

            # Buscar carpeta HU y entrar con doble clic
            entro = self.buscar_y_entrar_carpeta_hu(numero_hu)

            if not entro:
                return {
                    'numero_hu': numero_hu,
                    'categoria': cert['categoria'],
                    'estado': 'NO_ENCONTRADA',
                    'mensaje': 'Carpeta no encontrada en Drive',
                    'links_agregados': 0
                }

            # Ya estamos dentro de la carpeta, extraer CPs
            cps_links = self.extraer_cps_de_carpeta()

            if len(cps_links) == 0:
                return {
                    'numero_hu': numero_hu,
                    'categoria': cert['categoria'],
                    'estado': 'SIN_CPS',
                    'mensaje': 'No se encontraron carpetas CP',
                    'links_agregados': 0
                }

            # Actualizar Excel
            resultado = self.actualizar_excel(cert['ruta'], cps_links, numero_hu)

            if resultado['exito']:
                return {
                    'numero_hu': numero_hu,
                    'categoria': cert['categoria'],
                    'estado': 'OK',
                    'mensaje': f"{resultado['completados']} links, {resultado['no_encontrados']} sin match",
                    'links_agregados': resultado['completados'],
                    'cps_encontradas': len(cps_links)
                }
            else:
                return {
                    'numero_hu': numero_hu,
                    'categoria': cert['categoria'],
                    'estado': 'ERROR_EXCEL',
                    'mensaje': resultado.get('error', 'Error desconocido'),
                    'links_agregados': 0
                }

        except Exception as e:
            return {
                'numero_hu': numero_hu,
                'categoria': cert['categoria'],
                'estado': 'ERROR',
                'mensaje': str(e),
                'links_agregados': 0
            }

    def generar_reporte(self):
        """Genera reporte final en JSON y consola"""
        duracion = datetime.now() - self.inicio

        reporte = {
            'fecha': self.inicio.strftime("%Y-%m-%d %H:%M:%S"),
            'duracion_segundos': duracion.total_seconds(),
            'duracion_formato': str(duracion).split('.')[0],
            'total_procesadas': self.procesadas,
            'exitosas': self.exitosas,
            'fallidas': self.fallidas,
            'resultados': self.resultados
        }

        # Guardar JSON
        nombre_reporte = f"reporte_masivo_{self.inicio.strftime('%Y%m%d_%H%M%S')}.json"
        ruta_reporte = os.path.join(REPORTE_DIR, nombre_reporte)

        with open(ruta_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)

        return ruta_reporte

    def mostrar_resumen(self):
        """Muestra resumen final en consola"""
        duracion = datetime.now() - self.inicio

        print("\n")
        print("=" * 70)
        print("                    RESUMEN DE PROCESAMIENTO")
        print("=" * 70)
        print(f"  Total certificaciones procesadas: {self.procesadas}")
        print(f"  Exitosas:                         {self.exitosas}")
        print(f"  Fallidas:                         {self.fallidas}")
        print(f"  Duracion:                         {str(duracion).split('.')[0]}")
        print("=" * 70)

        # Desglose por estado
        estados = {}
        for r in self.resultados:
            estado = r['estado']
            if estado not in estados:
                estados[estado] = 0
            estados[estado] += 1

        print("\n  Desglose por estado:")
        for estado, cantidad in sorted(estados.items()):
            simbolo = "+" if estado == "OK" else "!"
            print(f"    [{simbolo}] {estado}: {cantidad}")

        # Mostrar errores si hay
        errores = [r for r in self.resultados if r['estado'] not in ['OK', 'SIN_CPS']]
        if errores:
            print("\n  Certificaciones con problemas:")
            for e in errores[:10]:  # Mostrar max 10
                print(f"    - HU{e['numero_hu']}: {e['mensaje'][:50]}")
            if len(errores) > 10:
                print(f"    ... y {len(errores) - 10} mas")

        print("=" * 70)

    def ejecutar(self):
        """Ejecuta el procesamiento masivo"""
        print("=" * 70)
        print("       PROCESAMIENTO MASIVO DE CERTIFICACIONES")
        print("=" * 70)
        print()

        # Verificar sesion
        if not verificar_sesion_guardada():
            print("[!] NO SE DETECTO SESION GUARDADA")
            print("    Por favor ejecuta primero: 1_Iniciar_Sesion.bat")
            print()
            respuesta = input("    Continuar de todas formas? (s/n): ").strip().lower()
            if respuesta != 's':
                return

        # Escanear certificaciones
        certificaciones = self.escanear_certificaciones()

        if len(certificaciones) == 0:
            self.log("No se encontraron certificaciones para procesar", "ERROR")
            return

        print()
        print(f"  Se procesaran {len(certificaciones)} certificaciones")
        print()

        # Mostrar preview
        print("  Preview de certificaciones:")
        for cat in CATEGORIAS:
            cantidad = len([c for c in certificaciones if c['categoria'] == cat])
            print(f"    - {cat}: {cantidad}")
        print()

        respuesta = input("  Iniciar procesamiento masivo? (s/n): ").strip().lower()
        if respuesta != 's':
            print("  Cancelado por usuario")
            return

        print()

        try:
            # Iniciar navegador
            self.iniciar_navegador()

            # Procesar cada certificacion
            total = len(certificaciones)

            for i, cert in enumerate(certificaciones, 1):
                self.log_progreso(i, total, f"HU{cert['numero_hu']}")

                resultado = self.procesar_certificacion(cert)
                self.resultados.append(resultado)
                self.procesadas += 1

                if resultado['estado'] == 'OK':
                    self.exitosas += 1
                else:
                    self.fallidas += 1

                # Pausa breve entre certificaciones
                time.sleep(1)

            print()  # Nueva linea despues de barra de progreso

        except KeyboardInterrupt:
            self.log("Proceso interrumpido por usuario", "WARN")

        except Exception as e:
            self.log(f"Error durante procesamiento: {e}", "ERROR")

        finally:
            self.cerrar_navegador()

        # Generar reporte
        ruta_reporte = self.generar_reporte()

        # Mostrar resumen
        self.mostrar_resumen()

        print(f"\n  Reporte guardado en: {ruta_reporte}")
        print()


# ============================================
# MAIN
# ============================================

def main():
    procesador = ProcesadorMasivo()
    procesador.ejecutar()
    print("\nPresiona ENTER para salir...")
    input()


if __name__ == "__main__":
    main()
