"""
HERRAMIENTA DE ANÁLISIS DE DATOS - AutCert
==========================================
Análisis completo de data.csv usando pandas para mejor manipulación de datos.

Funcionalidades:
- Estadísticas generales del proyecto
- Análisis por tester, módulo, HU
- Detección de datos faltantes
- Exportación de datasets filtrados
- Reportes personalizados

Uso: py analizar_datos.py
"""

import sys
import pandas as pd
import os
from datetime import datetime
from collections import Counter
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener la raíz del proyecto AutCert (2 niveles arriba: Analisis -> Modulos -> AutCert)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import CSV_PATH_STR, REPORTES_DIR_STR

CSV_PATH = CSV_PATH_STR
EXPORT_PATH = REPORTES_DIR_STR

def cargar_datos():
    """Carga el CSV en un DataFrame de pandas"""
    if not os.path.exists(CSV_PATH):
        print(f"✗ No se encontró el archivo: {CSV_PATH}")
        return None

    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        print(f"✓ Datos cargados: {len(df)} registros")
        return df
    except Exception as e:
        print(f"✗ Error al cargar datos: {e}")
        return None

def analisis_general(df):
    """Estadísticas generales del proyecto"""
    print("\n" + "="*80)
    print("ANÁLISIS GENERAL DEL PROYECTO")
    print("="*80)

    total_registros = len(df)

    # Contar por tipo de work item
    tipos = df['Work Item Type'].value_counts()
    print(f"\nTotal de registros: {total_registros}")
    print(f"\nDistribución por tipo:")
    for tipo, cantidad in tipos.items():
        porcentaje = (cantidad / total_registros) * 100
        print(f"  {tipo}: {cantidad} ({porcentaje:.1f}%)")

    # Estadísticas de User Stories
    user_stories = df[df['Work Item Type'] == 'User Story']
    test_cases = df[df['Work Item Type'] == 'Test Case']

    print(f"\n📊 User Stories: {len(user_stories)}")
    print(f"📊 Test Cases: {len(test_cases)}")

    if len(user_stories) > 0:
        tcs_por_hu = len(test_cases) / len(user_stories)
        print(f"📊 Promedio TCs por HU: {tcs_por_hu:.2f}")

    # Estados
    if 'State' in df.columns:
        estados = df['State'].value_counts()
        print(f"\nEstados de work items:")
        for estado, cantidad in estados.items():
            print(f"  {estado}: {cantidad}")

def analisis_por_tester(df):
    """Análisis detallado por tester"""
    print("\n" + "="*80)
    print("ANÁLISIS POR TESTER")
    print("="*80)

    user_stories = df[df['Work Item Type'] == 'User Story'].copy()

    if 'Tester' not in user_stories.columns:
        print("✗ No se encontró columna 'Tester'")
        return

    # Limpiar valores vacíos
    user_stories = user_stories[user_stories['Tester'].notna()]
    user_stories = user_stories[user_stories['Tester'].str.strip() != '']

    if len(user_stories) == 0:
        print("✗ No hay HUs con tester asignado")
        return

    testers_stats = user_stories.groupby('Tester').agg({
        'ID': 'count',
        'Modulo Balu': lambda x: x.value_counts().to_dict() if 'Modulo Balu' in user_stories.columns else {}
    }).rename(columns={'ID': 'HUs_Asignadas'})

    testers_stats = testers_stats.sort_values('HUs_Asignadas', ascending=False)

    print(f"\nTotal testers: {len(testers_stats)}")
    print(f"\nHUs asignadas por tester:")
    for tester, row in testers_stats.iterrows():
        print(f"\n  {tester}")
        print(f"    HUs: {row['HUs_Asignadas']}")

        # Calcular TCs para este tester
        tester_hus = user_stories[user_stories['Tester'] == tester]['ID'].tolist()
        tc_count = contar_tcs_para_hus(df, tester_hus)
        print(f"    TCs estimados: {tc_count}")

def contar_tcs_para_hus(df, hu_ids):
    """Cuenta los TCs asociados a una lista de HUs"""
    total_tcs = 0
    hu_actual = None
    capturando = False

    for _, row in df.iterrows():
        work_type = row.get('Work Item Type', '')

        if work_type == 'User Story':
            if str(row['ID']) in [str(hu) for hu in hu_ids]:
                capturando = True
                hu_actual = row['ID']
            else:
                capturando = False

        elif work_type == 'Test Case' and capturando:
            total_tcs += 1

    return total_tcs

def analisis_por_modulo(df):
    """Análisis por módulo Balu"""
    print("\n" + "="*80)
    print("ANÁLISIS POR MÓDULO")
    print("="*80)

    user_stories = df[df['Work Item Type'] == 'User Story'].copy()

    if 'Modulo Balu' not in user_stories.columns:
        print("✗ No se encontró columna 'Modulo Balu'")
        return

    user_stories = user_stories[user_stories['Modulo Balu'].notna()]
    user_stories = user_stories[user_stories['Modulo Balu'].str.strip() != '']

    modulos = user_stories['Modulo Balu'].value_counts()

    print(f"\nDistribución por módulo:")
    for modulo, cantidad in modulos.items():
        print(f"\n  {modulo}: {cantidad} HUs")

        # Contar TCs para este módulo
        modulo_hus = user_stories[user_stories['Modulo Balu'] == modulo]['ID'].tolist()
        tc_count = contar_tcs_para_hus(df, modulo_hus)
        print(f"    TCs estimados: {tc_count}")

def analisis_calidad_datos(df):
    """Detecta problemas de calidad en los datos"""
    print("\n" + "="*80)
    print("ANÁLISIS DE CALIDAD DE DATOS")
    print("="*80)

    user_stories = df[df['Work Item Type'] == 'User Story'].copy()

    # Campos críticos
    campos_criticos = ['Tester', 'Aprobador QA', 'Modulo Balu']

    print("\nCampos con valores faltantes:")
    for campo in campos_criticos:
        if campo in user_stories.columns:
            faltantes = user_stories[campo].isna().sum()
            vacios = (user_stories[campo].astype(str).str.strip() == '').sum()
            total_problemas = faltantes + vacios
            porcentaje = (total_problemas / len(user_stories)) * 100

            print(f"  {campo}: {total_problemas}/{len(user_stories)} ({porcentaje:.1f}%)")

            if total_problemas > 0:
                hus_problematicas = user_stories[
                    user_stories[campo].isna() |
                    (user_stories[campo].astype(str).str.strip() == '')
                ]['ID'].tolist()
                print(f"    HUs afectadas: {hus_problematicas[:5]}{'...' if len(hus_problematicas) > 5 else ''}")

    # Duplicados
    duplicados = df.duplicated(subset=['ID']).sum()
    print(f"\nIDs duplicados: {duplicados}")

    if duplicados > 0:
        ids_duplicados = df[df.duplicated(subset=['ID'], keep=False)]['ID'].tolist()
        print(f"  IDs afectados: {list(set(ids_duplicados))[:10]}")

def analisis_aprobadores(df):
    """Análisis de aprobadores QA"""
    print("\n" + "="*80)
    print("ANÁLISIS DE APROBADORES QA")
    print("="*80)

    user_stories = df[df['Work Item Type'] == 'User Story'].copy()

    if 'Aprobador QA' not in user_stories.columns:
        print("✗ No se encontró columna 'Aprobador QA'")
        return

    # Contar por aprobador
    aprobadores = user_stories['Aprobador QA'].value_counts(dropna=False)

    print(f"\nDistribución de aprobadores:")
    for aprobador, cantidad in aprobadores.items():
        if pd.isna(aprobador) or str(aprobador).strip() == '':
            print(f"  [SIN ASIGNAR]: {cantidad} HUs")
        else:
            print(f"  {aprobador}: {cantidad} HUs")

def exportar_dataset(df, filtro_nombre, condicion):
    """Exporta un dataset filtrado a CSV"""
    os.makedirs(EXPORT_PATH, exist_ok=True)

    df_filtrado = df[condicion].copy()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filtro_nombre}_{timestamp}.csv"
    filepath = os.path.join(EXPORT_PATH, filename)

    df_filtrado.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"✓ Exportado: {filename} ({len(df_filtrado)} registros)")
    return filepath

def menu_exportar(df):
    """Menú interactivo para exportar datasets"""
    print("\n" + "="*80)
    print("EXPORTAR DATASETS FILTRADOS")
    print("="*80)

    opciones = {
        '1': ('Solo User Stories', df['Work Item Type'] == 'User Story'),
        '2': ('Solo Test Cases', df['Work Item Type'] == 'Test Case'),
        '3': ('HUs sin Tester', (df['Work Item Type'] == 'User Story') &
                                 (df['Tester'].isna() | (df['Tester'].str.strip() == ''))),
        '4': ('HUs sin Aprobador QA', (df['Work Item Type'] == 'User Story') &
                                       (df['Aprobador QA'].isna() | (df['Aprobador QA'].str.strip() == ''))),
        '5': ('Dataset completo', df['ID'].notna())
    }

    print("\nOpciones de exportación:")
    for key, (nombre, _) in opciones.items():
        print(f"  {key}. {nombre}")
    print("  0. Volver al menú principal")

    seleccion = input("\nSelecciona una opción: ").strip()

    if seleccion == '0':
        return

    if seleccion in opciones:
        nombre, condicion = opciones[seleccion]
        exportar_dataset(df, nombre.replace(' ', '_'), condicion)
    else:
        print("✗ Opción inválida")

def generar_reporte_completo(df):
    """Genera un reporte completo en archivo de texto"""
    os.makedirs(EXPORT_PATH, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Reporte_Completo_{timestamp}.txt"
    filepath = os.path.join(EXPORT_PATH, filename)

    original_stdout = sys.stdout

    with open(filepath, 'w', encoding='utf-8') as f:
        sys.stdout = f

        print("="*80)
        print("REPORTE COMPLETO DE ANÁLISIS - AutCert")
        print(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        analisis_general(df)
        analisis_por_tester(df)
        analisis_por_modulo(df)
        analisis_calidad_datos(df)
        analisis_aprobadores(df)

    sys.stdout = original_stdout
    print(f"\n✓ Reporte completo generado: {filename}")
    return filepath

def menu_principal():
    """Menú principal interactivo"""
    df = cargar_datos()

    if df is None:
        return

    while True:
        print("\n" + "="*80)
        print("HERRAMIENTA DE ANÁLISIS DE DATOS - AutCert")
        print("="*80)
        print("\n1. Análisis General")
        print("2. Análisis por Tester")
        print("3. Análisis por Módulo")
        print("4. Análisis de Calidad de Datos")
        print("5. Análisis de Aprobadores QA")
        print("6. Exportar Datasets Filtrados")
        print("7. Generar Reporte Completo")
        print("0. Salir")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == '0':
            print("\n✓ Saliendo...")
            break
        elif opcion == '1':
            analisis_general(df)
        elif opcion == '2':
            analisis_por_tester(df)
        elif opcion == '3':
            analisis_por_modulo(df)
        elif opcion == '4':
            analisis_calidad_datos(df)
        elif opcion == '5':
            analisis_aprobadores(df)
        elif opcion == '6':
            menu_exportar(df)
        elif opcion == '7':
            generar_reporte_completo(df)
        else:
            print("✗ Opción inválida")

        input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    menu_principal()
