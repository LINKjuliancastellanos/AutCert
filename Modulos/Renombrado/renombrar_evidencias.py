"""
RENOMBRAR EVIDENCIAS - AutCert
================================
Renombra todas las evidencias capturadas según el título del Test Case en data.csv

Estructura actual:   Evidencias/{Categoria}/HU{id}/CP{tc_id}/TC{tc_id}_History_{timestamp}.{ext}
Estructura renombrada: Evidencias/{Categoria}/HU{id}/CP{tc_id}/{Title}.{ext}

Soporta imágenes (.png, .jpg, .jpeg, .gif, .bmp) y videos (.mp4, .avi, .mov, .mkv, .webm)
Si hay múltiples evidencias del mismo TC, se agregan sufijos: {Title}_1.ext, {Title}_2.ext, etc.

Uso: py renombrar_evidencias.py
"""

import sys
import os
import csv
import re
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener la raíz del proyecto AutCert (2 niveles arriba: Renombrado -> Modulos -> AutCert)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import CSV_PATH_STR, EVIDENCIAS_ROOT_STR, LOG_RENOMBRADO_STR

CSV_PATH = CSV_PATH_STR
EVIDENCIAS_ROOT = EVIDENCIAS_ROOT_STR
LOG_PATH = LOG_RENOMBRADO_STR

# Extensiones de archivos soportados para renombrado
EXTENSIONES_IMAGEN = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
EXTENSIONES_VIDEO = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
EXTENSIONES_SOPORTADAS = EXTENSIONES_IMAGEN | EXTENSIONES_VIDEO

def log_mensaje(mensaje, archivo=True, consola=True):
    """Registra mensaje en log y/o consola"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}"

    if consola:
        print(mensaje)

    if archivo:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(linea + '\n')

def limpiar_nombre_archivo(titulo):
    """
    Limpia el título para usarlo como nombre de archivo
    - Elimina caracteres no permitidos en Windows: < > : " / \ | ? *
    - Reemplaza espacios múltiples por uno solo
    - Trunca a 200 caracteres para evitar errores de ruta larga
    """
    # Caracteres no permitidos en Windows
    caracteres_invalidos = r'[<>:"/\\|?*]'

    # Reemplazar caracteres inválidos por guión bajo
    titulo_limpio = re.sub(caracteres_invalidos, '_', titulo)

    # Reemplazar espacios múltiples por uno solo
    titulo_limpio = re.sub(r'\s+', ' ', titulo_limpio)

    # Eliminar espacios al inicio y final
    titulo_limpio = titulo_limpio.strip()

    # Truncar si es muy largo (máx 200 caracteres)
    if len(titulo_limpio) > 200:
        titulo_limpio = titulo_limpio[:200]

    return titulo_limpio

def cargar_titulos_test_cases():
    """
    Carga un diccionario {TC_ID: Title} desde data.csv
    Solo para Test Cases
    """
    titulos = {}

    if not os.path.exists(CSV_PATH):
        log_mensaje(f"✗ No se encontró el CSV: {CSV_PATH}")
        return titulos

    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                work_type = row.get('Work Item Type', '')

                if work_type == 'Test Case':
                    tc_id = row.get('ID', '').strip()
                    titulo = row.get('Title', '').strip()

                    if tc_id and titulo:
                        titulos[tc_id] = titulo

        log_mensaje(f"✓ Cargados títulos de {len(titulos)} Test Cases desde CSV")
        return titulos

    except Exception as e:
        log_mensaje(f"✗ Error al leer CSV: {e}")
        return titulos

def encontrar_archivos_evidencias():
    """
    Escanea la carpeta Evidencias/ y encuentra todos los archivos de evidencia
    (imágenes y videos) soportados.
    Retorna lista de tuplas: (ruta_completa, tc_id, carpeta_padre)
    """
    archivos = []

    if not os.path.exists(EVIDENCIAS_ROOT):
        log_mensaje(f"✗ No existe la carpeta: {EVIDENCIAS_ROOT}")
        return archivos

    # Patrón para detectar carpetas CP{tc_id}
    patron_carpeta_cp = re.compile(r'CP(\d+)$')

    # Contadores por tipo
    imagenes_encontradas = 0
    videos_encontrados = 0

    # Recorrer toda la estructura de Evidencias/
    for root, dirs, files in os.walk(EVIDENCIAS_ROOT):
        # Verificar si estamos en una carpeta CP{tc_id}
        carpeta_nombre = os.path.basename(root)
        match = patron_carpeta_cp.match(carpeta_nombre)

        if match:
            tc_id = match.group(1)

            # Buscar archivos de evidencia (imágenes y videos) en esta carpeta
            for file in files:
                extension = os.path.splitext(file)[1].lower()
                if extension in EXTENSIONES_SOPORTADAS:
                    ruta_completa = os.path.join(root, file)
                    archivos.append((ruta_completa, tc_id, root))

                    # Contar por tipo
                    if extension in EXTENSIONES_IMAGEN:
                        imagenes_encontradas += 1
                    elif extension in EXTENSIONES_VIDEO:
                        videos_encontrados += 1

    log_mensaje(f"✓ Encontrados {len(archivos)} archivos de evidencia ({imagenes_encontradas} imágenes, {videos_encontrados} videos)")
    return archivos

def renombrar_evidencia(ruta_actual, tc_id, carpeta_padre, titulos):
    """
    Renombra un archivo de evidencia según el título del TC
    Preserva la extensión original del archivo (soporta imágenes y videos)
    Retorna: (exito, mensaje)
    """
    # Verificar si existe el título para este TC
    if tc_id not in titulos:
        return (False, f"TC {tc_id} no encontrado en CSV")

    titulo_original = titulos[tc_id]
    titulo_limpio = limpiar_nombre_archivo(titulo_original)

    # Obtener la extensión original del archivo
    nombre_actual = os.path.basename(ruta_actual)
    extension_original = os.path.splitext(nombre_actual)[1].lower()

    # Construir nuevo nombre preservando la extensión original
    nuevo_nombre = f"{titulo_limpio}{extension_original}"
    nueva_ruta = os.path.join(carpeta_padre, nuevo_nombre)

    # Verificar si ya existe un archivo con ese nombre
    if os.path.exists(nueva_ruta):
        # Si es el mismo archivo, no hacer nada
        if os.path.samefile(ruta_actual, nueva_ruta):
            return (True, "Ya renombrado")
        else:
            # Existe otro archivo con el mismo nombre
            # Agregar sufijo numérico (_1, _2, etc.)
            contador = 1
            while os.path.exists(nueva_ruta):
                nuevo_nombre = f"{titulo_limpio}_{contador}{extension_original}"
                nueva_ruta = os.path.join(carpeta_padre, nuevo_nombre)
                contador += 1

    # Renombrar archivo
    try:
        os.rename(ruta_actual, nueva_ruta)
        return (True, f"Renombrado a: {nuevo_nombre}")
    except Exception as e:
        return (False, f"Error al renombrar: {e}")

def generar_reporte_previo(archivos, titulos):
    """
    Genera un reporte de lo que se va a renombrar antes de ejecutar
    Considera imágenes y videos con sus extensiones originales
    """
    print("\n" + "="*80)
    print("VISTA PREVIA DE RENOMBRADO")
    print("="*80)

    total_renombrar = 0
    total_sin_titulo = 0
    total_ya_renombrados = 0
    imagenes_renombrar = 0
    videos_renombrar = 0

    # Agrupar archivos por TC para predecir sufijos numéricos
    archivos_por_tc = {}
    for ruta_actual, tc_id, carpeta_padre in archivos:
        if tc_id not in archivos_por_tc:
            archivos_por_tc[tc_id] = []
        archivos_por_tc[tc_id].append((ruta_actual, carpeta_padre))

    for ruta_actual, tc_id, carpeta_padre in archivos:
        nombre_actual = os.path.basename(ruta_actual)
        extension_original = os.path.splitext(nombre_actual)[1].lower()

        if tc_id in titulos:
            titulo_limpio = limpiar_nombre_archivo(titulos[tc_id])
            nuevo_nombre_base = f"{titulo_limpio}{extension_original}"

            # Verificar si ya tiene el nombre correcto (considerando posibles sufijos)
            nombre_sin_ext = os.path.splitext(nombre_actual)[0]
            if nombre_sin_ext == titulo_limpio or nombre_sin_ext.startswith(f"{titulo_limpio}_"):
                total_ya_renombrados += 1
            else:
                total_renombrar += 1

                # Contar por tipo
                if extension_original in EXTENSIONES_IMAGEN:
                    imagenes_renombrar += 1
                elif extension_original in EXTENSIONES_VIDEO:
                    videos_renombrar += 1

                if total_renombrar <= 10:  # Mostrar solo los primeros 10
                    tipo = "IMG" if extension_original in EXTENSIONES_IMAGEN else "VID"
                    print(f"\n[{tipo}] TC {tc_id}:")
                    print(f"  Actual: {nombre_actual}")
                    print(f"  Nuevo:  {nuevo_nombre_base}")
        else:
            total_sin_titulo += 1

    if total_renombrar > 10:
        print(f"\n... y {total_renombrar - 10} más")

    print("\n" + "="*80)
    print("RESUMEN:")
    print("="*80)
    print(f"  Total archivos encontrados: {len(archivos)}")
    print(f"  ✓ A renombrar: {total_renombrar}")
    print(f"      - Imágenes: {imagenes_renombrar}")
    print(f"      - Videos: {videos_renombrar}")
    print(f"  ⚠ Sin título en CSV: {total_sin_titulo}")
    print(f"  ℹ Ya renombrados correctamente: {total_ya_renombrados}")

    if total_sin_titulo > 0:
        print(f"\n⚠️  Advertencia: {total_sin_titulo} archivos no tienen título en el CSV")
        print("   Estos archivos NO serán renombrados")

    return total_renombrar

def main():
    print("="*80)
    print("RENOMBRAR EVIDENCIAS - AutCert")
    print("="*80)
    print()

    # Limpiar log anterior
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje("INICIO DE RENOMBRADO", archivo=True, consola=False)
    log_mensaje("="*80, archivo=True, consola=False)

    # Paso 1: Cargar títulos desde CSV
    print("📋 Paso 1/4: Cargando títulos desde CSV...")
    titulos = cargar_titulos_test_cases()

    if not titulos:
        print("✗ No se pudieron cargar los títulos. Abortando.")
        return

    # Paso 2: Encontrar archivos de evidencias
    print("\n📂 Paso 2/4: Escaneando carpeta de Evidencias...")
    archivos = encontrar_archivos_evidencias()

    if not archivos:
        print("✗ No se encontraron archivos de evidencia. Abortando.")
        return

    # Paso 3: Generar vista previa
    print("\n📊 Paso 3/4: Generando vista previa...")
    total_renombrar = generar_reporte_previo(archivos, titulos)

    if total_renombrar == 0:
        print("\n✓ Todos los archivos ya están correctamente renombrados.")
        print("\nPresiona ENTER para salir...")
        input()
        return

    # Paso 4: Confirmar y ejecutar
    print("\n" + "="*80)
    respuesta = input("¿Proceder con el renombrado? (s/n): ").strip().lower()

    if respuesta != 's':
        print("Cancelado.")
        return

    print("\n🔄 Paso 4/4: Renombrando archivos...")
    print("="*80)

    exitosos = 0
    fallidos = 0
    ya_renombrados = 0

    for i, (ruta_actual, tc_id, carpeta_padre) in enumerate(archivos, 1):
        nombre_actual = os.path.basename(ruta_actual)

        exito, mensaje = renombrar_evidencia(ruta_actual, tc_id, carpeta_padre, titulos)

        if exito:
            if mensaje == "Ya renombrado":
                ya_renombrados += 1
                log_mensaje(f"[{i}/{len(archivos)}] TC {tc_id}: {mensaje}", archivo=True, consola=False)
            else:
                exitosos += 1
                print(f"[{i}/{len(archivos)}] ✓ TC {tc_id}: {mensaje}")
                log_mensaje(f"[{i}/{len(archivos)}] ✓ TC {tc_id}: {mensaje}", archivo=True, consola=False)
        else:
            fallidos += 1
            print(f"[{i}/{len(archivos)}] ✗ TC {tc_id}: {mensaje}")
            log_mensaje(f"[{i}/{len(archivos)}] ✗ TC {tc_id}: {mensaje}", archivo=True, consola=False)

    print("\n" + "="*80)
    print("RENOMBRADO COMPLETADO")
    print("="*80)
    print(f"\nResultados:")
    print(f"  ✓ Renombrados exitosamente: {exitosos}")
    print(f"  ✗ Fallidos: {fallidos}")
    print(f"  ℹ Ya estaban correctos: {ya_renombrados}")
    print(f"  Total procesados: {len(archivos)}")

    print(f"\n📄 Log detallado guardado en:")
    print(f"  {LOG_PATH}")

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje("FIN DE RENOMBRADO", archivo=True, consola=False)
    log_mensaje("="*80, archivo=True, consola=False)

    print("\nPresiona ENTER para salir...")
    input()

if __name__ == "__main__":
    main()
