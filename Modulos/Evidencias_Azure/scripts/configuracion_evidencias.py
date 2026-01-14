"""
CONFIGURACIÓN CENTRALIZADA PARA CAPTURA DE EVIDENCIAS EN AZURE DEVOPS
========================================================================
Archivo de configuración único para captura de evidencias.
Edita estos valores según tu PC.
"""

import os
import sys
from pathlib import Path

# ============================================
# RUTAS DE ARCHIVOS
# ============================================

# Directorio base del proyecto (automático - apunta a raíz del proyecto)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # WebScraping_Evidencias/scripts/
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))  # WebScraping_Evidencias/

# Obtener la raíz del proyecto AutCert (3 niveles arriba: scripts -> Evidencias_Azure -> Modulos -> AutCert)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Añadir la raíz del proyecto al path para importar config_paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuración centralizada de rutas
from config_paths import EVIDENCIAS_ROOT_STR

# Perfil de Selenium (en datos/cache/)
SELENIUM_PROFILE_DIR = os.path.join(BASE_DIR, "datos", "cache", "selenium_profile")

# Archivos de salida (automáticos - en datos/)
LOG_DIR = os.path.join(BASE_DIR, "datos", "logs")
LOG_FILE = os.path.join(LOG_DIR, "captura_evidencias.log")

# Carpeta de evidencias (donde se guardarán las capturas) - Ruta dinámica
EVIDENCIAS_BASE = EVIDENCIAS_ROOT_STR

# ============================================
# CONFIGURACIÓN DE AZURE DEVOPS
# ============================================

# URL base de Azure DevOps para work items
AZURE_DEVOPS_BASE_URL = "https://dev.azure.com/Linktic/368%20-%20GAL/_workitems/edit/"

# XPath del botón de historial
HISTORY_TAB_XPATH = '/html/body/div[3]/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[2]/div/div[1]/div/div[3]/div[2]/div/div[6]'

# ============================================
# CONFIGURACIÓN DE SELENIUM
# ============================================

# Tiempos de espera (ajusta según la velocidad de tu PC/internet)
TIEMPO_INICIAL_LOGIN = 45  # Segundos para iniciar sesión la primera vez en Azure
TIEMPO_CARGA_PAGINA = 3    # Segundos después de navegar a una página (ahora usa WebDriverWait)
TIEMPO_ESPERA_CLICK = 1    # Segundos después de hacer click
TIEMPO_ESPERA_SCREENSHOT = 1  # Segundos antes de tomar screenshot (render final)

# ============================================
# CONFIGURACIÓN DE CHROME
# ============================================

# Opciones de Chrome
CHROME_OPTIONS = {
    'headless': False,  # True = sin interfaz gráfica, False = ver el navegador
    'sandbox': False,   # Desactivar sandbox (más compatible)
    'dev_shm': False,   # Desactivar /dev/shm (para PCs con poca RAM)
    'remote_debug': True,  # Habilitar debug remoto
}

# ============================================
# CONFIGURACIÓN DE CAPTURAS
# ============================================

# Formato de imagen para capturas
SCREENSHOT_FORMAT = "png"  # png o jpg

# Calidad de imagen (1-100, solo para jpg)
SCREENSHOT_QUALITY = 95

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

    # Maximizar ventana para capturas completas
    chrome_options.add_argument("--start-maximized")

    # Opciones configurables
    if CHROME_OPTIONS['headless']:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")

    if not CHROME_OPTIONS['sandbox']:
        chrome_options.add_argument("--no-sandbox")

    if not CHROME_OPTIONS['dev_shm']:
        chrome_options.add_argument("--disable-dev-shm-usage")

    if CHROME_OPTIONS['remote_debug']:
        chrome_options.add_argument("--remote-debugging-port=9223")

    return chrome_options


def asegurar_directorios():
    """Crea los directorios necesarios si no existen"""
    os.makedirs(SELENIUM_PROFILE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(EVIDENCIAS_BASE, exist_ok=True)


def verificar_sesion_guardada():
    """Verifica si existe una sesión guardada de Chrome para Azure DevOps"""
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
