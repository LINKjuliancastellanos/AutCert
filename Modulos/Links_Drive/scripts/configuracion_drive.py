"""
CONFIGURACIÓN CENTRALIZADA PARA SCRAPING DE DRIVE
==================================================
Archivo de configuración único para todos los scripts.
Edita estos valores según tu PC.
"""

import os
import sys
from pathlib import Path

# ============================================
# RUTAS DE ARCHIVOS
# ============================================

# Directorio base del proyecto (automático - apunta a raíz del proyecto)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # WebScraping_Drive/scripts/
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))  # WebScraping_Drive/

# Obtener la raíz del proyecto AutCert (3 niveles arriba: scripts -> Links_Drive -> Modulos -> AutCert)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import CSV_PATH_STR

# Perfil de Selenium (en datos/cache/)
SELENIUM_PROFILE_DIR = os.path.join(BASE_DIR, "datos", "cache", "selenium_profile")

# Archivos de salida (automáticos - en datos/)
OUTPUT_JSON = os.path.join(BASE_DIR, "datos", "mapeo_drive.json")
MIS_HUS_JSON = os.path.join(BASE_DIR, "datos", "mis_hus_drive.json")
LOG_DIR = os.path.join(BASE_DIR, "datos", "logs", "drive")
LOG_FILE = os.path.join(LOG_DIR, "scraping_completo.log")

# CSV de datos (ruta dinámica al CSV principal del proyecto)
CSV_PATH = CSV_PATH_STR

# ============================================
# CONFIGURACIÓN DE GOOGLE DRIVE
# ============================================

# URL raíz de Drive (tu carpeta principal)
DRIVE_ROOT_URL = "https://drive.google.com/drive/folders/1LOxZl_LY40jx-aq567TrWiSOo_QrO67S"

# Categorías a escanear
CATEGORIAS = [
    "Afiliaciones y Novedades",
    "Recaudo y Cartera",
    "Transversales"
]

# ============================================
# CONFIGURACIÓN DE SELENIUM
# ============================================

# Tiempos de espera (ajusta según la velocidad de tu PC/internet)
TIEMPO_INICIAL_LOGIN = 30  # Segundos para iniciar sesión la primera vez
TIEMPO_CARGA_PAGINA = 5    # Segundos después de navegar a una página
TIEMPO_SCROLL = 2          # Segundos entre scrolls
TIEMPO_BUSQUEDA = 5        # Segundos después de buscar

# Scroll
MAX_INTENTOS_SCROLL = 25   # Intentos máximos de scroll
INTENTOS_SIN_CAMBIO = 6    # Parar después de N intentos sin cambio

# ============================================
# CONFIGURACIÓN DE CHROME
# ============================================

# Opciones de Chrome (puedes habilitar/deshabilitar según necesites)
CHROME_OPTIONS = {
    'headless': False,  # True = sin interfaz gráfica, False = ver el navegador
    'sandbox': False,   # Desactivar sandbox (más compatible)
    'dev_shm': False,   # Desactivar /dev/shm (para PCs con poca RAM)
    'remote_debug': True,  # Habilitar debug remoto
}

# ============================================
# USUARIO
# ============================================

# Tu nombre como aparece en el CSV (para filtrar tus HUs)
MI_NOMBRE = "Julian Mateo Castellanos Cuervo"

# ============================================
# FUNCIONES DE CONFIGURACIÓN
# ============================================

def get_chrome_options():
    """Genera las opciones de Chrome según la configuración"""
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()

    # Crear directorio de perfil si no existe
    os.makedirs(SELENIUM_PROFILE_DIR, exist_ok=True)

    # Usar perfil dedicado
    chrome_options.add_argument(f"user-data-dir={SELENIUM_PROFILE_DIR}")

    # Opciones básicas
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Opciones configurables
    if CHROME_OPTIONS['headless']:
        chrome_options.add_argument("--headless")

    if not CHROME_OPTIONS['sandbox']:
        chrome_options.add_argument("--no-sandbox")

    if not CHROME_OPTIONS['dev_shm']:
        chrome_options.add_argument("--disable-dev-shm-usage")

    if CHROME_OPTIONS['remote_debug']:
        chrome_options.add_argument("--remote-debugging-port=9222")

    return chrome_options


def asegurar_directorios():
    """Crea los directorios necesarios si no existen"""
    os.makedirs(SELENIUM_PROFILE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def verificar_sesion_guardada():
    """Verifica si existe una sesión guardada de Chrome"""
    # Buscar archivos de sesión de Chrome
    archivos_sesion = [
        os.path.join(SELENIUM_PROFILE_DIR, "Default", "Cookies"),
        os.path.join(SELENIUM_PROFILE_DIR, "Default", "Preferences"),
    ]

    return any(os.path.exists(f) for f in archivos_sesion)


# ============================================
# INICIALIZACIÓN
# ============================================

# Crear directorios al importar
asegurar_directorios()
