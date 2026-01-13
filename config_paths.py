"""
Configuración centralizada de rutas para el proyecto AutCert.
Este archivo define todas las rutas de manera dinámica para que el proyecto
sea portable entre diferentes PCs sin necesidad de modificar código.

ESTRUCTURA DE CARPETAS:
======================
El proyecto se divide en DOS ubicaciones:

1. CARPETA DE CÓDIGO (AutCert/)
   - Contiene todo el código fuente y configuraciones
   - Ubicación: Donde coloques la carpeta AutCert

2. CARPETA DE DATOS (EntregaCerts/)
   - Contiene los archivos de trabajo (certificaciones, evidencias, PDFs)
   - Ubicación: Un nivel ARRIBA de la carpeta AutCert

Ejemplo de estructura:
    C:/Users/TuUsuario/Proyectos/
    ├── EntregaCerts/                    ← Carpeta de datos (se crea automáticamente)
    │   ├── Certificaciones/
    │   │   ├── AyN/
    │   │   ├── RyC/
    │   │   └── Transversal/
    │   ├── Certificaciones_PDF/
    │   │   ├── AyN/
    │   │   ├── RyC/
    │   │   └── Transversal/
    │   └── Evidencias/
    └── AutCert/                         ← Carpeta del proyecto (código)
        ├── config_paths.py
        ├── Modulos/
        ├── Assets/
        └── Logs/

¿CÓMO FUNCIONA EL ENRUTAMIENTO DINÁMICO?
=========================================
1. El script detecta su propia ubicación usando Path(__file__)
2. Sube un nivel (.parent) para encontrar la carpeta contenedora
3. Desde ahí, accede a "EntregaCerts" (carpeta hermana de AutCert)
4. Todas las rutas se calculan automáticamente sin importar dónde coloques el proyecto

BENEFICIOS:
===========
✓ Separación de código y datos
✓ Fácil backup del código sin incluir archivos grandes
✓ Los datos persisten aunque actualices el código
✓ Múltiples instalaciones pueden compartir la misma carpeta EntregaCerts
✓ Totalmente portable entre PCs
"""

import os
from pathlib import Path

# ============================================================================
# DETECCIÓN AUTOMÁTICA DE RUTAS
# ============================================================================

# 1. Detectar dónde está este archivo (config_paths.py)
PROJECT_ROOT = Path(__file__).parent.resolve()
# Ejemplo: C:/Users/Julian/Proyectos/AutCert

# 2. Subir un nivel para encontrar la carpeta contenedora
PARENT_DIR = PROJECT_ROOT.parent
# Ejemplo: C:/Users/Julian/Proyectos

# 3. Definir la carpeta de datos (hermana de AutCert)
DATA_ROOT = PARENT_DIR / "EntregaCerts"
# Ejemplo: C:/Users/Julian/Proyectos/EntregaCerts

# ============================================================================
# DIRECTORIOS DENTRO DEL PROYECTO (CÓDIGO)
# ============================================================================

ASSETS_DIR = PROJECT_ROOT / "Assets"
BASE_DATOS_DIR = ASSETS_DIR / "Base de datos"
REPORTES_DIR = ASSETS_DIR / "Reportes"
LOGS_DIR = PROJECT_ROOT / "Logs"
MODULOS_DIR = PROJECT_ROOT / "Modulos"

# ============================================================================
# DIRECTORIOS EN CARPETA EXTERNA (DATOS)
# ============================================================================

# Certificaciones (archivos Excel)
CERTIFICACIONES_ROOT = DATA_ROOT / "Certificaciones"
CERTIFICACIONES_AYN = CERTIFICACIONES_ROOT / "AyN"
CERTIFICACIONES_RYC = CERTIFICACIONES_ROOT / "RyC"
CERTIFICACIONES_TRANSVERSAL = CERTIFICACIONES_ROOT / "Transversal"

# PDFs generados
PDF_ROOT = DATA_ROOT / "Certificaciones_PDF"
PDF_AYN = PDF_ROOT / "AyN"
PDF_RYC = PDF_ROOT / "RyC"
PDF_TRANSVERSAL = PDF_ROOT / "Transversal"

# Evidencias capturadas
EVIDENCIAS_ROOT = DATA_ROOT / "Evidencias"

# ============================================================================
# ARCHIVOS Y RUTAS ESPECÍFICAS
# ============================================================================

# Archivos de datos
CSV_PATH = BASE_DATOS_DIR / "data.csv"

# Módulos específicos
LINKS_DRIVE_DIR = MODULOS_DIR / "Links_Drive"
EVIDENCIAS_AZURE_DIR = MODULOS_DIR / "Evidencias_Azure"
ANALISIS_DIR = MODULOS_DIR / "Analisis"
RENOMBRADO_DIR = MODULOS_DIR / "Renombrado"
CONVERSION_PDF_DIR = MODULOS_DIR / "Conversion_PDF"
CONTROL_EJECUCION_DIR = MODULOS_DIR / "Control_Ejecucion"

# Logs específicos por módulo
LOG_CONVERSION_PDF = LOGS_DIR / "conversion.log"
LOG_RENOMBRADO = LOGS_DIR / "renombrado.log"
LOG_CONTROL_EJECUCION = LOGS_DIR / "control_ejecucion.log"

# Archivos de salida específicos
CONTROL_EJECUCION_OUTPUT = CONTROL_EJECUCION_DIR / "datos" / "control_ejecucion.xlsx"

# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

def crear_directorios():
    """
    Crea los directorios necesarios si no existen.

    Esta función se ejecuta automáticamente al importar este módulo,
    creando toda la estructura de carpetas necesaria tanto en el proyecto
    como en la carpeta externa EntregaCerts.
    """
    # Directorios dentro del proyecto (código)
    directorios_proyecto = [
        ASSETS_DIR,
        BASE_DATOS_DIR,
        REPORTES_DIR,
        LOGS_DIR
    ]

    # Directorios en carpeta externa (datos)
    directorios_datos = [
        DATA_ROOT,
        CERTIFICACIONES_ROOT,
        CERTIFICACIONES_AYN,
        CERTIFICACIONES_RYC,
        CERTIFICACIONES_TRANSVERSAL,
        PDF_ROOT,
        PDF_AYN,
        PDF_RYC,
        PDF_TRANSVERSAL,
        EVIDENCIAS_ROOT
    ]

    # Crear todos los directorios
    for directorio in directorios_proyecto + directorios_datos:
        directorio.mkdir(parents=True, exist_ok=True)

    # Mostrar mensaje informativo solo la primera vez
    if not (DATA_ROOT / ".inicializado").exists():
        print(f"✓ Estructura de carpetas creada en: {DATA_ROOT}")
        # Crear archivo marcador para no mostrar el mensaje de nuevo
        (DATA_ROOT / ".inicializado").touch()

# Función auxiliar para obtener rutas como string (para compatibilidad con código antiguo)
def get_path_str(path):
    """Convierte un Path a string."""
    return str(path)

# Crear directorios al importar este módulo
crear_directorios()

# Exportar versiones string de las rutas principales para compatibilidad
CSV_PATH_STR = str(CSV_PATH)
CERTIFICACIONES_ROOT_STR = str(CERTIFICACIONES_ROOT)
PDF_ROOT_STR = str(PDF_ROOT)
EVIDENCIAS_ROOT_STR = str(EVIDENCIAS_ROOT)
REPORTES_DIR_STR = str(REPORTES_DIR)
LOG_CONVERSION_PDF_STR = str(LOG_CONVERSION_PDF)
LOG_RENOMBRADO_STR = str(LOG_RENOMBRADO)
CONTROL_EJECUCION_DIR_STR = str(CONTROL_EJECUCION_DIR)
CONTROL_EJECUCION_OUTPUT_STR = str(CONTROL_EJECUCION_OUTPUT)
