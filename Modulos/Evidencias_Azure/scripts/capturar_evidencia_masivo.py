"""
CAPTURAR EVIDENCIA - MODO MASIVO
==================================
Script para capturar evidencias de TODAS las HUs asignadas al usuario.

Uso: py capturar_evidencia_masivo.py
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
from webdriver_manager.chrome import ChromeDriverManager

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from configuracion_evidencias import (
    AZURE_DEVOPS_BASE_URL,
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
from config_paths import CSV_PATH_STR, EVIDENCIAS_ROOT_STR

CSV_PATH = CSV_PATH_STR
EVIDENCIAS_ROOT = EVIDENCIAS_ROOT_STR

def log(mensaje):
    print(f"  {mensaje}")

def obtener_testers(datos_cache):
    """Obtiene lista única de testers desde cache"""
    return sorted(list(datos_cache['testers']))

def obtener_hus_por_tester(tester_nombre, datos_cache):
    """Obtiene HUs asignadas a un tester específico desde cache"""
    print(f"\n📋 Buscando HUs asignadas a {tester_nombre}...")

    hus = []
    for hu_id, hu_data in datos_cache['hus'].items():
        if tester_nombre in hu_data['tester']:
            hus.append({
                'id': hu_id,
                'modulo': hu_data['modulo']
            })

    log(f"✓ Encontradas {len(hus)} HUs asignadas")
    return hus

def cargar_datos_csv_completos():
    """Carga y cachea todos los datos del CSV una sola vez"""
    datos = {'hus': {}, 'testers': set()}

    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            hu_actual = None

            for row in reader:
                work_type = row.get('Work Item Type', '')
                tester = row.get('Tester', '').strip()

                if work_type == 'User Story':
                    hu_id = row['ID']
                    hu_actual = hu_id
                    datos['hus'][hu_id] = {
                        'tester': tester,
                        'modulo': row.get('Modulo Balu', ''),
                        'tcs': []
                    }
                    if tester and '<' in tester:
                        datos['testers'].add(tester)

                elif work_type == 'Test Case' and hu_actual and hu_actual in datos['hus']:
                    datos['hus'][hu_actual]['tcs'].append(row['ID'])

        return datos
    except:
        return {'hus': {}, 'testers': set()}

def obtener_tcs_de_hu(numero_hu, datos_cache):
    """Obtiene todos los Test Cases de una HU desde cache"""
    return datos_cache['hus'].get(numero_hu, {}).get('tcs', [])

def capturar_evidencia_tc(driver, tc_id, carpeta_destino, timestamp):
    """Captura evidencia de un Test Case - ULTRA OPTIMIZADO"""
    try:
        url = f"{AZURE_DEVOPS_BASE_URL}{tc_id}"
        driver.get(url)

        # Espera inicial reducida
        time.sleep(1.5)

        # Esperar document ready optimizado (máx 3 seg)
        for _ in range(6):
            estado = driver.execute_script("return document.readyState")
            if estado == "complete":
                break
            time.sleep(0.5)

        # Espera mínima para render tabs
        time.sleep(0.5)

        # Buscar y hacer click directo con JS
        history_tab = driver.execute_script(
            'return document.querySelector("#__bolt-tab-Agile-Test-Case-System_History > span > span > span")'
        )

        if not history_tab:
            return False

        # Click directo con JS
        driver.execute_script("arguments[0].click();", history_tab)

        # Espera reducida después del click
        time.sleep(2)

        # Screenshot inmediato
        nombre_archivo = f"TC{tc_id}_History_{timestamp}.{SCREENSHOT_FORMAT}"
        ruta_screenshot = os.path.join(carpeta_destino, nombre_archivo)
        driver.save_screenshot(ruta_screenshot)
        return True

    except:
        return False

def obtener_carpeta_modulo(modulo):
    """Mapea módulo a carpeta de evidencias"""
    if "Afiliaciones y Novedades" in modulo or "Afiliación y Novedades" in modulo:
        return "AyN"
    elif "Recaudo y Cartera" in modulo:
        return "RyC"
    elif "Transversal" in modulo:
        return "Transversal"
    else:
        return "Otros"

def main():
    print("="*80)
    print("CAPTURAR EVIDENCIA - MODO MASIVO")
    print("="*80)
    print()

    if not verificar_sesion_guardada():
        print("⚠️  NO SE DETECTÓ SESIÓN GUARDADA")
        print("Por favor ejecuta primero: iniciar_sesion_azure.py")
        print()
        respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
        if respuesta != 's':
            return

    # Cargar CSV completo UNA SOLA VEZ
    print("\n📋 Cargando datos del CSV...")
    datos_cache = cargar_datos_csv_completos()

    if not datos_cache['testers']:
        print("✗ No se encontraron testers en el CSV")
        return

    # Seleccionar tester
    testers = obtener_testers(datos_cache)

    print(f"\n{'='*80}")
    print("TESTERS DISPONIBLES:")
    print(f"{'='*80}")
    for i, tester in enumerate(testers, 1):
        print(f"  {i}. {tester}")

    print(f"\n{'='*80}")
    seleccion = input("Selecciona el número del tester: ").strip()

    try:
        idx = int(seleccion) - 1
        if idx < 0 or idx >= len(testers):
            print("✗ Selección inválida")
            return
        tester_seleccionado = testers[idx]
    except:
        print("✗ Entrada inválida")
        return

    # Obtener HUs del tester
    hus = obtener_hus_por_tester(tester_seleccionado, datos_cache)

    if not hus:
        print(f"✗ No se encontraron HUs para {tester_seleccionado}")
        return

    # Organizar por módulo y contar TCs
    total_tcs = 0
    hu_data = {}
    modulos_resumen = {}
    todas_carpetas = set()

    for hu in hus:
        hu_id = hu['id']
        modulo = hu['modulo']
        carpeta_modulo = obtener_carpeta_modulo(modulo)

        tcs = obtener_tcs_de_hu(hu_id, datos_cache)
        hu_data[hu_id] = {
            'tcs': tcs,
            'modulo': modulo,
            'carpeta': carpeta_modulo
        }

        total_tcs += len(tcs)

        if carpeta_modulo not in modulos_resumen:
            modulos_resumen[carpeta_modulo] = {'hus': 0, 'tcs': 0}
        modulos_resumen[carpeta_modulo]['hus'] += 1
        modulos_resumen[carpeta_modulo]['tcs'] += len(tcs)

        # Recolectar todas las carpetas a crear
        for tc_id in tcs:
            carpeta_tc = os.path.join(EVIDENCIAS_ROOT, carpeta_modulo, f"HU{hu_id}", f"CP{tc_id}")
            todas_carpetas.add(carpeta_tc)

    print(f"\n{'='*80}")
    print(f"📊 RESUMEN PARA: {tester_seleccionado}")
    print(f"{'='*80}")
    print(f"  Total HUs: {len(hus)}")
    print(f"  Total Test Cases: {total_tcs}")
    print()
    print("Por módulo:")
    for carpeta, datos in modulos_resumen.items():
        print(f"  {carpeta}: {datos['hus']} HUs, {datos['tcs']} TCs")
    print()
    print(f"Carpeta base: {EVIDENCIAS_ROOT}")

    print(f"\n{'='*80}")
    respuesta = input("¿Iniciar captura masiva? (s/n): ").strip().lower()
    if respuesta != 's':
        print("Cancelado.")
        return

    # Crear TODAS las carpetas de destino antes de iniciar
    print(f"\n📁 Creando estructura de carpetas ({len(todas_carpetas)} carpetas)...")
    for carpeta in todas_carpetas:
        os.makedirs(carpeta, exist_ok=True)
    log("✓ Carpetas creadas")

    # Generar timestamp único para toda la ejecución
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    chrome_options = get_chrome_options()
    print(f"\n🌐 Iniciando Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        total_exitosos = 0
        total_fallidos = 0
        tc_procesados = 0

        for i_hu, (hu_id, datos) in enumerate(hu_data.items(), 1):
            tcs = datos['tcs']
            carpeta_modulo = datos['carpeta']

            print(f"\n{'='*80}")
            print(f"[HU {i_hu}/{len(hus)}] HU{hu_id} - {carpeta_modulo} ({len(tcs)} TCs)")
            print(f"{'='*80}")

            for i_tc, tc_id in enumerate(tcs, 1):
                tc_procesados += 1
                print(f"[{tc_procesados}/{total_tcs}] TC {tc_id}...", end=" ")

                # Estructura: Evidencias/{Categoria}/{HU_ID}/CP{TC_ID}/
                carpeta_tc = os.path.join(EVIDENCIAS_ROOT, carpeta_modulo, f"HU{hu_id}", f"CP{tc_id}")

                if capturar_evidencia_tc(driver, tc_id, carpeta_tc, timestamp):
                    print("✓")
                    total_exitosos += 1
                else:
                    print("✗")
                    total_fallidos += 1

        print(f"\n{'='*80}")
        print(f"✅ PROCESO MASIVO COMPLETADO")
        print(f"{'='*80}")
        print(f"\nResultados Globales:")
        print(f"  Tester: {tester_seleccionado}")
        print(f"  HUs procesadas: {len(hus)}")
        print(f"  ✓ Exitosos: {total_exitosos}")
        print(f"  ✗ Fallidos: {total_fallidos}")
        print(f"  Total: {total_tcs}")
        print(f"\n  Carpeta: {EVIDENCIAS_ROOT}")

    except Exception as e:
        print(f"\n✗ Error durante el proceso: {e}")

    finally:
        driver.quit()
        print("\n✓ Navegador cerrado")
        print("\nPresiona ENTER para salir...")
        input()

if __name__ == "__main__":
    main()
