"""
CAPTURAR EVIDENCIA - MODO HU COMPLETA
======================================
Script para capturar evidencias de TODOS los Test Cases de una HU.

Uso: py capturar_evidencia_hu.py
"""

import sys
import time
import os
import csv
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

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

# Obtener la raíz del proyecto AutCert (4 niveles arriba: scripts -> Evidencias_Azure -> Modulos -> AutCert)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import CSV_PATH_STR

CSV_PATH = CSV_PATH_STR

def log(mensaje):
    print(f"  {mensaje}")

def obtener_tcs_de_hu(numero_hu):
    """Obtiene todos los Test Cases de una HU desde el CSV"""
    print(f"\n📋 Buscando Test Cases de HU{numero_hu} en CSV...")

    if not os.path.exists(CSV_PATH):
        log(f"✗ No se encontró el CSV: {CSV_PATH}")
        return []

    tcs = []
    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            capturando = False

            for row in reader:
                work_type = row.get('Work Item Type', '')

                # Si encontramos la HU buscada, empezar a capturar TCs
                if work_type == 'User Story' and row['ID'] == numero_hu:
                    capturando = True
                    continue

                # Si encontramos otra User Story, dejar de capturar
                if work_type == 'User Story' and capturando:
                    break

                # Capturar Test Cases mientras estamos en la HU correcta
                if capturando and work_type == 'Test Case':
                    tcs.append(row['ID'])

        log(f"✓ Encontrados {len(tcs)} Test Cases")
        return tcs
    except Exception as e:
        log(f"✗ Error al leer CSV: {e}")
        return []

def capturar_evidencia_tc(driver, tc_id, carpeta_destino):
    """Captura evidencia de un Test Case"""
    print(f"\n📸 TC {tc_id}...")

    try:
        url = f"{AZURE_DEVOPS_BASE_URL}{tc_id}"
        driver.get(url)

        # Esperar a que la página cargue COMPLETAMENTE
        time.sleep(TIEMPO_CARGA_PAGINA)

        # Esperar explícitamente a que document.readyState sea complete
        for _ in range(20):
            estado = driver.execute_script("return document.readyState")
            if estado == "complete":
                break
            time.sleep(0.5)

        # Espera adicional para render de tabs
        time.sleep(2)

        os.makedirs(carpeta_destino, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Buscar tab History con querySelector (más confiable)
        history_tab = driver.execute_script(
            'return document.querySelector("#__bolt-tab-Agile-Test-Case-System_History > span > span > span")'
        )

        if not history_tab:
            log(f"✗ No se encontró tab de History")
            return False

        # Click en History
        driver.execute_script("arguments[0].scrollIntoView(true);", history_tab)
        time.sleep(0.5)

        try:
            history_tab.click()
        except:
            driver.execute_script("arguments[0].click();", history_tab)

        # CRÍTICO: Esperar a que termine la navegación del click
        # Azure cambia la URL o el contenido al hacer click en History
        time.sleep(2)  # Espera inicial

        # Esperar hasta que el navegador termine de procesar
        for _ in range(10):
            try:
                # Verificar si hay algún elemento de carga activo
                estado = driver.execute_script("return document.readyState")
                if estado == "complete":
                    break
            except:
                pass
            time.sleep(0.3)

        # Espera adicional para render completo
        time.sleep(TIEMPO_ESPERA_SCREENSHOT)

        # Screenshot
        nombre_archivo = f"TC{tc_id}_History_{timestamp}.{SCREENSHOT_FORMAT}"
        ruta_screenshot = os.path.join(carpeta_destino, nombre_archivo)
        driver.save_screenshot(ruta_screenshot)
        log(f"✓ Guardado")
        return True

    except Exception as e:
        log(f"✗ Error: {e}")
        return False

def main():
    print("="*80)
    print("CAPTURAR EVIDENCIA - MODO HU COMPLETA")
    print("="*80)
    print()

    if not verificar_sesion_guardada():
        print("⚠️  NO SE DETECTÓ SESIÓN GUARDADA")
        print("Por favor ejecuta primero: iniciar_sesion_azure.py")
        print()
        respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
        if respuesta != 's':
            return

    print("="*80)
    numero_hu = input("Ingresa el número de HU (ej: 273920): ").strip()
    print("="*80)

    if not numero_hu.isdigit():
        print("✗ Número de HU inválido")
        return

    tcs = obtener_tcs_de_hu(numero_hu)

    if not tcs:
        print(f"✗ No se encontraron Test Cases para HU{numero_hu}")
        return

    print(f"\n📁 Se capturarán evidencias de {len(tcs)} Test Cases")
    print(f"   Carpeta base: {EVIDENCIAS_BASE}")
    print()
    input("Presiona ENTER para comenzar...")

    chrome_options = get_chrome_options()
    print(f"\n🌐 Iniciando Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        exitosos = 0
        fallidos = 0

        for i, tc_id in enumerate(tcs, 1):
            print(f"\n[{i}/{len(tcs)}] Procesando TC {tc_id}...")
            carpeta_tc = os.path.join(EVIDENCIAS_BASE, f"HU{numero_hu}", f"CP{tc_id}")

            if capturar_evidencia_tc(driver, tc_id, carpeta_tc):
                exitosos += 1
            else:
                fallidos += 1

        print(f"\n{'='*80}")
        print(f"✅ PROCESO COMPLETADO")
        print(f"{'='*80}")
        print(f"\nResultados:")
        print(f"  ✓ Exitosos: {exitosos}")
        print(f"  ✗ Fallidos: {fallidos}")
        print(f"  Total: {len(tcs)}")

    except Exception as e:
        print(f"\n✗ Error durante el proceso: {e}")

    finally:
        driver.quit()
        print("\n✓ Navegador cerrado")
        print("\nPresiona ENTER para salir...")
        input()

if __name__ == "__main__":
    main()
