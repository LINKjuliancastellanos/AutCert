"""
COMPLETAR CERTIFICACIÓN - MODO INTERACTIVO
===========================================
Script interactivo que:
1. Te pide el número de HU
2. Busca la carpeta en Drive (como test_busqueda)
3. Entra y extrae los links de todas las CPs
4. Actualiza el Excel de esa HU con los links

Uso: py completar_certificacion_interactivo.py
"""

import sys
import time
import os
import re
import win32com.client
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Importar configuración
from configuracion_drive import (
    DRIVE_ROOT_URL,
    TIEMPO_CARGA_PAGINA,
    TIEMPO_SCROLL,
    TIEMPO_BUSQUEDA,
    MAX_INTENTOS_SCROLL,
    INTENTOS_SIN_CAMBIO,
    get_chrome_options,
    verificar_sesion_guardada
)

# Obtener la raíz del proyecto AutCert (3 niveles arriba: scripts -> Links_Drive -> Modulos -> AutCert)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import CERTIFICACIONES_ROOT_STR

# ============================================
# CONFIGURACIÓN
# ============================================

RUTA_CERTIFICACIONES = CERTIFICACIONES_ROOT_STR

# ============================================
# FUNCIONES
# ============================================

def log(mensaje):
    """Imprime mensaje con formato"""
    print(f"  {mensaje}")


def scroll_cargar_todo(driver, max_intentos=20):
    """Scroll para cargar todos los elementos"""
    print("  📜 Cargando todos los elementos...")

    elementos_anteriores = 0
    intentos_sin_cambio = 0

    for i in range(max_intentos):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.PAGE_DOWN)
            body.send_keys(Keys.PAGE_DOWN)
        except:
            pass

        time.sleep(TIEMPO_SCROLL)

        elementos_actuales = len(driver.find_elements(By.CSS_SELECTOR, "[data-tooltip]"))

        if elementos_actuales == elementos_anteriores:
            intentos_sin_cambio += 1
            if intentos_sin_cambio >= INTENTOS_SIN_CAMBIO:
                break
        else:
            intentos_sin_cambio = 0

        elementos_anteriores = elementos_actuales

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    print(f"  ✓ {elementos_actuales} elementos cargados")
    return elementos_actuales


def buscar_carpeta_hu_en_drive(driver, numero_hu):
    """Busca la carpeta de evidencias de una HU usando la búsqueda de Drive"""
    print(f"\n🔍 Buscando carpeta de HU{numero_hu} en Drive...")

    try:
        # Buscar la caja de búsqueda
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
                    search_box = driver.find_element(By.XPATH, selector)
                else:
                    search_box = driver.find_element(By.CSS_SELECTOR, selector)
                log("✓ Caja de búsqueda encontrada")
                break
            except:
                continue

        if not search_box:
            log("✗ No se encontró la caja de búsqueda")
            return None

        # Buscar por el número de HU
        search_box.click()
        time.sleep(0.5)
        search_box.clear()
        search_box.send_keys(numero_hu)
        time.sleep(1)
        search_box.send_keys(Keys.RETURN)

        log("⏳ Esperando resultados de búsqueda...")
        time.sleep(TIEMPO_BUSQUEDA)

        # Buscar carpeta que contenga "Evidencias HU{numero}"
        elementos = driver.find_elements(By.CSS_SELECTOR, "[data-tooltip]")

        for elem in elementos:
            try:
                tooltip = elem.get_attribute('data-tooltip')
                if tooltip and f"Evidencias HU{numero_hu}" in tooltip and "Carpeta" in tooltip:
                    log(f"✓ Carpeta encontrada: {tooltip}")

                    # Obtener data-id inmediatamente
                    data_id = elem.get_attribute("data-id")

                    if data_id:
                        url = f"https://drive.google.com/drive/folders/{data_id}"
                        log(f"✓ URL obtenida")
                        return url
                    else:
                        log("⚠️ No se pudo obtener data-id")
            except:
                continue

        log(f"✗ No se encontró carpeta 'Evidencias HU{numero_hu}'")
        return None

    except Exception as e:
        log(f"✗ Error en búsqueda: {e}")
        return None


def extraer_cps_de_carpeta(driver):
    """Extrae todas las carpetas CP con sus links de la carpeta actual"""
    print(f"\n📂 Extrayendo carpetas CP...")

    # Scroll para cargar todas las CPs
    scroll_cargar_todo(driver, max_intentos=15)

    # Buscar todas las carpetas
    elementos = driver.find_elements(By.CSS_SELECTOR, "[data-tooltip]")

    cps = {}  # {numero_cp: link}

    for elem in elementos:
        try:
            tooltip = elem.get_attribute('data-tooltip')

            # Verificar si es una carpeta CP
            if tooltip and 'CP' in tooltip and 'Carpeta' in tooltip:
                # Extraer número de CP
                match = re.search(r'CP\s*(\d+)', tooltip, re.IGNORECASE)
                if match:
                    numero_cp = match.group(1)

                    # Obtener link inmediatamente
                    data_id = elem.get_attribute("data-id")
                    if data_id:
                        link = f"https://drive.google.com/drive/folders/{data_id}"
                        cps[numero_cp] = link
                        log(f"✓ CP{numero_cp}: Link obtenido")
        except:
            continue

    print(f"\n✅ {len(cps)} carpetas CP encontradas con links")
    return cps


def buscar_excel_certificacion(numero_hu):
    """Busca el Excel de certificación de una HU"""
    categorias = ['AyN', 'RyC', 'Transversal']

    for cat in categorias:
        ruta = os.path.join(RUTA_CERTIFICACIONES, cat, f"Certificación_QA_HU{numero_hu}.xlsx")
        if os.path.exists(ruta):
            return ruta

    return None


def actualizar_excel_con_links(ruta_excel, cps_links, numero_hu):
    """Actualiza el Excel con los links de las CPs"""
    print(f"\n📝 Actualizando Excel: {os.path.basename(ruta_excel)}")

    try:
        # Abrir Excel
        excel = win32com.client.Dispatch("Excel.Application")
        excel.DisplayAlerts = False
        workbook = excel.Workbooks.Open(ruta_excel)
        worksheet = workbook.Worksheets(1)

        completados = 0
        no_encontrados = 0

        # Procesar desde fila 21
        fila = 21
        while True:
            # Leer ID de Test Case (columna C)
            tc_id = worksheet.Cells(fila, 3).Value

            if tc_id is None:
                break

            # Convertir a string, manejando números decimales de Excel
            tc_id_str = str(tc_id).strip()

            # Si es número decimal (ej: 280070.0), convertir a int
            try:
                if '.' in tc_id_str and tc_id_str.replace('.', '').isdigit():
                    tc_id_str = str(int(float(tc_id_str)))
            except:
                pass

            # Si es texto largo (conclusión), terminar
            if len(tc_id_str) > 10 or "CONCLUSIÓN" in tc_id_str.upper():
                break

            # Buscar link en el diccionario de CPs
            if tc_id_str in cps_links:
                link = cps_links[tc_id_str]
                worksheet.Cells(fila, 6).Value = link
                completados += 1
                log(f"Fila {fila}: TC {tc_id_str} → Link agregado ✓")
            else:
                no_encontrados += 1
                log(f"Fila {fila}: TC {tc_id_str} → No encontrado en Drive ⚠️")

            fila += 1

        # Guardar cambios
        workbook.Save()
        workbook.Close(False)
        excel.Quit()

        print(f"\n✅ Excel actualizado:")
        print(f"   {completados} links agregados")
        print(f"   {no_encontrados} CPs no encontradas en Drive")

        return True

    except Exception as e:
        print(f"\n✗ Error al actualizar Excel: {e}")
        try:
            workbook.Close(False)
            excel.Quit()
        except:
            pass
        return False


def main():
    print("="*80)
    print("COMPLETAR CERTIFICACIÓN - MODO INTERACTIVO")
    print("="*80)
    print()

    # Verificar sesión
    if not verificar_sesion_guardada():
        print("⚠️  NO SE DETECTÓ SESIÓN GUARDADA")
        print()
        print("Por favor ejecuta primero: Iniciar_Sesion.bat")
        print()
        respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
        if respuesta != 's':
            return

    # Pedir número de HU
    print("="*80)
    numero_hu = input("Ingresa el número de HU (ej: 273920): ").strip()
    print("="*80)

    if not numero_hu.isdigit():
        print("✗ Número de HU inválido")
        return

    # Buscar Excel
    print(f"\n📁 Buscando certificación para HU{numero_hu}...")
    ruta_excel = buscar_excel_certificacion(numero_hu)

    if not ruta_excel:
        print(f"✗ No se encontró certificación para HU{numero_hu}")
        print(f"   Buscado en: {RUTA_CERTIFICACIONES}")
        return

    print(f"✓ Excel encontrado: {os.path.basename(ruta_excel)}")

    # Configurar Chrome
    chrome_options = get_chrome_options()

    print(f"\n🌐 Iniciando Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # Navegar a Drive
        print(f"\n📂 Navegando a Google Drive...")
        driver.get(DRIVE_ROOT_URL)
        time.sleep(TIEMPO_CARGA_PAGINA)

        # Buscar carpeta de HU
        url_hu = buscar_carpeta_hu_en_drive(driver, numero_hu)

        if not url_hu:
            print(f"\n✗ No se pudo encontrar la carpeta de HU{numero_hu} en Drive")
            print(f"   Verifica que existe 'Evidencias HU{numero_hu}' en Drive")
            return

        # Navegar a la carpeta de HU
        print(f"\n🚀 Navegando a carpeta de HU{numero_hu}...")
        driver.get(url_hu)
        time.sleep(TIEMPO_CARGA_PAGINA)

        # Extraer CPs
        cps_links = extraer_cps_de_carpeta(driver)

        if len(cps_links) == 0:
            print(f"\n⚠️  No se encontraron carpetas CP en la HU{numero_hu}")
            respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
            if respuesta != 's':
                return

        # Actualizar Excel
        actualizar_excel_con_links(ruta_excel, cps_links, numero_hu)

        print(f"\n{'='*80}")
        print(f"✅ PROCESO COMPLETADO")
        print(f"{'='*80}")

    except Exception as e:
        print(f"\n✗ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        print("\n✓ Navegador cerrado")
        print("\nPresiona ENTER para salir...")
        input()


if __name__ == "__main__":
    main()
