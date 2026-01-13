"""
test_validacion.py
Script de prueba para validar la lectura de datos antes de crear certificaciones.
"""

import csv
import re
from pathlib import Path

# Rutas base
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CSV_PATH = PROJECT_ROOT / "Assets" / "Base de datos" / "data.csv"

APROBADOR_DEFAULT = "Victor Alejandro Moreno Gonzalez"


def extraer_nombre_aprobador(aprobador_completo: str) -> str:
    if not aprobador_completo:
        return APROBADOR_DEFAULT
    match = re.match(r'^([^<]+)', aprobador_completo)
    if match:
        return match.group(1).strip()
    return aprobador_completo.strip()


def extraer_nombre(texto_completo: str) -> str:
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


def main():
    print("\n" + "=" * 70)
    print("       VALIDACIÓN DE DATOS - TEST")
    print("=" * 70 + "\n")

    print(f"CSV Path: {CSV_PATH}")
    print(f"Existe: {CSV_PATH.exists()}\n")

    # Leer datos
    todas_las_hu = leer_todas_las_hu()
    print(f"Total HU encontradas: {len(todas_las_hu)}\n")

    # Estadísticas
    hu_con_tc = [hu for hu in todas_las_hu if len(hu['test_cases']) > 0]
    hu_sin_tc = [hu for hu in todas_las_hu if len(hu['test_cases']) == 0]
    hu_sin_aprobador = [hu for hu in todas_las_hu if not hu['aprobador_qa']]

    print(f"HU con Test Cases: {len(hu_con_tc)}")
    print(f"HU sin Test Cases: {len(hu_sin_tc)}")
    print(f"HU sin Aprobador QA (usarán default): {len(hu_sin_aprobador)}\n")

    # Mostrar detalle de las primeras 5 HU
    print("-" * 70)
    print("DETALLE DE PRIMERAS 5 HU:")
    print("-" * 70)

    for hu in todas_las_hu[:5]:
        print(f"\nHU{hu['id']}:")
        print(f"  Título: {hu['title'][:50]}...")
        print(f"  Módulo: {hu['modulo_balu']}")
        print(f"  Tester: {extraer_nombre(hu['tester'])}")
        print(f"  Aprobador Original: '{hu['aprobador_qa']}'")
        print(f"  Aprobador Final: {extraer_nombre_aprobador(hu['aprobador_qa'])}")
        print(f"  Test Cases: {len(hu['test_cases'])}")

        if hu['test_cases']:
            print("  TCs:")
            for tc in hu['test_cases'][:3]:
                print(f"    - [{tc['id']}] {tc['title'][:40]}...")
            if len(hu['test_cases']) > 3:
                print(f"    ... y {len(hu['test_cases']) - 3} más")

    # Mostrar HU sin Test Cases
    if hu_sin_tc:
        print("\n" + "-" * 70)
        print("HU SIN TEST CASES (problema potencial):")
        print("-" * 70)
        for hu in hu_sin_tc[:10]:
            print(f"  HU{hu['id']}: {hu['title'][:50]}...")

    print("\n[Validación completada]")


if __name__ == "__main__":
    main()
