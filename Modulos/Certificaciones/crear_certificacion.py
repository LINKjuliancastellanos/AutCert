"""
crear_certificacion.py
Script unificado para crear certificaciones QA.
- Usa win32com (Excel COM) para copiar el formato (preserva 100% formatos, imágenes, estilos)
- Usa openpyxl para llenar los datos
"""

import sys
import os
import csv
import re
from pathlib import Path

# Obtener la raíz del proyecto AutCert (2 niveles arriba: Certificaciones -> Modulos -> AutCert)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import CERTIFICACIONES_ROOT, CSV_PATH

# Formato original (dentro del proyecto)
FORMATO_ORIGINAL = PROJECT_ROOT / "Assets" / "Formatos" / "Formato Oficial.xlsx"


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


def leer_datos_hu(hu_id: str) -> dict:
    """
    Lee los datos de una HU desde el CSV.
    Los Test Cases se asignan por posición: pertenecen a la HU que les precede
    en el CSV hasta que aparezca la siguiente HU.
    """
    hu_data = None
    test_cases = []
    encontrada = False

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            work_item_type = row.get('Work Item Type', '')
            row_id = row.get('ID', '')

            if work_item_type == 'User Story':
                if encontrada:
                    # Ya encontramos la HU y ahora hay otra, terminamos
                    break
                if row_id == hu_id:
                    encontrada = True
                    hu_data = {
                        'id': row_id,
                        'title': row.get('Title', ''),
                        'iteration_path': row.get('Iteration Path', ''),
                        'modulo_balu': row.get('Modulo Balu', ''),
                        'aprobador_qa': row.get('Aprobador QA', ''),
                    }

            elif work_item_type == 'Test Case' and encontrada:
                # Test Case pertenece a la HU actual (por posición)
                test_cases.append({
                    'id': row_id,
                    'title': row.get('Title', '')
                })

    if hu_data:
        hu_data['test_cases'] = test_cases
    return hu_data


def copiar_con_excel_com(origen: Path, destino: Path) -> bool:
    """
    Copia un archivo Excel usando COM de Excel.
    Esto preserva 100% los formatos, imágenes, estilos, celdas combinadas, etc.
    """
    import win32com.client
    import pythoncom
    import time

    # Si el archivo destino existe, eliminarlo primero (evita conflictos con OneDrive)
    if destino.exists():
        try:
            destino.unlink()
            time.sleep(0.5)  # Pausa para que OneDrive procese la eliminación
            print(f"  Archivo existente eliminado")
        except Exception as e:
            print(f"  ADVERTENCIA: No se pudo eliminar archivo existente: {e}")

    pythoncom.CoInitialize()
    excel = None

    try:
        print("  Iniciando Excel...")
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        print(f"  Abriendo formato original...")
        wb = excel.Workbooks.Open(str(origen))

        print(f"  Guardando copia en: {destino}")
        wb.SaveAs(str(destino))
        wb.Close(SaveChanges=False)

        print("  Copia completada exitosamente")
        return True

    except Exception as e:
        print(f"  ERROR al copiar con Excel: {e}")
        return False

    finally:
        if excel:
            excel.Quit()
        pythoncom.CoUninitialize()


def llenar_certificacion(ruta_excel: Path, hu_data: dict) -> bool:
    """Llena los campos de la certificación usando Excel COM (maneja celdas combinadas)."""
    import win32com.client
    import pythoncom

    pythoncom.CoInitialize()
    excel = None

    try:
        print("  Abriendo archivo con Excel...")
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        wb = excel.Workbooks.Open(str(ruta_excel))
        ws = wb.ActiveSheet

        # F13: Aprobador QA
        nombre_aprobador = extraer_nombre_aprobador(hu_data.get('aprobador_qa', ''))
        ws.Range("F13").Value = nombre_aprobador
        print(f"    F13 (Aprobador): {nombre_aprobador}")

        # H12: HU + Iteration Path
        hu_texto = f"HU{hu_data['id']} - {hu_data.get('iteration_path', '')}"
        ws.Range("H12").Value = hu_texto
        print(f"    H12 (HU): {hu_texto}")

        # H13: Módulo Balu
        modulo = hu_data.get('modulo_balu', '')
        ws.Range("H13").Value = modulo
        print(f"    H13 (Módulo): {modulo}")

        # Test Cases desde fila 21
        test_cases = hu_data.get('test_cases', [])
        num_tc = len(test_cases)
        print(f"    Procesando {num_tc} Test Cases...")

        if num_tc > 1:
            # Duplicar la fila 21 (num_tc - 1) veces para tener espacio para todos los TC
            print(f"    Duplicando fila 21 ({num_tc - 1} veces)...")
            for i in range(num_tc - 1):
                # Copiar la fila 21
                ws.Rows(21).Copy()
                # Insertar debajo de la fila 21 + i
                ws.Rows(22 + i).Insert(Shift=-4121)  # xlShiftDown = -4121

        # Llenar los datos en cada fila
        print(f"    Llenando datos de Test Cases...")
        for i, tc in enumerate(test_cases):
            fila = 21 + i
            ws.Range(f"C{fila}").Value = tc['id']
            ws.Range(f"D{fila}").Value = tc['title']

        wb.Save()
        wb.Close(SaveChanges=True)

        print("  Datos llenados exitosamente")
        return True

    except Exception as e:
        print(f"  ERROR al llenar certificación: {e}")
        return False

    finally:
        if excel:
            excel.Quit()
        pythoncom.CoUninitialize()


def main():
    print("\n" + "=" * 65)
    print("      CREACIÓN DE CERTIFICACIÓN QA - MODO INDIVIDUAL")
    print("=" * 65 + "\n")

    # Verificar archivos
    print("[1/5] Verificando archivos necesarios...")

    if not FORMATO_ORIGINAL.exists():
        print(f"  ERROR: No se encuentra el formato en:")
        print(f"         {FORMATO_ORIGINAL}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    print(f"  [OK] Formato oficial encontrado")

    if not CSV_PATH.exists():
        print(f"  ERROR: No se encuentra el CSV en:")
        print(f"         {CSV_PATH}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    print(f"  [OK] CSV de datos encontrado")

    # Solicitar ID
    print("\n[2/5] Identificación de Historia de Usuario")
    hu_id = input("  Ingrese el ID de la HU (ej: 83439): ").strip()

    if not hu_id.isdigit():
        print("  ERROR: El ID debe ser numérico")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    # Leer datos del CSV
    print(f"\n[3/5] Buscando HU{hu_id} en el CSV...")
    hu_data = leer_datos_hu(hu_id)

    if not hu_data:
        print(f"  ERROR: No se encontró la HU con ID {hu_id}")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    print(f"  [OK] HU encontrada:")
    print(f"       Título: {hu_data['title'][:55]}...")
    print(f"       Módulo: {hu_data['modulo_balu']}")
    print(f"       Aprobador: {extraer_nombre_aprobador(hu_data['aprobador_qa'])}")
    print(f"       Test Cases: {len(hu_data['test_cases'])}")

    # Determinar ruta destino
    carpeta = determinar_carpeta_modulo(hu_data['modulo_balu'])
    destino_dir = CERTIFICACIONES_ROOT / carpeta
    destino_dir.mkdir(parents=True, exist_ok=True)
    archivo_destino = destino_dir / f"Certificacion_QA_{hu_id}.xlsx"

    # Verificar si ya existe
    if archivo_destino.exists():
        print(f"\n  ADVERTENCIA: El archivo ya existe:")
        print(f"  {archivo_destino}")
        respuesta = input("  ¿Desea sobrescribirlo? (S/N): ").strip().upper()
        if respuesta != 'S':
            print("  Operación cancelada.")
            input("\nPresione Enter para salir...")
            sys.exit(0)

    # Copiar formato con Excel COM
    print(f"\n[4/5] Copiando formato oficial (Excel COM)...")
    if not copiar_con_excel_com(FORMATO_ORIGINAL, archivo_destino):
        print("  ERROR: No se pudo copiar el formato")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    # Llenar datos con openpyxl
    print(f"\n[5/5] Llenando datos de certificación...")
    if not llenar_certificacion(archivo_destino, hu_data):
        print("  ERROR: No se pudo llenar la certificación")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    # Éxito
    print("\n" + "=" * 65)
    print("           CERTIFICACIÓN CREADA EXITOSAMENTE")
    print("=" * 65)
    print(f"\n  Archivo: {archivo_destino}\n")

    abrir = input("  ¿Desea abrir el archivo? (S/N): ").strip().upper()
    if abrir == 'S':
        os.startfile(archivo_destino)

    input("\nPresione Enter para salir...")


if __name__ == "__main__":
    main()
