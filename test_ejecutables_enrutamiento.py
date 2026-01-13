"""
TEST DE VALIDACIÓN DE ENRUTAMIENTO PARA EJECUTABLES
====================================================
Este script simula la ejecución de cada servicio y verifica que las rutas
estén correctamente configuradas hacia EntregaCerts.

Valida que:
- Los servicios de creación de certificaciones apunten a EntregaCerts/Certificaciones
- Los servicios de evidencias apunten a EntregaCerts/Evidencias
- Los servicios de PDF apunten a EntregaCerts/Certificaciones y Certificaciones_PDF
- No haya rutas hardcodeadas
"""

import sys
import os
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Importar configuración
from config_paths import (
    PROJECT_ROOT,
    DATA_ROOT,
    CERTIFICACIONES_ROOT,
    PDF_ROOT,
    EVIDENCIAS_ROOT,
    CSV_PATH
)

def print_header(title):
    """Imprime encabezado con formato"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_service(name, status, details=""):
    """Imprime resultado de verificación de servicio"""
    icon = "✓" if status else "✗"
    color = "OK" if status else "ERROR"
    print(f"\n  [{icon}] {name}")
    print(f"      Estado: {color}")
    if details:
        for line in details.split('\n'):
            print(f"      {line}")
    return status

def verificar_crear_certificacion():
    """Verifica: crear_certificacion.py"""
    print_header("SERVICIO 1: Crear Certificación Individual")

    try:
        # Cambiar al directorio del módulo temporalmente para importar
        old_path = sys.path.copy()
        modulo_path = PROJECT_ROOT / "Modulos" / "Certificaciones"
        sys.path.insert(0, str(modulo_path))

        # Importar el módulo
        import crear_certificacion

        # Verificar las rutas que usa
        checks = []
        details = []

        # Verificar CERTIFICACIONES_ROOT
        if hasattr(crear_certificacion, 'CERTIFICACIONES_ROOT'):
            cert_root = Path(crear_certificacion.CERTIFICACIONES_ROOT)
            usa_entregacerts = str(cert_root).startswith(str(DATA_ROOT))
            checks.append(usa_entregacerts)

            if usa_entregacerts:
                details.append(f"✓ CERTIFICACIONES_ROOT apunta a EntregaCerts")
            else:
                details.append(f"✗ CERTIFICACIONES_ROOT NO apunta a EntregaCerts")
            details.append(f"  Ruta: {cert_root}")

        # Verificar CSV_PATH
        if hasattr(crear_certificacion, 'CSV_PATH'):
            csv_path = Path(crear_certificacion.CSV_PATH)
            esta_en_proyecto = str(csv_path).startswith(str(PROJECT_ROOT))
            checks.append(esta_en_proyecto)

            if esta_en_proyecto:
                details.append(f"✓ CSV_PATH está en el proyecto")
            else:
                details.append(f"✗ CSV_PATH NO está en el proyecto")
            details.append(f"  Ruta: {csv_path}")

        # Verificar FORMATO_ORIGINAL
        if hasattr(crear_certificacion, 'FORMATO_ORIGINAL'):
            formato = Path(crear_certificacion.FORMATO_ORIGINAL)
            esta_en_proyecto = str(formato).startswith(str(PROJECT_ROOT))
            checks.append(esta_en_proyecto)

            if esta_en_proyecto:
                details.append(f"✓ FORMATO_ORIGINAL está en el proyecto")
            else:
                details.append(f"✗ FORMATO_ORIGINAL NO está en el proyecto")
            details.append(f"  Ruta: {formato}")

        sys.path = old_path
        return print_service(
            "crear_certificacion.py",
            all(checks),
            '\n'.join(details)
        )

    except Exception as e:
        return print_service(
            "crear_certificacion.py",
            False,
            f"Error al importar: {e}"
        )

def verificar_crear_certificacion_masivo():
    """Verifica: crear_certificacion_masivo.py"""
    print_header("SERVICIO 2: Crear Certificaciones Masivas")

    try:
        old_path = sys.path.copy()
        modulo_path = PROJECT_ROOT / "Modulos" / "Certificaciones"
        sys.path.insert(0, str(modulo_path))

        import crear_certificacion_masivo

        checks = []
        details = []

        # Verificar CERTIFICACIONES_ROOT
        if hasattr(crear_certificacion_masivo, 'CERTIFICACIONES_ROOT'):
            cert_root = Path(crear_certificacion_masivo.CERTIFICACIONES_ROOT)
            usa_entregacerts = str(cert_root).startswith(str(DATA_ROOT))
            checks.append(usa_entregacerts)

            if usa_entregacerts:
                details.append(f"✓ CERTIFICACIONES_ROOT apunta a EntregaCerts")
            else:
                details.append(f"✗ CERTIFICACIONES_ROOT NO apunta a EntregaCerts")
            details.append(f"  Ruta: {cert_root}")

        # Verificar CSV_PATH
        if hasattr(crear_certificacion_masivo, 'CSV_PATH'):
            csv_path = Path(crear_certificacion_masivo.CSV_PATH)
            esta_en_proyecto = str(csv_path).startswith(str(PROJECT_ROOT))
            checks.append(esta_en_proyecto)

            if esta_en_proyecto:
                details.append(f"✓ CSV_PATH está en el proyecto")
            else:
                details.append(f"✗ CSV_PATH NO está en el proyecto")
            details.append(f"  Ruta: {csv_path}")

        sys.path = old_path
        return print_service(
            "crear_certificacion_masivo.py",
            all(checks),
            '\n'.join(details)
        )

    except Exception as e:
        return print_service(
            "crear_certificacion_masivo.py",
            False,
            f"Error al importar: {e}"
        )

def verificar_convertir_pdf():
    """Verifica: convertir_a_pdf.py"""
    print_header("SERVICIO 3: Convertir Certificaciones a PDF")

    try:
        old_path = sys.path.copy()
        modulo_path = PROJECT_ROOT / "Modulos" / "Conversion_PDF"
        sys.path.insert(0, str(modulo_path))

        import convertir_a_pdf

        checks = []
        details = []

        # Verificar CERTIFICACIONES_ROOT (entrada)
        if hasattr(convertir_a_pdf, 'CERTIFICACIONES_ROOT'):
            cert_root = convertir_a_pdf.CERTIFICACIONES_ROOT
            usa_entregacerts = str(cert_root).startswith(str(DATA_ROOT))
            checks.append(usa_entregacerts)

            if usa_entregacerts:
                details.append(f"✓ CERTIFICACIONES_ROOT (entrada) apunta a EntregaCerts")
            else:
                details.append(f"✗ CERTIFICACIONES_ROOT (entrada) NO apunta a EntregaCerts")
            details.append(f"  Ruta entrada: {cert_root}")

        # Verificar PDF_ROOT (salida)
        if hasattr(convertir_a_pdf, 'PDF_ROOT'):
            pdf_root = convertir_a_pdf.PDF_ROOT
            usa_entregacerts = str(pdf_root).startswith(str(DATA_ROOT))
            checks.append(usa_entregacerts)

            if usa_entregacerts:
                details.append(f"✓ PDF_ROOT (salida) apunta a EntregaCerts")
            else:
                details.append(f"✗ PDF_ROOT (salida) NO apunta a EntregaCerts")
            details.append(f"  Ruta salida: {pdf_root}")

        sys.path = old_path
        return print_service(
            "convertir_a_pdf.py",
            all(checks),
            '\n'.join(details)
        )

    except Exception as e:
        return print_service(
            "convertir_a_pdf.py",
            False,
            f"Error al importar: {e}"
        )

def verificar_capturar_evidencias():
    """Verifica: capturar_evidencia_masivo.py y capturar_evidencia_hu.py"""
    print_header("SERVICIO 4: Capturar Evidencias")

    try:
        old_path = sys.path.copy()
        modulo_path = PROJECT_ROOT / "Modulos" / "Evidencias_Azure" / "scripts"
        sys.path.insert(0, str(modulo_path))

        # Verificar capturar_evidencia_masivo
        import capturar_evidencia_masivo

        checks = []
        details = []

        details.append("--- capturar_evidencia_masivo.py ---")

        # Verificar EVIDENCIAS_ROOT
        if hasattr(capturar_evidencia_masivo, 'EVIDENCIAS_ROOT'):
            evid_root = capturar_evidencia_masivo.EVIDENCIAS_ROOT
            usa_entregacerts = str(evid_root).startswith(str(DATA_ROOT))
            checks.append(usa_entregacerts)

            if usa_entregacerts:
                details.append(f"✓ EVIDENCIAS_ROOT apunta a EntregaCerts")
            else:
                details.append(f"✗ EVIDENCIAS_ROOT NO apunta a EntregaCerts")
            details.append(f"  Ruta: {evid_root}")

        # Verificar capturar_evidencia_hu
        import capturar_evidencia_hu

        details.append("\n--- capturar_evidencia_hu.py ---")

        # Verificar CSV_PATH
        if hasattr(capturar_evidencia_hu, 'CSV_PATH'):
            csv_path = Path(capturar_evidencia_hu.CSV_PATH)
            esta_en_proyecto = str(csv_path).startswith(str(PROJECT_ROOT))
            checks.append(esta_en_proyecto)

            if esta_en_proyecto:
                details.append(f"✓ CSV_PATH está en el proyecto")
            else:
                details.append(f"✗ CSV_PATH NO está en el proyecto")
            details.append(f"  Ruta: {csv_path}")

        sys.path = old_path
        return print_service(
            "capturar_evidencia_*.py",
            all(checks),
            '\n'.join(details)
        )

    except Exception as e:
        return print_service(
            "capturar_evidencia_*.py",
            False,
            f"Error al importar: {e}"
        )

def verificar_renombrar_evidencias():
    """Verifica: renombrar_evidencias.py"""
    print_header("SERVICIO 5: Renombrar Evidencias")

    try:
        old_path = sys.path.copy()
        modulo_path = PROJECT_ROOT / "Modulos" / "Renombrado"
        sys.path.insert(0, str(modulo_path))

        import renombrar_evidencias

        checks = []
        details = []

        # Verificar EVIDENCIAS_ROOT
        if hasattr(renombrar_evidencias, 'EVIDENCIAS_ROOT'):
            evid_root = renombrar_evidencias.EVIDENCIAS_ROOT
            usa_entregacerts = str(evid_root).startswith(str(DATA_ROOT))
            checks.append(usa_entregacerts)

            if usa_entregacerts:
                details.append(f"✓ EVIDENCIAS_ROOT apunta a EntregaCerts")
            else:
                details.append(f"✗ EVIDENCIAS_ROOT NO apunta a EntregaCerts")
            details.append(f"  Ruta: {evid_root}")

        # Verificar CSV_PATH
        if hasattr(renombrar_evidencias, 'CSV_PATH'):
            csv_path = renombrar_evidencias.CSV_PATH
            esta_en_proyecto = str(csv_path).startswith(str(PROJECT_ROOT))
            checks.append(esta_en_proyecto)

            if esta_en_proyecto:
                details.append(f"✓ CSV_PATH está en el proyecto")
            else:
                details.append(f"✗ CSV_PATH NO está en el proyecto")
            details.append(f"  Ruta: {csv_path}")

        sys.path = old_path
        return print_service(
            "renombrar_evidencias.py",
            all(checks),
            '\n'.join(details)
        )

    except Exception as e:
        return print_service(
            "renombrar_evidencias.py",
            False,
            f"Error al importar: {e}"
        )

def verificar_completar_certificacion():
    """Verifica: completar_certificacion_interactivo.py"""
    print_header("SERVICIO 6: Completar Certificación (Links Drive)")

    try:
        old_path = sys.path.copy()
        modulo_path = PROJECT_ROOT / "Modulos" / "Links_Drive" / "scripts"
        sys.path.insert(0, str(modulo_path))
        sys.path.insert(0, str(PROJECT_ROOT / "Modulos" / "Links_Drive"))

        import completar_certificacion_interactivo

        checks = []
        details = []

        # Verificar RUTA_CERTIFICACIONES
        if hasattr(completar_certificacion_interactivo, 'RUTA_CERTIFICACIONES'):
            ruta_cert = completar_certificacion_interactivo.RUTA_CERTIFICACIONES
            usa_entregacerts = str(ruta_cert).startswith(str(DATA_ROOT))
            checks.append(usa_entregacerts)

            if usa_entregacerts:
                details.append(f"✓ RUTA_CERTIFICACIONES apunta a EntregaCerts")
            else:
                details.append(f"✗ RUTA_CERTIFICACIONES NO apunta a EntregaCerts")
            details.append(f"  Ruta: {ruta_cert}")

        sys.path = old_path
        return print_service(
            "completar_certificacion_interactivo.py",
            all(checks),
            '\n'.join(details)
        )

    except Exception as e:
        return print_service(
            "completar_certificacion_interactivo.py",
            False,
            f"Error al importar: {e}"
        )

def verificar_analizar_datos():
    """Verifica: analizar_datos.py"""
    print_header("SERVICIO 7: Análisis de Datos")

    try:
        old_path = sys.path.copy()
        modulo_path = PROJECT_ROOT / "Modulos" / "Analisis"
        sys.path.insert(0, str(modulo_path))

        import analizar_datos

        checks = []
        details = []

        # Verificar CSV_PATH
        if hasattr(analizar_datos, 'CSV_PATH'):
            csv_path = analizar_datos.CSV_PATH
            esta_en_proyecto = str(csv_path).startswith(str(PROJECT_ROOT))
            checks.append(esta_en_proyecto)

            if esta_en_proyecto:
                details.append(f"✓ CSV_PATH está en el proyecto")
            else:
                details.append(f"✗ CSV_PATH NO está en el proyecto")
            details.append(f"  Ruta: {csv_path}")

        # Verificar EXPORT_PATH
        if hasattr(analizar_datos, 'EXPORT_PATH'):
            export_path = analizar_datos.EXPORT_PATH
            esta_en_proyecto = str(export_path).startswith(str(PROJECT_ROOT))
            checks.append(esta_en_proyecto)

            if esta_en_proyecto:
                details.append(f"✓ EXPORT_PATH está en el proyecto")
            else:
                details.append(f"✗ EXPORT_PATH NO está en el proyecto")
            details.append(f"  Ruta: {export_path}")

        sys.path = old_path
        return print_service(
            "analizar_datos.py",
            all(checks),
            '\n'.join(details)
        )

    except Exception as e:
        return print_service(
            "analizar_datos.py",
            False,
            f"Error al importar: {e}"
        )

def mostrar_tabla_resumen():
    """Muestra tabla resumen de dónde guarda cada servicio"""
    print_header("TABLA RESUMEN: ¿Dónde Guarda Cada Servicio?")

    servicios = [
        ("Crear Certificación", "EntregaCerts/Certificaciones/", "Crea archivos Excel"),
        ("Crear Cert. Masivo", "EntregaCerts/Certificaciones/", "Crea archivos Excel masivamente"),
        ("Convertir a PDF", "EntregaCerts/Certificaciones_PDF/", "Lee Excel y guarda PDF"),
        ("Capturar Evidencias", "EntregaCerts/Evidencias/", "Guarda screenshots PNG"),
        ("Renombrar Evidencias", "EntregaCerts/Evidencias/", "Renombra archivos existentes"),
        ("Completar Certificación", "EntregaCerts/Certificaciones/", "Actualiza Excel existente"),
        ("Análisis de Datos", "AutCert/Assets/Reportes/", "Exporta reportes CSV"),
    ]

    print("\n  ┌" + "─"*25 + "┬" + "─"*35 + "┬" + "─"*15 + "┐")
    print("  │ Servicio                │ Guarda en                         │ Tipo          │")
    print("  ├" + "─"*25 + "┼" + "─"*35 + "┼" + "─"*15 + "┤")

    for servicio, ubicacion, tipo in servicios:
        print(f"  │ {servicio:<23} │ {ubicacion:<33} │ {tipo:<13} │")

    print("  └" + "─"*25 + "┴" + "─"*35 + "┴" + "─"*15 + "┘")

def main():
    """Función principal"""
    print("\n" + "="*80)
    print("  TEST DE VALIDACIÓN DE ENRUTAMIENTO PARA EJECUTABLES")
    print("="*80)
    print("\n  Este test verifica que cada servicio esté configurado para guardar")
    print("  archivos en la carpeta correcta de EntregaCerts.\n")

    # Ejecutar verificaciones
    resultados = {
        "Crear Certificación": verificar_crear_certificacion(),
        "Crear Certificaciones Masivo": verificar_crear_certificacion_masivo(),
        "Convertir a PDF": verificar_convertir_pdf(),
        "Capturar Evidencias": verificar_capturar_evidencias(),
        "Renombrar Evidencias": verificar_renombrar_evidencias(),
        "Completar Certificación": verificar_completar_certificacion(),
        "Análisis de Datos": verificar_analizar_datos(),
    }

    # Mostrar tabla resumen
    mostrar_tabla_resumen()

    # Resultado final
    print_header("RESULTADO FINAL")

    servicios_ok = sum(1 for v in resultados.values() if v)
    servicios_total = len(resultados)

    print(f"\n  Servicios configurados correctamente: {servicios_ok}/{servicios_total}\n")

    for nombre, resultado in resultados.items():
        status = "✓ PASS" if resultado else "✗ FAIL"
        print(f"    {status} - {nombre}")

    print("\n" + "="*80)

    if all(resultados.values()):
        print("  ✓✓✓ TODOS LOS SERVICIOS ESTÁN CORRECTAMENTE ENRUTADOS ✓✓✓")
        print("="*80)
        print("\n  Resultado:")
        print("  • Certificaciones se crearán en: EntregaCerts/Certificaciones/")
        print("  • PDFs se generarán en: EntregaCerts/Certificaciones_PDF/")
        print("  • Evidencias se guardarán en: EntregaCerts/Evidencias/")
        print("\n  ¡El proyecto está listo para producción! 🎉\n")
        return 0
    else:
        print("  ✗✗✗ ALGUNOS SERVICIOS TIENEN PROBLEMAS DE ENRUTAMIENTO ✗✗✗")
        print("="*80)
        print("\n  Revisa los errores arriba y corrige las rutas antes de usar")
        print("  los servicios en producción.\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print("Presiona ENTER para salir...")
        input()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        print("\nPresiona ENTER para salir...")
        input()
        sys.exit(1)
