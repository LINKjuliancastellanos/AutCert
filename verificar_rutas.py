"""
Script para verificar que todas las rutas estén correctamente configuradas
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

print("="*80)
print("VERIFICACIÓN DE RUTAS DINÁMICAS - AutCert")
print("="*80)
print()

print("RUTAS DETECTADAS:")
print("-" * 80)
print(f"1. PROJECT_ROOT (Carpeta del código):")
print(f"   {PROJECT_ROOT}")
print(f"   Existe: {'SI' if PROJECT_ROOT.exists() else 'NO'}")
print()

print(f"2. PARENT_DIR (Carpeta contenedora):")
print(f"   {PARENT_DIR}")
print(f"   Existe: {'SI' if PARENT_DIR.exists() else 'NO'}")
print()

print(f"3. DATA_ROOT (Carpeta de datos EntregaCerts):")
print(f"   {DATA_ROOT}")
print(f"   Existe: {'SI' if DATA_ROOT.exists() else 'NO'}")
print()

print("-" * 80)
print("CARPETAS DE DATOS:")
print("-" * 80)

carpetas_datos = [
    ("Certificaciones", CERTIFICACIONES_ROOT),
    ("Certificaciones_PDF", PDF_ROOT),
    ("Evidencias", EVIDENCIAS_ROOT),
]

for nombre, ruta in carpetas_datos:
    existe = ruta.exists()
    print(f"  {nombre}:")
    print(f"    Ruta: {ruta}")
    print(f"    Existe: {'SI ✓' if existe else 'NO ✗'}")
    print()

print("-" * 80)
print("ARCHIVOS IMPORTANTES:")
print("-" * 80)

archivos = [
    ("CSV de datos", CSV_PATH),
    ("Logs", LOGS_DIR),
]

for nombre, ruta in archivos:
    existe = ruta.exists()
    print(f"  {nombre}:")
    print(f"    Ruta: {ruta}")
    print(f"    Existe: {'SI ✓' if existe else 'NO ✗'}")
    print()

print("="*80)
print("VERIFICACIÓN DE ESTRUCTURA:")
print("="*80)

# Verificar estructura esperada
estructura_correcta = True

if not DATA_ROOT.exists():
    print("✗ La carpeta EntregaCerts NO existe")
    estructura_correcta = False
else:
    print("✓ La carpeta EntregaCerts existe")

# Verificar subcarpetas
subcarpetas_esperadas = [
    CERTIFICACIONES_ROOT,
    CERTIFICACIONES_ROOT / "AyN",
    CERTIFICACIONES_ROOT / "RyC",
    CERTIFICACIONES_ROOT / "Transversal",
    PDF_ROOT,
    PDF_ROOT / "AyN",
    PDF_ROOT / "RyC",
    PDF_ROOT / "Transversal",
    EVIDENCIAS_ROOT,
]

carpetas_faltantes = []
for carpeta in subcarpetas_esperadas:
    if not carpeta.exists():
        carpetas_faltantes.append(carpeta)

if carpetas_faltantes:
    print(f"✗ Faltan {len(carpetas_faltantes)} carpetas:")
    for carpeta in carpetas_faltantes:
        print(f"    - {carpeta.relative_to(DATA_ROOT)}")
    estructura_correcta = False
else:
    print(f"✓ Todas las subcarpetas existen ({len(subcarpetas_esperadas)} carpetas)")

print()
if estructura_correcta:
    print("="*80)
    print("✓✓✓ TODAS LAS RUTAS ESTÁN CORRECTAMENTE CONFIGURADAS ✓✓✓")
    print("="*80)
else:
    print("="*80)
    print("⚠ ALGUNAS CARPETAS NECESITAN SER CREADAS")
    print("="*80)
    print("\nEjecuta cualquier script del proyecto y se crearán automáticamente.")

print("\nPresiona ENTER para salir...")
input()
