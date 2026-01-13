"""
COPIAR VIDEOS DE EVIDENCIAS A ENTREGACERTS
==========================================
Script para copiar videos de evidencias desde una carpeta externa
(ej: Linktic/Asignaciones/Evidencias) hacia la estructura organizada
en EntregaCerts/Evidencias.

Funcionalidades:
- Detecta automáticamente la HU desde el nombre de la carpeta
- Copia videos (.mp4, .avi, .mov, .mkv, .webm) a las carpetas CP correspondientes
- Mantiene la estructura organizada: EntregaCerts/Evidencias/{Categoria}/HU{id}/CP{tc_id}/
- Evita duplicados (no sobrescribe si ya existe)
- Genera log de operaciones

Uso:
    python copiar_videos_evidencias.py

Ejemplo de entrada:
    C:/Users/Julian/Linktic/Asignaciones/Evidencias/AyN/Evidencias HU83509

Estructura esperada:
    Evidencias HU83509/
    ├── CP123456/
    │   └── video1.mp4
    ├── CP123457/
    │   └── video2.mp4
    └── ...

Resultado:
    EntregaCerts/Evidencias/AyN/HU83509/CP123456/video1.mp4
    EntregaCerts/Evidencias/AyN/HU83509/CP123457/video2.mp4
"""

import sys
import os
import shutil
import re
from pathlib import Path
from datetime import datetime

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
LOG_PATH = LOGS_DIR / "copiar_videos.log"

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

    # Si no encuentra, buscar solo números
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

def determinar_categoria(ruta_origen):
    """
    Determina la categoría (AyN, RyC, Transversal) desde la ruta de origen.
    Busca en los componentes del path.
    """
    ruta_str = str(ruta_origen).replace('\\', '/')

    if '/AyN/' in ruta_str or '/ayn/' in ruta_str.lower():
        return 'AyN'
    elif '/RyC/' in ruta_str or '/ryc/' in ruta_str.lower():
        return 'RyC'
    elif '/Transversal/' in ruta_str or '/transversal/' in ruta_str.lower():
        return 'Transversal'

    # Si no encuentra, preguntar al usuario
    return None

def encontrar_videos_en_carpeta(carpeta_origen):
    """
    Escanea la carpeta origen y encuentra todos los videos organizados por CP.

    Retorna: dict {numero_cp: [lista de archivos de video]}
    """
    videos_por_cp = {}

    if not carpeta_origen.exists():
        log_mensaje(f"ERROR: La carpeta no existe: {carpeta_origen}", consola=True)
        return videos_por_cp

    # Buscar carpetas CP
    for item in carpeta_origen.iterdir():
        if item.is_dir():
            numero_cp = extraer_numero_cp(item.name)
            if numero_cp:
                # Buscar videos dentro de esta carpeta CP
                videos = []
                for video_file in item.iterdir():
                    if video_file.is_file() and video_file.suffix.lower() in EXTENSIONES_VIDEO:
                        videos.append(video_file)

                if videos:
                    videos_por_cp[numero_cp] = videos

    return videos_por_cp

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
                return (True, "Ya existe (mismo tamaño)")
            else:
                # Sobrescribir si es diferente
                shutil.copy2(origen, destino)
                return (True, "Sobrescrito (tamaño diferente)")
        else:
            # Copiar archivo
            shutil.copy2(origen, destino)
            return (True, "Copiado exitosamente")

    except Exception as e:
        return (False, f"Error: {e}")

def formatear_tamaño(bytes):
    """Formatea tamaño en bytes a formato legible"""
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unidad}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

def main():
    print("\n" + "="*80)
    print("  COPIAR VIDEOS DE EVIDENCIAS A ENTREGACERTS")
    print("="*80)
    print()

    # Limpiar log anterior
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje("INICIO DE COPIA DE VIDEOS", archivo=True, consola=False)
    log_mensaje("="*80, archivo=True, consola=False)

    # Paso 1: Solicitar carpeta origen
    print("[1/5] Ubicación de los videos")
    print("-" * 80)
    print("\n  Ingresa la ruta completa de la carpeta con los videos.")
    print("  Ejemplo: C:\\Users\\Julian\\Linktic\\Evidencias\\AyN\\Evidencias HU83509")
    print()

    ruta_input = input("  Ruta de la carpeta: ").strip()

    # Limpiar comillas si las tiene
    ruta_input = ruta_input.strip('"').strip("'")

    carpeta_origen = Path(ruta_input)

    if not carpeta_origen.exists():
        print(f"\n  ERROR: La carpeta no existe:")
        print(f"  {carpeta_origen}")
        log_mensaje(f"ERROR: Carpeta no existe: {carpeta_origen}")
        input("\nPresiona ENTER para salir...")
        return

    print(f"\n  Carpeta de origen: {carpeta_origen}")
    log_mensaje(f"Carpeta de origen: {carpeta_origen}")

    # Paso 2: Extraer número de HU
    print("\n[2/5] Identificación de Historia de Usuario")
    print("-" * 80)

    numero_hu = extraer_numero_hu(carpeta_origen.name)

    if not numero_hu:
        print(f"\n  No se pudo detectar automáticamente el número de HU.")
        print(f"  Nombre de carpeta: {carpeta_origen.name}")
        numero_hu = input("\n  Ingresa el número de HU manualmente (ej: 83509): ").strip()

        if not numero_hu.isdigit():
            print("\n  ERROR: El número de HU debe ser numérico")
            log_mensaje(f"ERROR: HU inválida: {numero_hu}")
            input("\nPresiona ENTER para salir...")
            return

    print(f"\n  HU detectada: {numero_hu}")
    log_mensaje(f"HU detectada: {numero_hu}")

    # Paso 3: Determinar categoría
    print("\n[3/5] Categoría del módulo")
    print("-" * 80)

    categoria = determinar_categoria(carpeta_origen)

    if not categoria:
        print("\n  No se pudo detectar automáticamente la categoría.")
        print("\n  Opciones:")
        print("    1. AyN (Afiliaciones y Novedades)")
        print("    2. RyC (Recaudo y Cartera)")
        print("    3. Transversal")

        opcion = input("\n  Selecciona la categoría (1/2/3): ").strip()

        if opcion == '1':
            categoria = 'AyN'
        elif opcion == '2':
            categoria = 'RyC'
        elif opcion == '3':
            categoria = 'Transversal'
        else:
            print("\n  ERROR: Opción inválida")
            log_mensaje(f"ERROR: Categoría inválida: {opcion}")
            input("\nPresiona ENTER para salir...")
            return

    print(f"\n  Categoría: {categoria}")
    log_mensaje(f"Categoría: {categoria}")

    # Paso 4: Escanear videos
    print("\n[4/5] Escaneando videos en la carpeta")
    print("-" * 80)

    videos_por_cp = encontrar_videos_en_carpeta(carpeta_origen)

    if not videos_por_cp:
        print("\n  No se encontraron videos en carpetas CP.")
        print(f"\n  Estructura esperada:")
        print(f"    {carpeta_origen.name}/")
        print(f"      ├── CP123456/")
        print(f"      │   └── video.mp4")
        print(f"      └── CP123457/")
        print(f"          └── video.mp4")
        log_mensaje("ERROR: No se encontraron videos")
        input("\nPresiona ENTER para salir...")
        return

    # Mostrar resumen
    total_videos = sum(len(videos) for videos in videos_por_cp.values())
    total_tamaño = sum(
        sum(v.stat().st_size for v in videos)
        for videos in videos_por_cp.values()
    )

    print(f"\n  Videos encontrados:")
    print(f"    Carpetas CP: {len(videos_por_cp)}")
    print(f"    Total de videos: {total_videos}")
    print(f"    Tamaño total: {formatear_tamaño(total_tamaño)}")

    print(f"\n  Primeros CPs encontrados:")
    for cp, videos in list(videos_por_cp.items())[:5]:
        print(f"    CP{cp}: {len(videos)} video(s)")

    if len(videos_por_cp) > 5:
        print(f"    ... y {len(videos_por_cp) - 5} CPs más")

    # Mostrar destino
    carpeta_destino = EVIDENCIAS_ROOT / categoria / f"HU{numero_hu}"
    print(f"\n  Carpeta de destino:")
    print(f"    {carpeta_destino}")

    log_mensaje(f"Videos encontrados: {total_videos} en {len(videos_por_cp)} CPs")
    log_mensaje(f"Tamaño total: {formatear_tamaño(total_tamaño)}")
    log_mensaje(f"Destino: {carpeta_destino}")

    # Paso 5: Confirmar y copiar
    print("\n[5/5] Confirmación")
    print("-" * 80)

    confirmar = input("\n  ¿Proceder con la copia? (S/N): ").strip().upper()

    if confirmar != 'S':
        print("\n  Operación cancelada.")
        log_mensaje("Operación cancelada por el usuario")
        input("\nPresiona ENTER para salir...")
        return

    # Copiar videos
    print("\n" + "="*80)
    print("  COPIANDO VIDEOS...")
    print("="*80)

    copiados = 0
    ya_existian = 0
    sobrescritos = 0
    errores = 0

    for cp, videos in videos_por_cp.items():
        carpeta_cp_destino = carpeta_destino / f"CP{cp}"

        print(f"\n  CP{cp} ({len(videos)} video(s)):")
        log_mensaje(f"Procesando CP{cp} con {len(videos)} videos", consola=False)

        for video in videos:
            destino = carpeta_cp_destino / video.name
            print(f"    {video.name}...", end=" ")

            exito, mensaje = copiar_video(video, destino)

            if exito:
                if "Ya existe" in mensaje:
                    ya_existian += 1
                    print(f"[EXISTE]")
                    log_mensaje(f"  {video.name}: {mensaje}", consola=False)
                elif "Sobrescrito" in mensaje:
                    sobrescritos += 1
                    print(f"[SOBRESCRITO]")
                    log_mensaje(f"  {video.name}: {mensaje}", consola=False)
                else:
                    copiados += 1
                    print(f"[COPIADO]")
                    log_mensaje(f"  {video.name}: {mensaje}", consola=False)
            else:
                errores += 1
                print(f"[ERROR]")
                print(f"      {mensaje}")
                log_mensaje(f"  {video.name}: {mensaje}", consola=False)

    # Resumen final
    print("\n" + "="*80)
    print("  COPIA COMPLETADA")
    print("="*80)

    print(f"\n  Resultados:")
    print(f"    Copiados nuevos:  {copiados}")
    print(f"    Ya existían:      {ya_existian}")
    print(f"    Sobrescritos:     {sobrescritos}")
    print(f"    Errores:          {errores}")
    print(f"    Total procesados: {total_videos}")

    print(f"\n  Ubicación final:")
    print(f"    {carpeta_destino}")

    print(f"\n  Log guardado en:")
    print(f"    {LOG_PATH}")

    log_mensaje("="*80, archivo=True, consola=False)
    log_mensaje(f"RESUMEN: {copiados} copiados, {ya_existian} existían, {sobrescritos} sobrescritos, {errores} errores", archivo=True, consola=False)
    log_mensaje("FIN DE COPIA DE VIDEOS", archivo=True, consola=False)
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
