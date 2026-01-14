"""
VERIFICADOR DE ESTADO DE CERTIFICACIONES
=========================================
Escanea todas las certificaciones y muestra:
- Cuantas tienen links completos
- Cuantas tienen links parciales
- Cuantas estan vacias (sin links)

Util para ejecutar ANTES y DESPUES del procesamiento masivo.

Uso: py verificar_estado_certificaciones.py
"""

import sys
import os
import re
import win32com.client
from pathlib import Path
from datetime import datetime

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener la raiz del proyecto AutCert
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Agregar al path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar configuracion centralizada de rutas
from config_paths import CERTIFICACIONES_ROOT_STR

# ============================================
# CONFIGURACION
# ============================================

RUTA_CERTIFICACIONES = CERTIFICACIONES_ROOT_STR
CATEGORIAS = ['AyN', 'RyC', 'Transversal']

# ============================================
# FUNCIONES
# ============================================

def verificar_excel(ruta_excel):
    """
    Verifica el estado de links en un Excel de certificacion.
    Retorna: (total_filas, con_link, sin_link)
    """
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.DisplayAlerts = False
        excel.Visible = False

        workbook = excel.Workbooks.Open(ruta_excel)
        worksheet = workbook.Worksheets(1)

        total_filas = 0
        con_link = 0
        sin_link = 0

        fila = 21
        while True:
            tc_id = worksheet.Cells(fila, 3).Value

            if tc_id is None:
                break

            tc_id_str = str(tc_id).strip()

            # Manejar decimales
            try:
                if '.' in tc_id_str and tc_id_str.replace('.', '').isdigit():
                    tc_id_str = str(int(float(tc_id_str)))
            except:
                pass

            # Si es texto largo (conclusion), terminar
            if len(tc_id_str) > 10 or "CONCLUSION" in tc_id_str.upper():
                break

            total_filas += 1

            # Verificar si tiene link en columna F
            link = worksheet.Cells(fila, 6).Value
            if link and str(link).strip().startswith("http"):
                con_link += 1
            else:
                sin_link += 1

            fila += 1

        workbook.Close(False)
        excel.Quit()

        return (total_filas, con_link, sin_link)

    except Exception as e:
        try:
            workbook.Close(False)
            excel.Quit()
        except:
            pass
        return (0, 0, 0)


def escanear_certificaciones():
    """Escanea todas las certificaciones disponibles"""
    certificaciones = []

    for categoria in CATEGORIAS:
        ruta_cat = os.path.join(RUTA_CERTIFICACIONES, categoria)
        if not os.path.exists(ruta_cat):
            continue

        for archivo in os.listdir(ruta_cat):
            if archivo.startswith("Certificacion_QA_") and archivo.endswith(".xlsx"):
                match = re.search(r'Certificacion_QA_(\d+)\.xlsx', archivo)
                if match:
                    numero_hu = match.group(1)
                    ruta_completa = os.path.join(ruta_cat, archivo)
                    certificaciones.append({
                        'numero_hu': numero_hu,
                        'categoria': categoria,
                        'archivo': archivo,
                        'ruta': ruta_completa
                    })

    certificaciones.sort(key=lambda x: int(x['numero_hu']))
    return certificaciones


def main():
    print("=" * 70)
    print("       VERIFICADOR DE ESTADO DE CERTIFICACIONES")
    print("=" * 70)
    print()

    # Escanear certificaciones
    print("Escaneando certificaciones...")
    certificaciones = escanear_certificaciones()

    if len(certificaciones) == 0:
        print("[!] No se encontraron certificaciones")
        return

    print(f"Encontradas {len(certificaciones)} certificaciones")
    print()
    print("Verificando estado de links (esto puede tomar unos minutos)...")
    print()

    # Contadores globales
    total_cert = len(certificaciones)
    completas = []      # 100% links
    parciales = []      # Algunos links
    vacias = []         # Sin links

    total_filas_global = 0
    total_con_link_global = 0
    total_sin_link_global = 0

    # Procesar cada certificacion
    for i, cert in enumerate(certificaciones, 1):
        # Mostrar progreso
        porcentaje = (i / total_cert) * 100
        print(f"\r  [{i}/{total_cert}] ({porcentaje:.0f}%) Verificando HU{cert['numero_hu']}...", end="", flush=True)

        total_filas, con_link, sin_link = verificar_excel(cert['ruta'])

        cert['total_filas'] = total_filas
        cert['con_link'] = con_link
        cert['sin_link'] = sin_link

        total_filas_global += total_filas
        total_con_link_global += con_link
        total_sin_link_global += sin_link

        if total_filas > 0:
            if sin_link == 0:
                completas.append(cert)
            elif con_link == 0:
                vacias.append(cert)
            else:
                parciales.append(cert)
        else:
            vacias.append(cert)

    print()
    print()

    # Mostrar resumen
    print("=" * 70)
    print("                         RESUMEN")
    print("=" * 70)
    print()

    porcentaje_completo = (len(completas) / total_cert * 100) if total_cert > 0 else 0

    print(f"  Total certificaciones:     {total_cert}")
    print(f"  [+] Completas (100%):      {len(completas)}")
    print(f"  [~] Parciales:             {len(parciales)}")
    print(f"  [-] Vacias (sin links):    {len(vacias)}")
    print()
    print(f"  Progreso global:           {porcentaje_completo:.1f}% certificaciones completas")
    print()

    # Estadisticas de links
    porcentaje_links = (total_con_link_global / total_filas_global * 100) if total_filas_global > 0 else 0
    print(f"  Total filas (Test Cases):  {total_filas_global}")
    print(f"  Con link:                  {total_con_link_global}")
    print(f"  Sin link:                  {total_sin_link_global}")
    print(f"  Cobertura de links:        {porcentaje_links:.1f}%")
    print()

    # Desglose por categoria
    print("=" * 70)
    print("                    DESGLOSE POR CATEGORIA")
    print("=" * 70)
    print()

    for cat in CATEGORIAS:
        certs_cat = [c for c in certificaciones if c['categoria'] == cat]
        completas_cat = [c for c in completas if c['categoria'] == cat]
        parciales_cat = [c for c in parciales if c['categoria'] == cat]
        vacias_cat = [c for c in vacias if c['categoria'] == cat]

        print(f"  {cat}:")
        print(f"    Total:     {len(certs_cat)}")
        print(f"    Completas: {len(completas_cat)}")
        print(f"    Parciales: {len(parciales_cat)}")
        print(f"    Vacias:    {len(vacias_cat)}")
        print()

    # Mostrar certificaciones vacias
    if vacias:
        print("=" * 70)
        print("              CERTIFICACIONES SIN LINKS (PENDIENTES)")
        print("=" * 70)
        print()
        for cert in vacias[:20]:  # Mostrar max 20
            print(f"  - HU{cert['numero_hu']} ({cert['categoria']})")
        if len(vacias) > 20:
            print(f"  ... y {len(vacias) - 20} mas")
        print()

    # Mostrar certificaciones parciales
    if parciales:
        print("=" * 70)
        print("             CERTIFICACIONES PARCIALES (INCOMPLETAS)")
        print("=" * 70)
        print()
        for cert in parciales[:15]:
            porcentaje = (cert['con_link'] / cert['total_filas'] * 100) if cert['total_filas'] > 0 else 0
            print(f"  - HU{cert['numero_hu']} ({cert['categoria']}): {cert['con_link']}/{cert['total_filas']} ({porcentaje:.0f}%)")
        if len(parciales) > 15:
            print(f"  ... y {len(parciales) - 15} mas")
        print()

    print("=" * 70)
    print(f"  Verificacion completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
    print("\nPresiona ENTER para salir...")
    input()
