"""
crear_certificacion_masivo.py
Script para crear certificaciones QA de forma masiva.
- Procesa todas las HU del CSV
- Omite las certificaciones que ya existen
- Usa win32com (Excel COM) para preservar formatos y manejar celdas combinadas
"""

import sys
import os
import csv
import re
import time
from pathlib import Path
from datetime import datetime

# Rutas base
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
FORMATO_ORIGINAL = PROJECT_ROOT / "Assets" / "Formatos" / "Formato Oficial.xlsx"
CERTIFICACIONES_ROOT = PROJECT_ROOT / "Certificaciones"
CSV_PATH = PROJECT_ROOT / "Assets" / "Base de datos" / "data.csv"


def determinar_carpeta_modulo(modulo_balu: str) -> str:
    """Determina la carpeta destino según el módulo Balu."""
    modulo_lower = modulo_balu.lower() if modulo_balu else ""

    if "recaudo" in modulo_lower or "cartera" in modulo_lower:
        return "RyC"
    elif "afiliaci" in modulo_lower or "novedades" in modulo_lower:
        return "AyN"
    else:
        return "Transversal"


APROBADOR_DEFAULT = "Victor Alejandro Moreno Gonzalez"


def extraer_nombre_aprobador(aprobador_completo: str) -> str:
    """Extrae solo el nombre del aprobador (sin correo). Si está vacío, usa el default."""
    if not aprobador_completo:
        return APROBADOR_DEFAULT
    match = re.match(r'^([^<]+)', aprobador_completo)
    if match:
        return match.group(1).strip()
    return aprobador_completo.strip()


def extraer_nombre(texto_completo: str) -> str:
    """Extrae solo el nombre (sin correo) de un texto como 'Nombre <correo>'."""
    if not texto_completo:
        return ""
    match = re.match(r'^([^<]+)', texto_completo)
    if match:
        return match.group(1).strip()
    return texto_completo.strip()


def leer_todas_las_hu() -> list:
    """
    Lee todas las HU y sus Test Cases desde el CSV.
    Los Test Cases se asignan por posición: pertenecen a la HU que les precede
    en el CSV hasta que aparezca la siguiente HU.
    """
    hu_list = []
    current_hu = None

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            work_item_type = row.get('Work Item Type', '')
            row_id = row.get('ID', '')

            if work_item_type == 'User Story':
                # Guardar la HU anterior si existe
                if current_hu is not None:
                    hu_list.append(current_hu)

                # Iniciar nueva HU
                current_hu = {
                    'id': row_id,
                    'title': row.get('Title', ''),
                    'iteration_path': row.get('Iteration Path', ''),
                    'modulo_balu': row.get('Modulo Balu', ''),
                    'aprobador_qa': row.get('Aprobador QA', ''),
                    'tester': row.get('Tester', ''),
                    'test_cases': []
                }

            elif work_item_type == 'Test Case' and current_hu is not None:
                # Agregar TC a la HU actual (por posición en el CSV)
                current_hu['test_cases'].append({
                    'id': row_id,
                    'title': row.get('Title', '')
                })

    # Agregar la última HU
    if current_hu is not None:
        hu_list.append(current_hu)

    return hu_list


def obtener_testers_unicos(hu_list: list) -> list:
    """Obtiene la lista de testers únicos de las HU."""
    testers = set()
    for hu in hu_list:
        tester = extraer_nombre(hu.get('tester', ''))
        if tester:
            testers.add(tester)
    return sorted(list(testers))


def mostrar_menu_testers(testers: list) -> list:
    """Muestra el menú de selección de testers y retorna los seleccionados."""
    print("\n  Testers disponibles:")
    print("  " + "-" * 50)
    print("  [0] TODOS los testers")
    for idx, tester in enumerate(testers, 1):
        print(f"  [{idx}] {tester}")
    print("  " + "-" * 50)

    while True:
        seleccion = input("\n  Ingrese los números separados por coma (ej: 1,3,5) o 0 para todos: ").strip()

        if seleccion == '0':
            return testers  # Retorna todos

        try:
            indices = [int(x.strip()) for x in seleccion.split(',')]
            seleccionados = []
            for idx in indices:
                if 1 <= idx <= len(testers):
                    seleccionados.append(testers[idx - 1])
                else:
                    print(f"  ERROR: Índice {idx} fuera de rango")
                    continue

            if seleccionados:
                return seleccionados
            else:
                print("  ERROR: No se seleccionó ningún tester válido")
        except ValueError:
            print("  ERROR: Ingrese solo números separados por coma")


def crear_certificacion_completa(excel, origen: Path, destino: Path, hu_data: dict) -> bool:
    """
    Crea una certificación completa en una sola operación:
    - Abre el formato original
    - Llena todos los datos
    - Guarda como nuevo archivo

    Esto es más eficiente que copiar y luego abrir de nuevo.
    """
    # Si el archivo destino existe, eliminarlo primero (evita conflictos con OneDrive)
    if destino.exists():
        try:
            destino.unlink()
            time.sleep(0.3)  # Pausa para que OneDrive procese la eliminación
        except Exception as e:
            print(f"      ADVERTENCIA: No se pudo eliminar existente: {e}")

    try:
        # Abrir formato original
        wb = excel.Workbooks.Open(str(origen))
        ws = wb.ActiveSheet

        # F13: Aprobador QA
        nombre_aprobador = extraer_nombre_aprobador(hu_data.get('aprobador_qa', ''))
        ws.Range("F13").Value = nombre_aprobador

        # H12: HU + Iteration Path
        hu_texto = f"HU{hu_data['id']} - {hu_data.get('iteration_path', '')}"
        ws.Range("H12").Value = hu_texto

        # H13: Módulo Balu
        modulo = hu_data.get('modulo_balu', '')
        ws.Range("H13").Value = modulo

        # Test Cases desde fila 21
        test_cases = hu_data.get('test_cases', [])
        num_tc = len(test_cases)

        if num_tc > 1:
            # Duplicar la fila 21 para cada TC adicional
            for i in range(num_tc - 1):
                ws.Rows(21).Copy()
                ws.Rows(22 + i).Insert(Shift=-4121)

        # Llenar los datos en cada fila
        for i, tc in enumerate(test_cases):
            fila = 21 + i
            ws.Range(f"C{fila}").Value = tc['id']
            ws.Range(f"D{fila}").Value = tc['title']

        # Guardar como nuevo archivo (en lugar de copiar primero)
        wb.SaveAs(str(destino))
        wb.Close(SaveChanges=False)
        return True

    except Exception as e:
        print(f"      ERROR: {e}")
        try:
            wb.Close(SaveChanges=False)
        except:
            pass
        return False


def main():
    print("\n" + "=" * 70)
    print("       CREACIÓN MASIVA DE CERTIFICACIONES QA")
    print("=" * 70 + "\n")

    # Verificar archivos
    print("[1/5] Verificando archivos necesarios...")

    if not FORMATO_ORIGINAL.exists():
        print(f"  ERROR: No se encuentra el formato en: {FORMATO_ORIGINAL}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    print(f"  [OK] Formato oficial encontrado")

    if not CSV_PATH.exists():
        print(f"  ERROR: No se encuentra el CSV en: {CSV_PATH}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    print(f"  [OK] CSV de datos encontrado")

    # Leer todas las HU
    print("\n[2/5] Leyendo datos del CSV...")
    todas_las_hu = leer_todas_las_hu()
    print(f"  Total de HU encontradas: {len(todas_las_hu)}")

    # Selección de testers
    print("\n[3/5] Selección de Testers...")
    testers_disponibles = obtener_testers_unicos(todas_las_hu)

    if not testers_disponibles:
        print("  ADVERTENCIA: No se encontraron testers en las HU")
        testers_seleccionados = []
    else:
        print(f"  Se encontraron {len(testers_disponibles)} testers")
        testers_seleccionados = mostrar_menu_testers(testers_disponibles)
        print(f"\n  Testers seleccionados: {len(testers_seleccionados)}")
        for t in testers_seleccionados:
            print(f"    - {t}")

    # Filtrar HU por testers seleccionados
    if testers_seleccionados:
        hu_filtradas = [
            hu for hu in todas_las_hu
            if extraer_nombre(hu.get('tester', '')) in testers_seleccionados
        ]
    else:
        hu_filtradas = todas_las_hu

    print(f"\n  HU después del filtro por tester: {len(hu_filtradas)}")

    # Filtrar HU sin Test Cases
    print("\n[4/6] Filtrando HU sin Test Cases...")
    hu_con_tc = [hu for hu in hu_filtradas if len(hu.get('test_cases', [])) > 0]
    hu_sin_tc = [hu for hu in hu_filtradas if len(hu.get('test_cases', [])) == 0]

    print(f"  HU con Test Cases: {len(hu_con_tc)}")
    print(f"  HU sin Test Cases (se omitirán): {len(hu_sin_tc)}")

    if hu_sin_tc:
        print("  HUs omitidas por falta de TCs:")
        for hu in hu_sin_tc[:10]:
            print(f"    - HU{hu['id']}: {hu['title'][:45]}...")
        if len(hu_sin_tc) > 10:
            print(f"    ... y {len(hu_sin_tc) - 10} más")

    # Filtrar HU que ya tienen certificación
    print("\n[5/6] Verificando certificaciones existentes...")
    hu_a_procesar = []
    hu_omitidas = []

    for hu in hu_con_tc:
        carpeta = determinar_carpeta_modulo(hu['modulo_balu'])
        archivo = CERTIFICACIONES_ROOT / carpeta / f"Certificacion_QA_{hu['id']}.xlsx"

        if archivo.exists():
            hu_omitidas.append(hu)
        else:
            hu_a_procesar.append(hu)

    print(f"  Certificaciones existentes (se omitirán): {len(hu_omitidas)}")
    print(f"  Certificaciones a crear: {len(hu_a_procesar)}")

    if not hu_a_procesar:
        print("\n  No hay certificaciones nuevas para crear.")
        input("\nPresione Enter para salir...")
        sys.exit(0)

    # Confirmar ejecución
    print(f"\n  Se crearán {len(hu_a_procesar)} certificaciones nuevas.")
    confirmar = input("  ¿Desea continuar? (S/N): ").strip().upper()
    if confirmar != 'S':
        print("  Operación cancelada.")
        input("\nPresione Enter para salir...")
        sys.exit(0)

    # Procesar certificaciones
    print("\n[6/6] Creando certificaciones...")
    print("-" * 70)

    import win32com.client
    import pythoncom

    pythoncom.CoInitialize()
    excel = None

    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        creadas = 0
        errores = 0
        inicio = time.time()

        for idx, hu in enumerate(hu_a_procesar, 1):
            hu_id = hu['id']
            carpeta = determinar_carpeta_modulo(hu['modulo_balu'])
            destino_dir = CERTIFICACIONES_ROOT / carpeta
            destino_dir.mkdir(parents=True, exist_ok=True)
            archivo_destino = destino_dir / f"Certificacion_QA_{hu_id}.xlsx"

            print(f"\n  [{idx}/{len(hu_a_procesar)}] HU{hu_id} -> {carpeta}/")
            print(f"      TCs: {len(hu['test_cases'])} | {hu['title'][:45]}...")

            # Crear certificación en una sola operación (optimizado)
            if crear_certificacion_completa(excel, FORMATO_ORIGINAL, archivo_destino, hu):
                print("      [OK] Creada")
                creadas += 1
            else:
                errores += 1

        tiempo_total = time.time() - inicio

    finally:
        if excel:
            excel.Quit()
        pythoncom.CoUninitialize()

    # Resumen final
    print("\n" + "=" * 70)
    print("                      RESUMEN DE EJECUCIÓN")
    print("=" * 70)
    print(f"\n  Certificaciones creadas:    {creadas}")
    print(f"  Omitidas (ya existían):     {len(hu_omitidas)}")
    print(f"  Omitidas (sin Test Cases):  {len(hu_sin_tc)}")
    print(f"  Errores:                    {errores}")
    print(f"  Tiempo total:               {tiempo_total:.1f} segundos")
    print(f"\n  Ubicación: {CERTIFICACIONES_ROOT}")

    input("\nPresione Enter para salir...")


if __name__ == "__main__":
    main()
