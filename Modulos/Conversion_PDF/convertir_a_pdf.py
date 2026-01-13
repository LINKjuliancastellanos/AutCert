"""
CONVERTIR CERTIFICACIONES A PDF - AutCert
==========================================
Convierte certificaciones Excel (.xlsx) a PDF manteniendo el nombre original.

Estructura:
  Entrada:  Certificaciones/{Categoria}/Cert_HU{id}.xlsx
  Salida:   Certificaciones_PDF/{Categoria}/Cert_HU{id}.pdf

Uso: py convertir_a_pdf.py
"""

import sys
import os
import win32com.client
import pythoncom
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener la raíz del proyecto AutCert (2 niveles arriba: Conversion_PDF -> Modulos -> AutCert)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import CERTIFICACIONES_ROOT_STR, PDF_ROOT_STR, LOG_CONVERSION_PDF_STR

CERTIFICACIONES_ROOT = CERTIFICACIONES_ROOT_STR
PDF_ROOT = PDF_ROOT_STR
LOG_PATH = LOG_CONVERSION_PDF_STR

def log_mensaje(mensaje, archivo=True, consola=True):
    """Registra mensaje en log y/o consola"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}"

    if consola:
        print(mensaje)

    if archivo:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(linea + '\n')

def encontrar_archivos_excel():
    """
    Escanea carpeta Certificaciones/ y encuentra todos los .xlsx
    Retorna lista de tuplas: (ruta_completa, ruta_relativa, categoria)
    """
    archivos = []

    if not os.path.exists(CERTIFICACIONES_ROOT):
        log_mensaje(f"✗ No existe la carpeta: {CERTIFICACIONES_ROOT}")
        return archivos

    # Recorrer toda la estructura de Certificaciones/
    for root, dirs, files in os.walk(CERTIFICACIONES_ROOT):
        for file in files:
            if file.lower().endswith('.xlsx') and not file.startswith('~$'):
                ruta_completa = os.path.join(root, file)

                # Obtener categoría (subcarpeta directa de Certificaciones/)
                ruta_relativa = os.path.relpath(root, CERTIFICACIONES_ROOT)
                categoria = ruta_relativa.split(os.sep)[0] if os.sep in ruta_relativa or ruta_relativa != '.' else 'Otros'

                archivos.append((ruta_completa, ruta_relativa, categoria, file))

    log_mensaje(f"✓ Encontrados {len(archivos)} archivos Excel")
    return archivos

def encontrar_ultima_fila_con_contenido(sheet, max_col=11):
    """
    Encuentra la última fila que realmente tiene contenido.
    Busca desde abajo hacia arriba para ser eficiente.
    """
    # Usar el método Find de Excel para buscar la última celda con datos
    # Buscar hacia arriba desde la última celda
    try:
        # xlFindLookIn: 1 = xlFormulas, busca en fórmulas y valores
        # xlSearchOrder: 1 = xlByRows
        # xlSearchDirection: 2 = xlPrevious (hacia atrás/arriba)
        ultima_celda = sheet.Cells.Find(
            What="*",
            After=sheet.Cells(1, 1),
            LookIn=-4163,  # xlValues
            LookAt=2,      # xlPart
            SearchOrder=1,  # xlByRows
            SearchDirection=2  # xlPrevious
        )
        if ultima_celda:
            return ultima_celda.Row
    except:
        pass

    # Fallback: buscar manualmente
    used_range = sheet.UsedRange
    ultima_fila = 1

    for row in range(used_range.Rows.Count, 0, -1):
        fila_real = used_range.Row + row - 1
        for col in range(1, min(max_col + 1, used_range.Columns.Count + 1)):
            celda = sheet.Cells(fila_real, col)
            if celda.Value is not None and str(celda.Value).strip() != "":
                return fila_real

    return ultima_fila


def encontrar_ultima_columna_con_contenido(sheet):
    """
    Encuentra la última columna que realmente tiene contenido.
    """
    try:
        ultima_celda = sheet.Cells.Find(
            What="*",
            After=sheet.Cells(1, 1),
            LookIn=-4163,  # xlValues
            LookAt=2,      # xlPart
            SearchOrder=2,  # xlByColumns
            SearchDirection=2  # xlPrevious
        )
        if ultima_celda:
            return ultima_celda.Column
    except:
        pass

    return sheet.UsedRange.Columns.Count


def convertir_excel_a_pdf(ruta_excel, ruta_pdf):
    """
    Convierte un archivo Excel a PDF usando COM de Excel
    Configuración optimizada:
    - Orientación vertical (portrait)
    - Todas las columnas ajustadas al ancho de una página (FitToPagesWide)
    - Solo incluye filas con contenido real (elimina filas vacías)
    - Mínima cantidad de hojas posible
    - Márgenes reducidos para maximizar contenido
    - Centrado horizontal

    Retorna: (exito, mensaje)
    """
    import tempfile
    import shutil

    temp_dir = None

    try:
        # Eliminar PDF existente si hay
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)

        # Crear copia temporal del Excel (para no modificar el original)
        temp_dir = tempfile.mkdtemp()
        temp_excel = os.path.join(temp_dir, os.path.basename(ruta_excel))
        shutil.copy2(ruta_excel, temp_excel)

        # Inicializar COM para el thread actual
        pythoncom.CoInitialize()

        # Crear instancia de Excel
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        try:
            # Abrir copia temporal
            workbook = excel.Workbooks.Open(temp_excel)

            # Procesar cada hoja
            for sheet in workbook.Worksheets:
                # Encontrar última fila con contenido real
                ultima_celda = sheet.Cells.Find(
                    What="*",
                    After=sheet.Cells(1, 1),
                    LookIn=-4163,  # xlValues
                    LookAt=2,      # xlPart
                    SearchOrder=1,  # xlByRows
                    SearchDirection=2  # xlPrevious
                )
                ultima_fila = ultima_celda.Row if ultima_celda else 1

                # Encontrar última fila del UsedRange
                used_range = sheet.UsedRange
                ultima_fila_used = used_range.Row + used_range.Rows.Count - 1

                # Eliminar filas vacías (desde ultima_fila+1 hasta el final)
                if ultima_fila_used > ultima_fila:
                    rango_eliminar = sheet.Range(
                        sheet.Rows(ultima_fila + 1),
                        sheet.Rows(ultima_fila_used)
                    )
                    rango_eliminar.Delete()

            # Guardar cambios (filas eliminadas)
            workbook.Save()

            # Configurar página para cada hoja
            for sheet in workbook.Worksheets:
                page_setup = sheet.PageSetup

                # Orientación vertical
                page_setup.Orientation = 1  # xlPortrait
                page_setup.PaperSize = 1    # xlPaperLetter

                # Ajustar todas las columnas a 1 página de ancho
                page_setup.Zoom = False
                page_setup.FitToPagesWide = 1
                page_setup.FitToPagesTall = False

                # Márgenes reducidos
                page_setup.LeftMargin = excel.InchesToPoints(0.25)
                page_setup.RightMargin = excel.InchesToPoints(0.25)
                page_setup.TopMargin = excel.InchesToPoints(0.5)
                page_setup.BottomMargin = excel.InchesToPoints(0.5)
                page_setup.HeaderMargin = excel.InchesToPoints(0.2)
                page_setup.FooterMargin = excel.InchesToPoints(0.2)

                # Centrar horizontalmente
                page_setup.CenterHorizontally = True
                page_setup.CenterVertically = False
                page_setup.PrintGridlines = False

            # Guardar configuración de página
            workbook.Save()

            # Asegurarse de que el directorio de destino existe
            os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)

            # Exportar a PDF
            workbook.ExportAsFixedFormat(
                Type=0,  # PDF
                Filename=ruta_pdf,
                Quality=0,  # Calidad estándar
                IncludeDocProperties=True,
                IgnorePrintAreas=False,
                OpenAfterPublish=False
            )

            # Cerrar sin guardar (ya guardamos antes)
            workbook.Close(SaveChanges=False)

            return (True, "Convertido exitosamente")

        finally:
            # Cerrar Excel
            excel.Quit()
            pythoncom.CoUninitialize()

    except Exception as e:
        return (False, f"Error: {e}")

    finally:
        # Limpiar directorio temporal
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

def convertir_certificacion_individual(hu_id):
    """
    Convierte una certificación específica a PDF por su ID de HU.
    Busca en todas las carpetas (AyN, RyC, Transversal).

    Retorna: (exito, mensaje, ruta_pdf)
    """
    # Buscar el archivo Excel en todas las subcarpetas
    nombre_buscado = f"Certificacion_QA_{hu_id}.xlsx"

    for root, dirs, files in os.walk(CERTIFICACIONES_ROOT):
        for file in files:
            if file == nombre_buscado:
                ruta_excel = os.path.join(root, file)

                # Obtener categoría (subcarpeta)
                ruta_relativa = os.path.relpath(root, CERTIFICACIONES_ROOT)
                categoria = ruta_relativa if ruta_relativa != '.' else ''

                # Construir ruta PDF
                nombre_pdf = f"Certificacion_QA_{hu_id}.pdf"
                if categoria:
                    carpeta_pdf = os.path.join(PDF_ROOT, categoria)
                else:
                    carpeta_pdf = PDF_ROOT

                ruta_pdf = os.path.join(carpeta_pdf, nombre_pdf)

                # Convertir
                exito, mensaje = convertir_excel_a_pdf(ruta_excel, ruta_pdf)

                if exito:
                    return (True, f"Convertido: {ruta_pdf}", ruta_pdf)
                else:
                    return (False, mensaje, None)

    return (False, f"No se encontró certificación para HU {hu_id}", None)


def main():
    print("="*80)
    print("CONVERTIR CERTIFICACIONES A PDF - AutCert")
    print("="*80)
    print()

    # Menú de opciones
    print("Opciones:")
    print("  1. Convertir TODAS las certificaciones")
    print("  2. Convertir una certificación específica (por ID de HU)")
    print()
    opcion = input("Selecciona una opción (1/2): ").strip()

    if opcion == "2":
        # Modo individual
        hu_id = input("Ingresa el ID de la HU (ej: 83488): ").strip()
        if not hu_id:
            print("ID inválido. Abortando.")
            input("\nPresiona ENTER para salir...")
            return

        print(f"\nConvirtiendo certificación HU {hu_id}...")
        exito, mensaje, ruta_pdf = convertir_certificacion_individual(hu_id)

        if exito:
            print(f"\n✓ {mensaje}")
            print(f"\n📁 PDF guardado en:")
            print(f"   {ruta_pdf}")
        else:
            print(f"\n✗ Error: {mensaje}")

        input("\nPresiona ENTER para salir...")
        return

    # Modo masivo (opción 1 o cualquier otra)
    print("\n" + "="*80)
    print("CONVERSIÓN MASIVA")
    print("="*80 + "\n")

    # Limpiar log anterior
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje("INICIO DE CONVERSIÓN A PDF", archivo=True, consola=False)
    log_mensaje("="*80, archivo=True, consola=False)

    # Paso 1: Encontrar archivos Excel
    print("📂 Paso 1/3: Escaneando carpeta de Certificaciones...")
    archivos = encontrar_archivos_excel()

    if not archivos:
        print("✗ No se encontraron archivos Excel. Abortando.")
        return

    # Paso 2: Vista previa
    print("\n📊 Paso 2/3: Vista previa de conversión...")
    print(f"\nTotal archivos a convertir: {len(archivos)}\n")

    # Agrupar por categoría
    categorias = {}
    for _, _, categoria, _ in archivos:
        categorias[categoria] = categorias.get(categoria, 0) + 1

    print("Distribución por categoría:")
    for categoria, cantidad in sorted(categorias.items()):
        print(f"  {categoria}: {cantidad} certificaciones")

    print(f"\nCarpeta destino: {PDF_ROOT}")

    # Paso 3: Confirmar y convertir
    print("\n" + "="*80)
    respuesta = input("¿Proceder con la conversión? (s/n): ").strip().lower()

    if respuesta != 's':
        print("Cancelado.")
        return

    print("\n🔄 Paso 3/3: Convirtiendo archivos...")
    print("="*80)

    exitosos = 0
    fallidos = 0

    for i, (ruta_excel, ruta_relativa, categoria, nombre_archivo) in enumerate(archivos, 1):
        nombre_base = os.path.splitext(nombre_archivo)[0]
        nombre_pdf = f"{nombre_base}.pdf"

        # Construir ruta PDF manteniendo estructura de carpetas
        if ruta_relativa == '.':
            carpeta_pdf = PDF_ROOT
        else:
            carpeta_pdf = os.path.join(PDF_ROOT, ruta_relativa)

        ruta_pdf = os.path.join(carpeta_pdf, nombre_pdf)

        print(f"[{i}/{len(archivos)}] {nombre_archivo}...", end=" ")

        exito, mensaje = convertir_excel_a_pdf(ruta_excel, ruta_pdf)

        if exito:
            exitosos += 1
            print("✓")
            log_mensaje(f"[{i}/{len(archivos)}] ✓ {nombre_archivo} → {nombre_pdf}", archivo=True, consola=False)
        else:
            fallidos += 1
            print("✗")
            print(f"    Error: {mensaje}")
            log_mensaje(f"[{i}/{len(archivos)}] ✗ {nombre_archivo}: {mensaje}", archivo=True, consola=False)

    print("\n" + "="*80)
    print("CONVERSIÓN COMPLETADA")
    print("="*80)
    print(f"\nResultados:")
    print(f"  ✓ Convertidos exitosamente: {exitosos}")
    print(f"  ✗ Fallidos: {fallidos}")
    print(f"  Total procesados: {len(archivos)}")

    print(f"\n📁 PDFs guardados en:")
    print(f"  {PDF_ROOT}")

    print(f"\n📄 Log detallado guardado en:")
    print(f"  {LOG_PATH}")

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje("FIN DE CONVERSIÓN", archivo=True, consola=False)
    log_mensaje("="*80, archivo=True, consola=False)

    print("\nPresiona ENTER para salir...")
    input()

if __name__ == "__main__":
    main()
