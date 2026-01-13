"""
CAPTURAR EVIDENCIA - MODO SINGLE (UN SOLO CASO DE PRUEBA)
===========================================================
Script para capturar evidencia de UN solo caso de prueba en Azure DevOps.
Útil para pruebas iniciales.

Uso: py capturar_evidencia_single.py
"""

import sys
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Importar configuración
from configuracion_evidencias import (
    AZURE_DEVOPS_BASE_URL,
    HISTORY_TAB_XPATH,
    TIEMPO_CARGA_PAGINA,
    TIEMPO_ESPERA_CLICK,
    TIEMPO_ESPERA_SCREENSHOT,
    EVIDENCIAS_BASE,
    SCREENSHOT_FORMAT,
    get_chrome_options,
    verificar_sesion_guardada
)

# ============================================
# FUNCIONES
# ============================================

def log(mensaje):
    """Imprime mensaje con formato"""
    print(f"  {mensaje}")


def capturar_evidencia_tc(driver, tc_id, carpeta_destino):
    """
    Captura evidencia de un Test Case en Azure DevOps

    Args:
        driver: WebDriver de Selenium
        tc_id: ID del Test Case
        carpeta_destino: Ruta donde guardar la captura

    Returns:
        True si se capturó correctamente, False si hubo error
    """
    print(f"\n📸 Capturando evidencia de TC {tc_id}...")

    try:
        # Construir URL del work item
        url = f"{AZURE_DEVOPS_BASE_URL}{tc_id}"
        log(f"Navegando a: {url}")

        # Navegar al work item
        driver.get(url)
        log(f"Esperando carga inicial ({TIEMPO_CARGA_PAGINA}s)...")
        time.sleep(TIEMPO_CARGA_PAGINA)

        # Crear carpeta de destino si no existe
        os.makedirs(carpeta_destino, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Buscar el tab de historial usando múltiples selectores
        log("Buscando tab de History...")
        history_tab = None

        # Lista de selectores a probar
        selectores = [
            ("xpath", HISTORY_TAB_XPATH, "XPath configurado"),
            ("xpath", "//button[contains(@aria-label, 'History')]", "Button con aria-label History"),
            ("xpath", "//div[contains(text(), 'History')]", "Div con texto History"),
            ("xpath", "//*[contains(@id, 'History')]", "Elemento con ID History"),
            ("css", "[aria-label*='History']", "CSS aria-label History"),
            ("css", "button[name='History']", "CSS button name History"),
        ]

        for tipo, selector, descripcion in selectores:
            try:
                log(f"Probando: {descripcion}...")
                wait = WebDriverWait(driver, 5)

                if tipo == "xpath":
                    elementos = driver.find_elements(By.XPATH, selector)
                else:
                    elementos = driver.find_elements(By.CSS_SELECTOR, selector)

                if elementos:
                    log(f"  ✓ Encontrados {len(elementos)} elementos con: {descripcion}")
                    history_tab = elementos[0]
                    break
                else:
                    log(f"  ✗ No encontrado con: {descripcion}")
            except Exception as e:
                log(f"  ✗ Error con {descripcion}: {str(e)[:50]}")
                continue

        if not history_tab:
            log(f"✗ No se encontró el tab de History con ningún selector")
            return False

        log("✓ Tab de History encontrado")

        # Hacer scroll al elemento para asegurarse que está visible
        log("Haciendo scroll al tab...")
        driver.execute_script("arguments[0].scrollIntoView(true);", history_tab)
        time.sleep(1)

        # Hacer click en el tab de historial
        log("Haciendo click en tab 'History'...")
        try:
            history_tab.click()
            time.sleep(TIEMPO_ESPERA_CLICK)
            log("✓ Click en History exitoso")
        except Exception as e:
            log(f"⚠️ Click directo falló, intentando con JavaScript...")
            try:
                driver.execute_script("arguments[0].click();", history_tab)
                time.sleep(TIEMPO_ESPERA_CLICK)
                log("✓ Click con JavaScript exitoso")
            except Exception as e2:
                log(f"✗ Error al hacer click: {e2}")
                return False

        # Esperar a que cargue el historial
        log(f"Esperando carga de historial ({TIEMPO_ESPERA_SCREENSHOT}s)...")
        time.sleep(TIEMPO_ESPERA_SCREENSHOT)

        # Tomar screenshot final
        nombre_archivo = f"TC{tc_id}_History_{timestamp}.{SCREENSHOT_FORMAT}"
        ruta_screenshot = os.path.join(carpeta_destino, nombre_archivo)

        log(f"Tomando screenshot final...")
        driver.save_screenshot(ruta_screenshot)

        if os.path.exists(ruta_screenshot):
            log(f"✓ Screenshot guardado: {nombre_archivo}")
            return True
        else:
            log(f"✗ Error: No se pudo guardar el screenshot")
            return False

    except Exception as e:
        log(f"✗ Error durante captura: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*80)
    print("CAPTURAR EVIDENCIA - MODO SINGLE")
    print("="*80)
    print()

    # Verificar sesión
    if not verificar_sesion_guardada():
        print("⚠️  NO SE DETECTÓ SESIÓN GUARDADA")
        print()
        print("Por favor ejecuta primero: iniciar_sesion_azure.py")
        print()
        respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
        if respuesta != 's':
            return

    # Pedir ID de Test Case
    print("="*80)
    tc_id = input("Ingresa el ID del Test Case (ej: 280070): ").strip()
    print("="*80)

    if not tc_id.isdigit():
        print("✗ ID de Test Case inválido")
        return

    # Carpeta de destino (temporal para pruebas)
    carpeta_destino = os.path.join(EVIDENCIAS_BASE, "Pruebas_Single", f"TC{tc_id}")

    print(f"\n📁 Carpeta de destino: {carpeta_destino}")

    # Configurar Chrome
    chrome_options = get_chrome_options()

    print(f"\n🌐 Iniciando Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # Capturar evidencia
        exito = capturar_evidencia_tc(driver, tc_id, carpeta_destino)

        if exito:
            print(f"\n{'='*80}")
            print(f"✅ CAPTURA COMPLETADA EXITOSAMENTE")
            print(f"{'='*80}")
            print(f"\nArchivo guardado en:")
            print(f"  {carpeta_destino}")
        else:
            print(f"\n{'='*80}")
            print(f"✗ ERROR EN LA CAPTURA")
            print(f"{'='*80}")
            print(f"\nVerifica:")
            print(f"  1. Que la sesión esté iniciada")
            print(f"  2. Que el ID del Test Case sea correcto")
            print(f"  3. Que tengas acceso al work item en Azure DevOps")

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
