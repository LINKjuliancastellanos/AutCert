"""
INICIAR SESION EN GOOGLE DRIVE - VERSION PLAYWRIGHT
=====================================================
Script para iniciar sesion en Drive una sola vez usando Playwright.
Usa un perfil completamente aislado de tu Chrome personal.
NO necesitas cerrar tu Chrome actual.

Uso: py iniciar_sesion_playwright.py
"""

import sys
import os
import time
from pathlib import Path

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Obtener rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Directorio para datos de usuario de Playwright
PLAYWRIGHT_USER_DATA = os.path.join(BASE_DIR, "datos", "cache", "playwright_profile")
os.makedirs(PLAYWRIGHT_USER_DATA, exist_ok=True)


def verificar_sesion_playwright():
    """Verifica si existe una sesion guardada de Playwright"""
    # Buscar archivos de sesion en el perfil de Playwright
    archivos_sesion = [
        os.path.join(PLAYWRIGHT_USER_DATA, "Default", "Cookies"),
        os.path.join(PLAYWRIGHT_USER_DATA, "Default", "Preferences"),
        os.path.join(PLAYWRIGHT_USER_DATA, "Default", "Local Storage"),
    ]
    return any(os.path.exists(f) for f in archivos_sesion)


def main():
    print("=" * 80)
    print("   INICIAR SESION EN GOOGLE DRIVE (PLAYWRIGHT)")
    print("=" * 80)
    print()
    print("Este script usa un perfil aislado (como modo invitado).")
    print("NO interfiere con tu Chrome personal.")
    print()

    # Verificar si ya hay sesion guardada
    if verificar_sesion_playwright():
        print("[+] Ya existe una sesion guardada de Playwright")
        print()
        respuesta = input("Quieres crear una nueva sesion? (s/n): ").strip().lower()
        if respuesta != 's':
            print("\nCancelado. Usando sesion existente.")
            print("\nPuedes ejecutar:")
            print("  - 6_Completar_HU_Playwright.bat (para una HU)")
            print("  - 5_Procesar_Masivo_Playwright.bat (para todas)")
            return

    print("=" * 80)
    print("INSTRUCCIONES:")
    print("=" * 80)
    print()
    print("1. Se abrira un Chrome SEPARADO (sin tus sesiones actuales)")
    print("2. Inicia sesion en Google manualmente")
    print("3. Navega a https://drive.google.com")
    print("4. Ve a tu carpeta de evidencias de HUs")
    print("5. Tienes 120 segundos (2 minutos)")
    print("6. La sesion se guardara automaticamente")
    print()
    print("NOTA: NO necesitas cerrar tu Chrome actual")
    print()
    print("=" * 80)
    print()

    input("Presiona ENTER para abrir Chrome con Playwright...")

    print()
    print("[*] Iniciando Playwright...")
    print("    (Completamente separado de tu Chrome normal)")
    print()

    try:
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()

        # Usar contexto persistente para mantener la sesion
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=PLAYWRIGHT_USER_DATA,
            headless=False,
            viewport={'width': 1280, 'height': 900},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("[+] Chrome abierto exitosamente")
        print()

        # Navegar a Google Drive
        print("[*] Navegando a Google Drive...")
        page.goto("https://drive.google.com")
        page.wait_for_timeout(2000)

        print()
        print("=" * 80)
        print("   TIEMPO PARA INICIAR SESION")
        print("=" * 80)
        print()
        print("PASOS:")
        print("-" * 80)
        print()
        print("1. Si aparece pantalla de login, inicia sesion con tu cuenta de Google")
        print("2. Navega a tu carpeta de evidencias de HUs")
        print("3. ESPERA hasta que termine el tiempo (NO cierres el navegador)")
        print()
        print("   Tiempo disponible: 120 segundos (2 minutos)")
        print()
        print("-" * 80)
        print()

        # Countdown de 120 segundos
        segundos_totales = 120
        for i in range(segundos_totales, 0, -10):
            print(f"   [{i:3d} segundos restantes...]", end="\r")
            page.wait_for_timeout(10000)

        print()
        print()
        print("   Tiempo terminado!")
        print()

        print("=" * 80)
        print("   SESION GUARDADA")
        print("=" * 80)
        print()
        print("Tu sesion ha sido guardada en un perfil aislado.")
        print()
        print("IMPORTANTE:")
        print("-" * 80)
        print("  - Este perfil es INDEPENDIENTE de tu Chrome normal")
        print("  - Los scripts de Playwright usaran este perfil automaticamente")
        print("  - Tu Chrome personal NO fue afectado")
        print()
        print("Ahora puedes ejecutar:")
        print("  - 6_Completar_HU_Playwright.bat (para una HU)")
        print("  - 5_Procesar_Masivo_Playwright.bat (para todas)")
        print()
        print("=" * 80)
        print()

        input("Presiona ENTER para cerrar Chrome...")

        context.close()
        playwright.stop()

        print()
        print("[+] Navegador cerrado")

    except ImportError:
        print()
        print("[!] Error: Playwright no esta instalado")
        print()
        print("SOLUCION:")
        print("-" * 80)
        print()
        print("1. Ejecuta: pip install playwright")
        print("2. Ejecuta: playwright install chromium")
        print("3. Vuelve a ejecutar este script")
        print()
        input("\nPresiona ENTER para salir...")
        return

    except Exception as e:
        print(f"\n[!] Error: {e}")
        print()
        print("SOLUCION:")
        print("-" * 80)
        print()
        print("Si el error persiste:")
        print("  1. Elimina la carpeta: datos/cache/playwright_profile")
        print("  2. Vuelve a ejecutar este script")
        print()
        input("\nPresiona ENTER para salir...")
        return

    print()
    print("[+] Proceso completado!")
    print()
    print("RECUERDA: Tu Chrome normal NO fue afectado.")
    print()


if __name__ == "__main__":
    main()
    print("\nPresiona ENTER para salir...")
    input()
