"""
COMPLETAR UNA HU - VERSION PLAYWRIGHT
======================================
Script para completar UNA certificacion usando Playwright.
Permite probar el scroll antes de ejecutar el masivo.

Uso: py completar_hu_playwright.py
"""

import sys
import time
import os
import re
import win32com.client
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

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

# Directorio para datos de usuario de Playwright
PLAYWRIGHT_USER_DATA = os.path.join(BASE_DIR, "datos", "cache", "playwright_profile")
os.makedirs(PLAYWRIGHT_USER_DATA, exist_ok=True)

# Tiempos (en milisegundos)
TIEMPO_CARGA_PAGINA = 3000
TIEMPO_SCROLL = 800
TIEMPO_BUSQUEDA = 4000


def log(mensaje, nivel="INFO"):
    """Log con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    simbolo = {"INFO": " ", "OK": "+", "ERROR": "!", "WARN": "?"}
    print(f"[{timestamp}] [{simbolo.get(nivel, ' ')}] {mensaje}")


def buscar_certificacion(numero_hu):
    """Busca el archivo de certificacion para una HU"""
    for categoria in CATEGORIAS:
        ruta_cat = os.path.join(RUTA_CERTIFICACIONES, categoria)
        if os.path.exists(ruta_cat):
            archivo = f"Certificacion_QA_{numero_hu}.xlsx"
            ruta_completa = os.path.join(ruta_cat, archivo)
            if os.path.exists(ruta_completa):
                return {
                    'categoria': categoria,
                    'archivo': archivo,
                    'ruta': ruta_completa
                }
    return None


def contar_tcs_en_excel(ruta_excel):
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


def actualizar_excel(ruta_excel, cps_links, numero_hu):
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
                log(f"  CP{tc_id_str} -> Link agregado", "OK")
            else:
                no_encontrados += 1
                log(f"  CP{tc_id_str} -> No encontrado en Drive", "WARN")

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


def scroll_cargar_todo(page, total_esperado=0, max_intentos=50):
    """
    Scroll incremental para cargar todos los elementos.
    Usa el contenedor .PEfnhb con hover, click y scroll incremental.
    """
    try:
        # 1. Seleccionar el contenedor .PEfnhb
        log("Buscando contenedor .PEfnhb...")
        container = page.locator('.PEfnhb')
        container.wait_for(state='visible', timeout=10000)
        log("Contenedor encontrado", "OK")

        # 2. Forzar foco con hover y click
        log("Forzando foco con hover y click...")
        container.hover()
        container.click(force=True)
        page.wait_for_timeout(500)

        # 3. Scroll incremental
        log(f"Iniciando scroll incremental (esperados: {total_esperado} CPs)...")
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
            page.wait_for_timeout(TIEMPO_SCROLL)

            # Validar scrollTop
            scroll_top = container.evaluate("el => el.scrollTop")

            # Contar CPs cargados
            elementos = page.locator('[data-tooltip*="CP"][data-tooltip*="Carpeta"]')
            elementos_actuales = elementos.count()

            print(f"\r  Scroll {i+1}/{max_intentos}: {elementos_actuales} CPs encontrados (scrollTop: {scroll_top})", end="", flush=True)

            # Si alcanzamos el objetivo, terminar
            if total_esperado > 0 and elementos_actuales >= total_esperado:
                print()
                log(f"Objetivo alcanzado: {elementos_actuales}/{total_esperado} CPs", "OK")
                break

            # Verificar si hay cambios
            if current_height == previous_height and elementos_actuales == elementos_anteriores:
                intentos_sin_cambio += 1
                if intentos_sin_cambio >= max_sin_cambio:
                    print()
                    log(f"Scroll completado: {elementos_actuales} CPs encontrados", "OK")
                    break
            else:
                intentos_sin_cambio = 0

            previous_height = current_height
            elementos_anteriores = elementos_actuales

        # Volver arriba
        container.evaluate("el => el.scrollTop = 0")
        page.wait_for_timeout(500)

        return elementos_actuales

    except Exception as e:
        log(f"Error en scroll: {e}", "ERROR")
        return 0


def extraer_cps_de_carpeta(page, total_esperado=0):
    """Extrae todas las carpetas CP con sus links"""
    # Scroll para cargar todos los CPs
    scroll_cargar_todo(page, total_esperado=total_esperado, max_intentos=50)
    page.wait_for_timeout(1000)

    # Segundo pase para asegurar
    log("Segundo pase de scroll...")
    scroll_cargar_todo(page, total_esperado=total_esperado, max_intentos=20)
    page.wait_for_timeout(500)

    # Extraer CPs
    log("Extrayendo links de CPs...")
    cps = {}
    elementos = page.locator('[data-tooltip*="CP"][data-tooltip*="Carpeta"]')
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

    log(f"Extraidos {len(cps)} links de CPs", "OK")
    return cps


def main():
    print("=" * 60)
    print("     COMPLETAR HU - PLAYWRIGHT")
    print("=" * 60)
    print()

    # Solicitar numero de HU
    numero_hu = input("Ingresa el numero de HU: ").strip()

    if not numero_hu:
        log("Numero de HU no proporcionado", "ERROR")
        return

    # Buscar certificacion
    log(f"Buscando certificacion para HU{numero_hu}...")
    cert = buscar_certificacion(numero_hu)

    if not cert:
        log(f"No se encontro certificacion para HU{numero_hu}", "ERROR")
        return

    log(f"Certificacion encontrada: {cert['categoria']}/{cert['archivo']}", "OK")

    # Contar TCs
    total_tcs = contar_tcs_en_excel(cert['ruta'])
    log(f"Test Cases en Excel: {total_tcs}")

    print()
    respuesta = input("Continuar con el procesamiento? (s/n): ").strip().lower()
    if respuesta != 's':
        print("Cancelado por usuario")
        return

    print()

    # Iniciar Playwright
    log("Iniciando Playwright...")
    playwright = sync_playwright().start()

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=PLAYWRIGHT_USER_DATA,
        headless=False,
        viewport={'width': 1280, 'height': 900},
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
    )

    page = context.pages[0] if context.pages else context.new_page()
    log("Playwright iniciado", "OK")

    try:
        # Navegar a Drive
        log("Navegando a Google Drive...")
        page.goto(DRIVE_ROOT_URL)
        page.wait_for_timeout(TIEMPO_CARGA_PAGINA)

        # Verificar si necesita login
        if "accounts.google.com" in page.url:
            log("Necesitas iniciar sesion en Google", "WARN")
            print("\n  Por favor inicia sesion en la ventana del navegador...")
            print("  Tienes 120 segundos para hacerlo.")
            page.wait_for_timeout(120000)

        # Buscar carpeta HU
        log(f"Buscando carpeta Evidencias HU{numero_hu}...")

        search_box = page.locator('input[aria-label="Buscar en Drive"]')
        if not search_box.is_visible():
            search_box = page.locator('input[type="search"]')

        search_box.click()
        page.wait_for_timeout(300)
        search_box.fill('')
        page.wait_for_timeout(200)
        search_box.fill(numero_hu)
        page.wait_for_timeout(500)
        search_box.press('Enter')
        page.wait_for_timeout(TIEMPO_BUSQUEDA)

        # Buscar y entrar a carpeta
        carpeta_selector = f'[data-tooltip*="Evidencias HU{numero_hu}"][data-tooltip*="Carpeta"]'
        carpeta = page.locator(carpeta_selector).first

        if not carpeta.is_visible():
            log(f"No se encontro carpeta Evidencias HU{numero_hu} en Drive", "ERROR")
            return

        log("Carpeta encontrada, entrando...", "OK")
        carpeta.dblclick()
        page.wait_for_timeout(TIEMPO_CARGA_PAGINA + 2000)

        # Extraer CPs
        cps_links = extraer_cps_de_carpeta(page, total_esperado=total_tcs)

        if len(cps_links) == 0:
            log("No se encontraron carpetas CP en Drive", "ERROR")
            return

        # Actualizar Excel
        print()
        log("Actualizando Excel...")
        resultado = actualizar_excel(cert['ruta'], cps_links, numero_hu)

        print()
        print("=" * 60)
        print("                    RESUMEN")
        print("=" * 60)
        print(f"  HU: {numero_hu}")
        print(f"  Categoria: {cert['categoria']}")
        print(f"  TCs en Excel: {total_tcs}")
        print(f"  CPs en Drive: {len(cps_links)}")
        print(f"  Links agregados: {resultado['completados']}")
        print(f"  Sin match: {resultado['no_encontrados']}")
        print("=" * 60)

        if resultado['exito']:
            log("Certificacion actualizada exitosamente!", "OK")
        else:
            log(f"Error al actualizar: {resultado.get('error', 'desconocido')}", "ERROR")

    except Exception as e:
        log(f"Error: {e}", "ERROR")

    finally:
        context.close()
        playwright.stop()
        log("Playwright cerrado", "OK")


if __name__ == "__main__":
    main()
    print("\nPresiona ENTER para salir...")
    input()
