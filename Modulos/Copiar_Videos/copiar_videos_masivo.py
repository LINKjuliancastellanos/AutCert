"""
COPIAR VIDEOS DE EVIDENCIAS MASIVO
===================================
Script para copiar videos de evidencias de MÚLTIPLES HUs desde una carpeta externa
(ej: Linktic/Asignaciones/Evidencias) hacia la estructura organizada en EntregaCerts/Evidencias.

La diferencia con la versión individual es que este script:
- Procesa TODAS las carpetas de HU que encuentre en la ruta base
- Detecta automáticamente categorías (AyN, RyC, Transversal)
- Copia todos los videos de todas las HUs en una sola operación

Funcionalidades:
- Escanea recursivamente carpetas de HU
- Detecta automáticamente HU, categoría y CPs
- Copia videos (.mp4, .avi, .mov, .mkv, .webm, etc.)
- Mantiene la estructura: EntregaCerts/Evidencias/{Categoria}/HU{id}/CP{tc_id}/
- Evita duplicados (compara tamaños)
- Genera log detallado de operaciones
- Resumen estadístico por HU y total

Uso:
    python copiar_videos_masivo.py

Ejemplo de entrada:
    C:/Users/Julian/Linktic/Asignaciones/Evidencias

Estructura esperada:
    Evidencias/
    ├── AyN/
    │   ├── Evidencias HU83509/
    │   │   ├── CP123456/
    │   │   │   └── video1.mp4
    │   │   └── CP123457/
    │   │       └── video2.mp4
    │   └── Evidencias HU83510/
    │       └── CP123458/
    │           └── video3.mp4
    ├── RyC/
    │   └── Evidencias HU83511/
    │       └── CP123459/
    │           └── video4.mp4
    └── Transversal/
        └── Evidencias HU83512/
            └── CP123460/
                └── video5.mp4

Resultado:
    EntregaCerts/Evidencias/AyN/HU83509/CP123456/video1.mp4
    EntregaCerts/Evidencias/AyN/HU83509/CP123457/video2.mp4
    EntregaCerts/Evidencias/AyN/HU83510/CP123458/video3.mp4
    EntregaCerts/Evidencias/RyC/HU83511/CP123459/video4.mp4
    EntregaCerts/Evidencias/Transversal/HU83512/CP123460/video5.mp4
"""

import sys
import os
import shutil
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener la raíz del proyecto AutCert (2 niveles arriba: Copiar_Videos -> Modulos -> AutCert)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import EVIDENCIAS_ROOT, LOGS_DIR

# Extensiones de video soportadas
EXTENSIONES_VIDEO = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}

# Log del módulo
LOG_PATH = LOGS_DIR / "copiar_videos_masivo.log"

def log_mensaje(mensaje, archivo=True, consola=True):
    """Registra mensaje en log y/o consola"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}"

    if consola:
        print(f"  {mensaje}")

    if archivo:
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(linea + '\n')
        except:
            pass  # Ignorar errores de log

def extraer_numero_hu(nombre_carpeta):
    """
    Extrae el número de HU del nombre de la carpeta.

    Ejemplos:
        "Evidencias HU83509" -> "83509"
        "HU83509" -> "83509"
        "evidencias_hu_83509" -> "83509"
    """
    # Buscar patrón HU seguido de números
    match = re.search(r'HU\s*(\d+)', nombre_carpeta, re.IGNORECASE)
    if match:
        return match.group(1)

    # Si no encuentra, buscar solo números de 5+ dígitos
    match = re.search(r'(\d{5,})', nombre_carpeta)
    if match:
        return match.group(1)

    return None

def extraer_numero_cp(nombre_carpeta):
    """
    Extrae el número de CP (Test Case) del nombre de la carpeta.

    Ejemplos:
        "CP123456" -> "123456"
        "TC123456" -> "123456"
        "cp_123456" -> "123456"
    """
    # Buscar patrón CP o TC seguido de números
    match = re.search(r'(?:CP|TC)\s*(\d+)', nombre_carpeta, re.IGNORECASE)
    if match:
        return match.group(1)

    return None

def determinar_categoria_desde_ruta(ruta):
    """
    Determina la categoría (AyN, RyC, Transversal) desde cualquier parte de la ruta.
    """
    ruta_str = str(ruta).replace('\\', '/')
    ruta_lower = ruta_str.lower()

    if '/ayn/' in ruta_lower or '\\ayn\\' in str(ruta).lower():
        return 'AyN'
    elif '/ryc/' in ruta_lower or '\\ryc\\' in str(ruta).lower():
        return 'RyC'
    elif '/transversal/' in ruta_lower or '\\transversal\\' in str(ruta).lower():
        return 'Transversal'

    return None

def escanear_carpetas_hu(carpeta_base):
    """
    Escanea recursivamente la carpeta base y encuentra todas las carpetas de HU con videos.

    Retorna: dict {
        numero_hu: {
            'categoria': str,
            'ruta_origen': Path,
            'videos_por_cp': {numero_cp: [lista de archivos]}
        }
    }
    """
    hus_encontradas = {}

    if not carpeta_base.exists():
        log_mensaje(f"ERROR: La carpeta no existe: {carpeta_base}", consola=True)
        return hus_encontradas

    # Buscar recursivamente carpetas que contengan HU en el nombre
    for item in carpeta_base.rglob('*'):
        if item.is_dir():
            numero_hu = extraer_numero_hu(item.name)

            if numero_hu and numero_hu not in hus_encontradas:
                # Intentar determinar categoría desde la ruta
                categoria = determinar_categoria_desde_ruta(item)

                # Buscar videos en carpetas CP dentro de esta HU
                videos_por_cp = {}

                for subitem in item.iterdir():
                    if subitem.is_dir():
                        numero_cp = extraer_numero_cp(subitem.name)
                        if numero_cp:
                            # Buscar videos dentro de esta carpeta CP
                            videos = []
                            for video_file in subitem.iterdir():
                                if video_file.is_file() and video_file.suffix.lower() in EXTENSIONES_VIDEO:
                                    videos.append(video_file)

                            if videos:
                                videos_por_cp[numero_cp] = videos

                # Solo agregar si tiene videos
                if videos_por_cp:
                    hus_encontradas[numero_hu] = {
                        'categoria': categoria,
                        'ruta_origen': item,
                        'videos_por_cp': videos_por_cp
                    }

    return hus_encontradas

def copiar_video(origen, destino):
    """
    Copia un video desde origen a destino.

    Retorna: (exito, mensaje)
    """
    try:
        # Crear directorio destino si no existe
        destino.parent.mkdir(parents=True, exist_ok=True)

        # Verificar si ya existe
        if destino.exists():
            # Comparar tamaños
            if origen.stat().st_size == destino.stat().st_size:
                return (True, "Ya existe")
            else:
                # Sobrescribir si es diferente
                shutil.copy2(origen, destino)
                return (True, "Sobrescrito")
        else:
            # Copiar archivo
            shutil.copy2(origen, destino)
            return (True, "Copiado")

    except Exception as e:
        return (False, f"Error: {e}")

def formatear_tamaño(bytes):
    """Formatea tamaño en bytes a formato legible"""
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unidad}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

def preguntar_categoria(numero_hu):
    """Pregunta al usuario por la categoría de una HU"""
    print(f"\n  No se pudo detectar la categoría para HU{numero_hu}")
    print("\n  Opciones:")
    print("    1. AyN (Afiliaciones y Novedades)")
    print("    2. RyC (Recaudo y Cartera)")
    print("    3. Transversal")
    print("    S. Saltar esta HU")

    while True:
        opcion = input(f"\n  Categoría para HU{numero_hu} (1/2/3/S): ").strip().upper()

        if opcion == '1':
            return 'AyN'
        elif opcion == '2':
            return 'RyC'
        elif opcion == '3':
            return 'Transversal'
        elif opcion == 'S':
            return None
        else:
            print("  ERROR: Opción inválida. Usa 1, 2, 3 o S")

def main():
    print("\n" + "="*80)
    print("  COPIAR VIDEOS DE EVIDENCIAS MASIVO")
    print("="*80)
    print()

    # Limpiar log anterior
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje("INICIO DE COPIA MASIVA DE VIDEOS", archivo=True, consola=False)
    log_mensaje("="*80, archivo=True, consola=False)

    # Paso 1: Solicitar carpeta base
    print("[1/5] Ubicación base de evidencias")
    print("-" * 80)
    print("\n  Ingresa la ruta de la carpeta base que contiene múltiples HUs.")
    print("  Ejemplo: C:\\Users\\Julian\\Linktic\\Asignaciones\\Evidencias")
    print()
    print("  El script buscará automáticamente todas las carpetas de HU")
    print("  dentro de esta ubicación y sus subcarpetas.")
    print()

    ruta_input = input("  Ruta de la carpeta base: ").strip()

    # Limpiar comillas si las tiene
    ruta_input = ruta_input.strip('"').strip("'")

    carpeta_base = Path(ruta_input)

    if not carpeta_base.exists():
        print(f"\n  ERROR: La carpeta no existe:")
        print(f"  {carpeta_base}")
        log_mensaje(f"ERROR: Carpeta no existe: {carpeta_base}")
        input("\nPresiona ENTER para salir...")
        return

    print(f"\n  Carpeta base: {carpeta_base}")
    log_mensaje(f"Carpeta base: {carpeta_base}")

    # Paso 2: Escanear todas las HUs
    print("\n[2/5] Escaneando carpetas de HU...")
    print("-" * 80)
    print("\n  Buscando carpetas de HU con videos...")

    hus_encontradas = escanear_carpetas_hu(carpeta_base)

    if not hus_encontradas:
        print("\n  No se encontraron carpetas de HU con videos en la estructura.")
        print("\n  Estructura esperada:")
        print("    Evidencias/")
        print("      └── AyN/ (o RyC/ o Transversal/)")
        print("          └── Evidencias HU83509/")
        print("              └── CP123456/")
        print("                  └── video.mp4")
        log_mensaje("ERROR: No se encontraron HUs con videos")
        input("\nPresiona ENTER para salir...")
        return

    print(f"\n  HUs encontradas: {len(hus_encontradas)}")

    # Paso 3: Verificar y asignar categorías
    print("\n[3/5] Verificando categorías")
    print("-" * 80)

    hus_sin_categoria = []
    for numero_hu, datos in hus_encontradas.items():
        if datos['categoria'] is None:
            hus_sin_categoria.append(numero_hu)

    if hus_sin_categoria:
        print(f"\n  Se encontraron {len(hus_sin_categoria)} HUs sin categoría detectada.")
        print("  Por favor, asigna la categoría manualmente:")

        for numero_hu in hus_sin_categoria:
            categoria = preguntar_categoria(numero_hu)
            if categoria:
                hus_encontradas[numero_hu]['categoria'] = categoria
                log_mensaje(f"HU{numero_hu}: Categoría asignada manualmente -> {categoria}", consola=False)
            else:
                # Marcar para eliminar
                del hus_encontradas[numero_hu]
                log_mensaje(f"HU{numero_hu}: Saltada por el usuario", consola=False)

    # Verificar que aún hay HUs para procesar
    if not hus_encontradas:
        print("\n  No hay HUs para procesar.")
        log_mensaje("No hay HUs para procesar")
        input("\nPresiona ENTER para salir...")
        return

    # Paso 4: Mostrar resumen
    print("\n[4/5] Resumen de videos encontrados")
    print("-" * 80)

    # Calcular estadísticas por categoría
    stats_por_categoria = defaultdict(lambda: {'hus': 0, 'cps': 0, 'videos': 0, 'tamaño': 0})

    for numero_hu, datos in hus_encontradas.items():
        categoria = datos['categoria']
        videos_por_cp = datos['videos_por_cp']

        stats_por_categoria[categoria]['hus'] += 1
        stats_por_categoria[categoria]['cps'] += len(videos_por_cp)

        for videos in videos_por_cp.values():
            stats_por_categoria[categoria]['videos'] += len(videos)
            stats_por_categoria[categoria]['tamaño'] += sum(v.stat().st_size for v in videos)

    # Mostrar por categoría
    for categoria in sorted(stats_por_categoria.keys()):
        stats = stats_por_categoria[categoria]
        print(f"\n  {categoria}:")
        print(f"    HUs:    {stats['hus']}")
        print(f"    CPs:    {stats['cps']}")
        print(f"    Videos: {stats['videos']}")
        print(f"    Tamaño: {formatear_tamaño(stats['tamaño'])}")

    # Totales
    total_hus = sum(s['hus'] for s in stats_por_categoria.values())
    total_cps = sum(s['cps'] for s in stats_por_categoria.values())
    total_videos = sum(s['videos'] for s in stats_por_categoria.values())
    total_tamaño = sum(s['tamaño'] for s in stats_por_categoria.values())

    print(f"\n  TOTAL:")
    print(f"    HUs:    {total_hus}")
    print(f"    CPs:    {total_cps}")
    print(f"    Videos: {total_videos}")
    print(f"    Tamaño: {formatear_tamaño(total_tamaño)}")

    print(f"\n  Carpeta de destino base:")
    print(f"    {EVIDENCIAS_ROOT}")

    log_mensaje(f"Total: {total_hus} HUs, {total_cps} CPs, {total_videos} videos, {formatear_tamaño(total_tamaño)}")

    # Paso 5: Confirmar y copiar
    print("\n[5/5] Confirmación")
    print("-" * 80)

    confirmar = input("\n  ¿Proceder con la copia masiva? (S/N): ").strip().upper()

    if confirmar != 'S':
        print("\n  Operación cancelada.")
        log_mensaje("Operación cancelada por el usuario")
        input("\nPresiona ENTER para salir...")
        return

    # Copiar videos
    print("\n" + "="*80)
    print("  COPIANDO VIDEOS...")
    print("="*80)

    # Estadísticas globales
    stats_globales = {
        'copiados': 0,
        'ya_existian': 0,
        'sobrescritos': 0,
        'errores': 0
    }

    # Procesar cada HU
    for numero_hu, datos in sorted(hus_encontradas.items()):
        categoria = datos['categoria']
        videos_por_cp = datos['videos_por_cp']

        print(f"\n  HU{numero_hu} ({categoria}):")
        log_mensaje(f"Procesando HU{numero_hu} ({categoria})", consola=False)

        carpeta_destino_hu = EVIDENCIAS_ROOT / categoria / f"HU{numero_hu}"

        # Procesar cada CP
        for cp, videos in sorted(videos_por_cp.items()):
            carpeta_cp_destino = carpeta_destino_hu / f"CP{cp}"

            print(f"    CP{cp} ({len(videos)} video(s)): ", end="")
            log_mensaje(f"  CP{cp}: {len(videos)} videos", consola=False)

            resultados_cp = {'copiados': 0, 'existian': 0, 'sobrescritos': 0, 'errores': 0}

            for video in videos:
                destino = carpeta_cp_destino / video.name
                exito, mensaje = copiar_video(video, destino)

                if exito:
                    if "Ya existe" in mensaje:
                        resultados_cp['existian'] += 1
                        stats_globales['ya_existian'] += 1
                    elif "Sobrescrito" in mensaje:
                        resultados_cp['sobrescritos'] += 1
                        stats_globales['sobrescritos'] += 1
                    else:
                        resultados_cp['copiados'] += 1
                        stats_globales['copiados'] += 1
                    log_mensaje(f"    {video.name}: {mensaje}", consola=False)
                else:
                    resultados_cp['errores'] += 1
                    stats_globales['errores'] += 1
                    log_mensaje(f"    {video.name}: {mensaje}", consola=False)

            # Resumen del CP
            resumen_parts = []
            if resultados_cp['copiados'] > 0:
                resumen_parts.append(f"{resultados_cp['copiados']} copiados")
            if resultados_cp['existian'] > 0:
                resumen_parts.append(f"{resultados_cp['existian']} existían")
            if resultados_cp['sobrescritos'] > 0:
                resumen_parts.append(f"{resultados_cp['sobrescritos']} sobrescritos")
            if resultados_cp['errores'] > 0:
                resumen_parts.append(f"{resultados_cp['errores']} errores")

            print(", ".join(resumen_parts))

    # Resumen final
    print("\n" + "="*80)
    print("  COPIA MASIVA COMPLETADA")
    print("="*80)

    print(f"\n  Resultados totales:")
    print(f"    Copiados nuevos:  {stats_globales['copiados']}")
    print(f"    Ya existían:      {stats_globales['ya_existian']}")
    print(f"    Sobrescritos:     {stats_globales['sobrescritos']}")
    print(f"    Errores:          {stats_globales['errores']}")
    print(f"    Total procesados: {total_videos}")

    print(f"\n  Estadísticas por categoría:")
    for categoria in sorted(stats_por_categoria.keys()):
        stats = stats_por_categoria[categoria]
        print(f"    {categoria}: {stats['videos']} videos en {stats['hus']} HUs")

    print(f"\n  Ubicación final:")
    print(f"    {EVIDENCIAS_ROOT}")

    print(f"\n  Log guardado en:")
    print(f"    {LOG_PATH}")

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje(f"RESUMEN: {stats_globales['copiados']} copiados, {stats_globales['ya_existian']} existían, {stats_globales['sobrescritos']} sobrescritos, {stats_globales['errores']} errores", archivo=True, consola=False)
    log_mensaje(f"Procesadas: {total_hus} HUs con {total_videos} videos", archivo=True, consola=False)
    log_mensaje("FIN DE COPIA MASIVA DE VIDEOS", archivo=True, consola=False)
    log_mensaje("="*80, archivo=True, consola=False)

    print("\n" + "="*80)
    input("\nPresiona ENTER para salir...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Operación cancelada por el usuario.")
        log_mensaje("Operación cancelada por interrupción de teclado")
        input("\nPresiona ENTER para salir...")
    except Exception as e:
        print(f"\n  ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        log_mensaje(f"ERROR INESPERADO: {e}")
        input("\nPresiona ENTER para salir...")
