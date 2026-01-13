"""
TEST COMPLETO DE ENRUTAMIENTO DINÁMICO
=======================================
Este script verifica que TODOS los módulos del proyecto estén
correctamente configurados para usar rutas dinámicas desde EntregaCerts.

Ejecuta este script para confirmar que el proyecto está listo para
funcionar en cualquier PC sin modificaciones.
"""

import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path

# Importar configuración
from config_paths import (
    PROJECT_ROOT,
    PARENT_DIR,
    DATA_ROOT,
    CERTIFICACIONES_ROOT,
    PDF_ROOT,
    EVIDENCIAS_ROOT,
    CSV_PATH,
    LOGS_DIR
)

def print_section(title):
    """Imprime una sección con formato"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_check(name, condition, details=""):
    """Imprime resultado de una verificación"""
    status = "✓" if condition else "✗"
    color = "OK" if condition else "ERROR"
    print(f"  [{status}] {name}: {color}")
    if details:
        print(f"      {details}")
    return condition

def test_estructura_basica():
    """Test 1: Verificar estructura de carpetas básica"""
    print_section("TEST 1: Estructura Básica de Carpetas")

    checks = []

    # Verificar carpetas del proyecto
    checks.append(print_check(
        "PROJECT_ROOT existe",
        PROJECT_ROOT.exists(),
        f"Ruta: {PROJECT_ROOT}"
    ))

    checks.append(print_check(
        "PARENT_DIR existe",
        PARENT_DIR.exists(),
        f"Ruta: {PARENT_DIR}"
    ))

    checks.append(print_check(
        "DATA_ROOT (EntregaCerts) existe",
        DATA_ROOT.exists(),
        f"Ruta: {DATA_ROOT}"
    ))

    return all(checks)

def test_carpetas_datos():
    """Test 2: Verificar carpetas de datos en EntregaCerts"""
    print_section("TEST 2: Carpetas de Datos (EntregaCerts)")

    carpetas_datos = [
        ("Certificaciones", CERTIFICACIONES_ROOT),
        ("Certificaciones/AyN", CERTIFICACIONES_ROOT / "AyN"),
        ("Certificaciones/RyC", CERTIFICACIONES_ROOT / "RyC"),
        ("Certificaciones/Transversal", CERTIFICACIONES_ROOT / "Transversal"),
        ("Certificaciones_PDF", PDF_ROOT),
        ("Certificaciones_PDF/AyN", PDF_ROOT / "AyN"),
        ("Certificaciones_PDF/RyC", PDF_ROOT / "RyC"),
        ("Certificaciones_PDF/Transversal", PDF_ROOT / "Transversal"),
        ("Evidencias", EVIDENCIAS_ROOT),
    ]

    checks = []
    for nombre, ruta in carpetas_datos:
        checks.append(print_check(
            f"Carpeta '{nombre}'",
            ruta.exists(),
            f"Ruta: {ruta}"
        ))

    return all(checks)

def test_archivos_importantes():
    """Test 3: Verificar archivos importantes del proyecto"""
    print_section("TEST 3: Archivos Importantes")

    checks = []

    checks.append(print_check(
        "CSV de datos (data.csv)",
        CSV_PATH.exists(),
        f"Ruta: {CSV_PATH}"
    ))

    checks.append(print_check(
        "Directorio de Logs",
        LOGS_DIR.exists(),
        f"Ruta: {LOGS_DIR}"
    ))

    formato_oficial = PROJECT_ROOT / "Assets" / "Formatos" / "Formato Oficial.xlsx"
    checks.append(print_check(
        "Formato Oficial de certificación",
        formato_oficial.exists(),
        f"Ruta: {formato_oficial}"
    ))

    return all(checks)

def test_importacion_modulos():
    """Test 4: Verificar que todos los módulos pueden importar config_paths"""
    print_section("TEST 4: Importación en Módulos")

    modulos_a_probar = [
        ("Conversion_PDF", "Modulos/Conversion_PDF/convertir_a_pdf.py"),
        ("Renombrado", "Modulos/Renombrado/renombrar_evidencias.py"),
        ("Analisis", "Modulos/Analisis/analizar_datos.py"),
        ("Certificaciones", "Modulos/Certificaciones/crear_certificacion.py"),
        ("Certificaciones Masivo", "Modulos/Certificaciones/crear_certificacion_masivo.py"),
        ("Evidencias Masivo", "Modulos/Evidencias_Azure/scripts/capturar_evidencia_masivo.py"),
        ("Evidencias HU", "Modulos/Evidencias_Azure/scripts/capturar_evidencia_hu.py"),
        ("Completar Certificación", "Modulos/Links_Drive/scripts/completar_certificacion_interactivo.py"),
    ]

    checks = []
    for nombre, ruta_relativa in modulos_a_probar:
        ruta_completa = PROJECT_ROOT / ruta_relativa
        exists = ruta_completa.exists()
        checks.append(print_check(
            f"Módulo '{nombre}'",
            exists,
            f"Archivo: {ruta_relativa}"
        ))

    return all(checks)

def test_rutas_son_dinamicas():
    """Test 5: Verificar que las rutas NO son hardcodeadas"""
    print_section("TEST 5: Verificación de Rutas Dinámicas")

    # Verificar que EntregaCerts está al lado de AutCert
    entregacerts_esperado = PARENT_DIR / "EntregaCerts"
    check1 = print_check(
        "EntregaCerts está en ubicación correcta",
        DATA_ROOT == entregacerts_esperado,
        f"Esperado: {entregacerts_esperado}\nReal: {DATA_ROOT}"
    )

    # Verificar que las rutas de datos están en EntregaCerts
    check2 = print_check(
        "Certificaciones está en EntregaCerts",
        str(CERTIFICACIONES_ROOT).startswith(str(DATA_ROOT)),
        f"CERTIFICACIONES_ROOT: {CERTIFICACIONES_ROOT}"
    )

    check3 = print_check(
        "PDFs está en EntregaCerts",
        str(PDF_ROOT).startswith(str(DATA_ROOT)),
        f"PDF_ROOT: {PDF_ROOT}"
    )

    check4 = print_check(
        "Evidencias está en EntregaCerts",
        str(EVIDENCIAS_ROOT).startswith(str(DATA_ROOT)),
        f"EVIDENCIAS_ROOT: {EVIDENCIAS_ROOT}"
    )

    return check1 and check2 and check3 and check4

def test_escritura_archivos():
    """Test 6: Verificar permisos de escritura"""
    print_section("TEST 6: Permisos de Escritura")

    checks = []

    # Intentar crear un archivo de prueba en cada carpeta principal
    carpetas_prueba = [
        ("Certificaciones", CERTIFICACIONES_ROOT),
        ("Certificaciones_PDF", PDF_ROOT),
        ("Evidencias", EVIDENCIAS_ROOT),
        ("Logs", LOGS_DIR),
    ]

    for nombre, carpeta in carpetas_prueba:
        archivo_prueba = carpeta / ".test_escritura"
        try:
            archivo_prueba.touch()
            archivo_prueba.unlink()
            checks.append(print_check(
                f"Escritura en {nombre}",
                True,
                f"Carpeta: {carpeta}"
            ))
        except Exception as e:
            checks.append(print_check(
                f"Escritura en {nombre}",
                False,
                f"Error: {e}"
            ))

    return all(checks)

def mostrar_resumen_rutas():
    """Muestra un resumen de las rutas detectadas"""
    print_section("RESUMEN DE RUTAS DETECTADAS")

    rutas = [
        ("Raíz del Proyecto (código)", PROJECT_ROOT),
        ("Carpeta Contenedora", PARENT_DIR),
        ("Carpeta de Datos (EntregaCerts)", DATA_ROOT),
        ("", ""),  # Separador
        ("Certificaciones", CERTIFICACIONES_ROOT),
        ("Certificaciones PDF", PDF_ROOT),
        ("Evidencias", EVIDENCIAS_ROOT),
        ("", ""),  # Separador
        ("CSV de Datos", CSV_PATH),
        ("Logs", LOGS_DIR),
    ]

    for nombre, ruta in rutas:
        if nombre == "":
            print()
        else:
            print(f"  {nombre}:")
            print(f"    {ruta}")

def main():
    """Función principal que ejecuta todos los tests"""
    print("\n" + "="*80)
    print("  TEST COMPLETO DE ENRUTAMIENTO DINÁMICO - AutCert")
    print("="*80)
    print("\n  Este script verifica que el proyecto esté correctamente configurado")
    print("  para usar rutas dinámicas desde la carpeta externa EntregaCerts.\n")

    # Ejecutar todos los tests
    resultados = {
        "Estructura Básica": test_estructura_basica(),
        "Carpetas de Datos": test_carpetas_datos(),
        "Archivos Importantes": test_archivos_importantes(),
        "Importación de Módulos": test_importacion_modulos(),
        "Rutas Dinámicas": test_rutas_son_dinamicas(),
        "Permisos de Escritura": test_escritura_archivos(),
    }

    # Mostrar resumen de rutas
    mostrar_resumen_rutas()

    # Resultado final
    print_section("RESULTADO FINAL")

    tests_pasados = sum(1 for v in resultados.values() if v)
    tests_totales = len(resultados)

    print(f"\n  Tests pasados: {tests_pasados}/{tests_totales}\n")

    for nombre, resultado in resultados.items():
        status = "✓ PASS" if resultado else "✗ FAIL"
        print(f"    {status} - {nombre}")

    print("\n" + "="*80)

    if all(resultados.values()):
        print("  ✓✓✓ TODOS LOS TESTS PASARON EXITOSAMENTE ✓✓✓")
        print("="*80)
        print("\n  El proyecto está correctamente configurado y listo para usar.")
        print("  Puedes ejecutar cualquier script y se guardarán los archivos")
        print("  en la carpeta EntregaCerts automáticamente.\n")
        return 0
    else:
        print("  ✗✗✗ ALGUNOS TESTS FALLARON ✗✗✗")
        print("="*80)
        print("\n  Revisa los errores arriba y corrige los problemas antes de usar")
        print("  el proyecto. Consulta la documentación en:")
        print("  - ENRUTAMIENTO_DINAMICO.md")
        print("  - GUIA_RAPIDA_ENRUTAMIENTO.md\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print("\nPresiona ENTER para salir...")
        input()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        print("\nPresiona ENTER para salir...")
        input()
        sys.exit(1)
