"""
TEST: Verificar búsqueda de certificaciones
============================================
Este script prueba la función de búsqueda de certificaciones
para asegurarse de que encuentra los archivos con el formato correcto.
"""

import sys
import os
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener la raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.resolve()

# Añadir al path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración
from config_paths import CERTIFICACIONES_ROOT

def buscar_excel_certificacion(numero_hu):
    """Busca el Excel de certificación de una HU"""
    categorias = ['AyN', 'RyC', 'Transversal']

    print(f"\n🔍 Buscando certificación para HU{numero_hu}...")
    print(f"   Ruta base: {CERTIFICACIONES_ROOT}")

    for cat in categorias:
        # Formato correcto: Certificacion_QA_{numero}.xlsx
        ruta = CERTIFICACIONES_ROOT / cat / f"Certificacion_QA_{numero_hu}.xlsx"
        print(f"   Buscando en {cat}/: {ruta.name}...", end=" ")

        if ruta.exists():
            print("✓ ENCONTRADO")
            return str(ruta)
        else:
            print("✗ No existe")

    return None

def listar_certificaciones_disponibles():
    """Lista todas las certificaciones disponibles"""
    print("\n📋 Certificaciones disponibles:")
    print("="*80)

    categorias = ['AyN', 'RyC', 'Transversal']

    for cat in categorias:
        carpeta = CERTIFICACIONES_ROOT / cat
        if carpeta.exists():
            archivos = sorted(carpeta.glob("Certificacion_QA_*.xlsx"))
            if archivos:
                print(f"\n{cat}:")
                for archivo in archivos:
                    # Extraer número de HU
                    nombre = archivo.stem  # Certificacion_QA_83509
                    numero = nombre.split('_')[-1]
                    print(f"  - HU{numero}: {archivo.name}")
            else:
                print(f"\n{cat}: (vacía)")
        else:
            print(f"\n{cat}: (carpeta no existe)")

def main():
    print("="*80)
    print("TEST: BÚSQUEDA DE CERTIFICACIONES")
    print("="*80)

    # Listar certificaciones disponibles
    listar_certificaciones_disponibles()

    # Test interactivo
    print("\n" + "="*80)
    print("TEST INTERACTIVO")
    print("="*80)

    numero_hu = input("\nIngresa el número de HU para buscar (o Enter para salir): ").strip()

    if numero_hu:
        resultado = buscar_excel_certificacion(numero_hu)

        print("\n" + "="*80)
        if resultado:
            print("✅ RESULTADO: CERTIFICACIÓN ENCONTRADA")
            print("="*80)
            print(f"\nRuta completa:\n{resultado}")
        else:
            print("❌ RESULTADO: CERTIFICACIÓN NO ENCONTRADA")
            print("="*80)
            print(f"\nNo se encontró Certificacion_QA_{numero_hu}.xlsx")
            print("en ninguna de las categorías (AyN, RyC, Transversal)")

    print("\n" + "="*80)
    print("Presiona ENTER para salir...")
    input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona ENTER para salir...")
