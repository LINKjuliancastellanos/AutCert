"""
PROCESAMIENTO MASIVO DE CERTIFICACIONES - VERSION PLAYWRIGHT
=============================================================
Script batch que procesa TODAS las certificaciones usando Playwright:
1. Escanea todas las certificaciones en AyN, RyC y Transversal
2. Extrae el numero de HU de cada archivo
3. Busca las carpetas en Drive y extrae links de CPs
4. Actualiza cada Excel con los links correspondientes
5. Genera reporte final de resultados

Uso: py procesar_certificaciones_playwright.py
"""

import sys
import time
import os
import re
import json
import win32com.client
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener la raiz del proyecto AutCert
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
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

# URL raiz de Drive
DRIVE_ROOT_URL = "https://drive.google.com/drive/folders/1LOxZl_LY40jx-aq567TrWiSOo_QrO67S"

# Directorio para datos de usuario de Playwright (sesion persistente)
PLAYWRIGHT_USER_DATA = os.path.join(BASE_DIR, "datos", "cache", "playwright_profile")

# Archivo de reporte
REPORTE_DIR = os.path.join(BASE_DIR, "datos", "reportes")
os.makedirs(REPORTE_DIR, exist_ok=True)
os.makedirs(PLAYWRIGHT_USER_DATA, exist_ok=True)

# Tiempos
TIEMPO_CARGA_PAGINA = 3000  # ms
TIEMPO_SCROLL = 800  # ms
TIEMPO_BUSQUEDA = 4000  # ms

# ============================================
# CLASE PRINCIPAL
# ============================================

class ProcesadorMasivoPlaywright:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
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

        certificaciones.sort(key=lambda x: int(x['numero_hu']))
        self.log(f"Encontradas {len(certificaciones)} certificaciones")
        return certificaciones

    def iniciar_navegador(self):
        """Inicia Playwright con Chromium"""
        self.log("Iniciando Playwright...")
        self.playwright = sync_playwright().start()

        # Usar contexto persistente para mantener la sesion
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=PLAYWRIGHT_USER_DATA,
            headless=False,
            viewport={'width': 1280, 'height': 900},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        self.log("Playwright iniciado", "OK")

    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        self.log("Playwright cerrado", "OK")

    def navegar_a_drive(self):
        """Navega a la URL raiz de Drive"""
        self.page.goto(DRIVE_ROOT_URL)
        self.page.wait_for_timeout(TIEMPO_CARGA_PAGINA)

    def scroll_cargar_todo(self, total_esperado=0, max_intentos=50):
        """
        Scroll incremental para cargar todos los elementos.
        Implementa: seleccion de contenedor, forzar foco, scroll incremental, validacion.
        """
        try:
            # 1. Seleccionar el contenedor .PEfnhb
            container = self.page.locator('.PEfnhb')
            container.wait_for(state='visible', timeout=10000)

            # 2. Forzar foco con hover y click
            container.hover()
            container.click(force=True)
            self.page.wait_for_timeout(500)

            # 3. Scroll incremental
            previous_height = 0
            elementos_anteriores = 0
            intentos_sin_cambio = 0
            max_sin_cambio = 10

            for i in range(max_intentos):
                # Obtener altura actual del scroll
                current_height = container.evaluate("el => el.scrollHeight")

                # Hacer scroll incremental
                container.evaluate("el => el.scrollBy(0, 500)")

                # Esperar carga lazy
                self.page.wait_for_timeout(TIEMPO_SCROLL)

                # 4. Validacion - verificar scrollTop
                scroll_top = container.evaluate("el => el.scrollTop")

                # Contar CPs cargados
                elementos = self.page.locator('[data-tooltip*="CP"][data-tooltip*="Carpeta"]')
                elementos_actuales = elementos.count()

                # Si alcanzamos el objetivo, terminar
                if total_esperado > 0 and elementos_actuales >= total_esperado:
                    break

                # Verificar si hay cambios
                if current_height == previous_height and elementos_actuales == elementos_anteriores:
                    intentos_sin_cambio += 1
                    if intentos_sin_cambio >= max_sin_cambio:
                        break
                else:
                    intentos_sin_cambio = 0

                previous_height = current_height
                elementos_anteriores = elementos_actuales

            # Volver arriba
            container.evaluate("el => el.scrollTop = 0")
            self.page.wait_for_timeout(500)

            return elementos_actuales

        except Exception as e:
            self.log(f"Error en scroll: {e}", "WARN")
            return 0

    def buscar_y_entrar_carpeta_hu(self, numero_hu):
        """Busca la carpeta de una HU en Drive y entra"""
        try:
            # Buscar caja de busqueda
            search_box = self.page.locator('input[aria-label="Buscar en Drive"]')
            if not search_box.is_visible():
                search_box = self.page.locator('input[type="search"]')

            search_box.click()
            self.page.wait_for_timeout(300)
            search_box.fill('')
            self.page.wait_for_timeout(200)
            search_box.fill(numero_hu)
            self.page.wait_for_timeout(500)
            search_box.press('Enter')
            self.page.wait_for_timeout(TIEMPO_BUSQUEDA)

            # Buscar carpeta con el nombre exacto
            carpeta_selector = f'[data-tooltip*="Evidencias HU{numero_hu}"][data-tooltip*="Carpeta"]'
            carpeta = self.page.locator(carpeta_selector).first

            if carpeta.is_visible():
                # Doble clic para entrar
                carpeta.dblclick()
                self.page.wait_for_timeout(TIEMPO_CARGA_PAGINA + 2000)
                return True

            return False

        except Exception as e:
            return False

    def extraer_cps_de_carpeta(self, total_esperado=0):
        """Extrae todas las carpetas CP con sus links"""
        # Scroll para cargar todos los CPs
        self.scroll_cargar_todo(total_esperado=total_esperado, max_intentos=50)
        self.page.wait_for_timeout(1000)

        # Segundo pase para asegurar
        self.scroll_cargar_todo(total_esperado=total_esperado, max_intentos=20)
        self.page.wait_for_timeout(500)

        # Extraer CPs
        cps = {}
        elementos = self.page.locator('[data-tooltip*="CP"][data-tooltip*="Carpeta"]')
        count = elementos.count()

        for i in range(count):
            try:
                elem = elementos.nth(i)
                tooltip = elem.get_attribute('data-tooltip')
                data_id = elem.get_attribute('data-id')

                if tooltip and data_id:
                    match = re.search(r'CP\s*(\d+)', tooltip, re.IGNORECASE)
                    if match:
                        numero_cp = match.group(1)
                        link = f"https://drive.google.com/drive/folders/{data_id}"
                        cps[numero_cp] = link
            except:
                continue

        return cps

    def contar_tcs_en_excel(self, ruta_excel):
        """Cuenta cuantos Test Cases hay en el Excel"""
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            excel.Visible = False

            workbook = excel.Workbooks.Open(ruta_excel)
            worksheet = workbook.Worksheets(1)

            total_tcs = 0
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

                total_tcs += 1
                fila += 1

            workbook.Close(False)
            excel.Quit()
            return total_tcs

        except Exception as e:
            try:
                workbook.Close(False)
                excel.Quit()
            except:
                pass
            return 0

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
            # Contar TCs del Excel
            total_tcs = self.contar_tcs_en_excel(cert['ruta'])

            # Navegar a Drive
            self.navegar_a_drive()

            # Buscar y entrar a carpeta HU
            entro = self.buscar_y_entrar_carpeta_hu(numero_hu)

            if not entro:
                return {
                    'numero_hu': numero_hu,
                    'categoria': cert['categoria'],
                    'estado': 'NO_ENCONTRADA',
                    'mensaje': 'Carpeta no encontrada en Drive',
                    'links_agregados': 0
                }

            # Extraer CPs
            cps_links = self.extraer_cps_de_carpeta(total_esperado=total_tcs)

            if len(cps_links) == 0:
                return {
                    'numero_hu': numero_hu,
                    'categoria': cert['categoria'],
                    'estado': 'SIN_CPS',
                    'mensaje': f'No se encontraron CPs (esperados: {total_tcs})',
                    'links_agregados': 0,
                    'tcs_esperados': total_tcs
                }

            # Actualizar Excel
            resultado = self.actualizar_excel(cert['ruta'], cps_links, numero_hu)

            if resultado['exito']:
                return {
                    'numero_hu': numero_hu,
                    'categoria': cert['categoria'],
                    'estado': 'OK',
                    'mensaje': f"{resultado['completados']}/{total_tcs} links ({len(cps_links)} CPs en Drive)",
                    'links_agregados': resultado['completados'],
                    'cps_encontradas': len(cps_links),
                    'tcs_esperados': total_tcs
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
        """Genera reporte final en JSON"""
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

        nombre_reporte = f"reporte_masivo_{self.inicio.strftime('%Y%m%d_%H%M%S')}.json"
        ruta_reporte = os.path.join(REPORTE_DIR, nombre_reporte)

        with open(ruta_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)

        return ruta_reporte

    def mostrar_resumen(self):
        """Muestra resumen final"""
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

        estados = {}
        for r in self.resultados:
            estado = r['estado']
            estados[estado] = estados.get(estado, 0) + 1

        print("\n  Desglose por estado:")
        for estado, cantidad in sorted(estados.items()):
            simbolo = "+" if estado == "OK" else "!"
            print(f"    [{simbolo}] {estado}: {cantidad}")

        errores = [r for r in self.resultados if r['estado'] not in ['OK', 'SIN_CPS']]
        if errores:
            print("\n  Certificaciones con problemas:")
            for e in errores[:10]:
                print(f"    - HU{e['numero_hu']}: {e['mensaje'][:50]}")
            if len(errores) > 10:
                print(f"    ... y {len(errores) - 10} mas")

        print("=" * 70)

    def verificar_sesion(self):
        """Verifica si hay sesion de Google guardada"""
        # Verificar si existe el directorio de perfil con datos
        cookies_path = os.path.join(PLAYWRIGHT_USER_DATA, "Default", "Cookies")
        return os.path.exists(cookies_path) or os.path.exists(PLAYWRIGHT_USER_DATA)

    def ejecutar(self):
        """Ejecuta el procesamiento masivo"""
        print("=" * 70)
        print("   PROCESAMIENTO MASIVO DE CERTIFICACIONES (PLAYWRIGHT)")
        print("=" * 70)
        print()

        # Escanear certificaciones
        certificaciones = self.escanear_certificaciones()

        if len(certificaciones) == 0:
            self.log("No se encontraron certificaciones para procesar", "ERROR")
            return

        print()
        print(f"  Se procesaran {len(certificaciones)} certificaciones")
        print()

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
            self.iniciar_navegador()

            # Verificar sesion
            self.log("Navegando a Drive para verificar sesion...")
            self.navegar_a_drive()
            self.page.wait_for_timeout(3000)

            # Verificar si estamos logueados
            if "accounts.google.com" in self.page.url:
                self.log("Necesitas iniciar sesion en Google", "WARN")
                print("\n  Por favor inicia sesion en la ventana del navegador...")
                print("  Tienes 120 segundos para hacerlo.")
                self.page.wait_for_timeout(120000)

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

                self.page.wait_for_timeout(1000)

            print()

        except KeyboardInterrupt:
            self.log("Proceso interrumpido por usuario", "WARN")

        except Exception as e:
            self.log(f"Error durante procesamiento: {e}", "ERROR")

        finally:
            self.cerrar_navegador()

        ruta_reporte = self.generar_reporte()
        self.mostrar_resumen()

        print(f"\n  Reporte guardado en: {ruta_reporte}")
        print()


# ============================================
# MAIN
# ============================================

def main():
    procesador = ProcesadorMasivoPlaywright()
    procesador.ejecutar()
    print("\nPresiona ENTER para salir...")
    input()


if __name__ == "__main__":
    main()
