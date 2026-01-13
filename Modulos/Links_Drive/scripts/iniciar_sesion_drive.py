"""
INICIAR SESIÓN EN GOOGLE DRIVE
================================
Script para iniciar sesión en Drive una sola vez.
Después de esto, los otros scripts usarán la sesión guardada.
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configurar encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Importar configuración
from configuracion_drive import (
    DRIVE_ROOT_URL,
    TIEMPO_INICIAL_LOGIN,
    get_chrome_options,
    verificar_sesion_guardada
)

def main():
    print("="*80)
    print("INICIAR SESIÓN EN GOOGLE DRIVE")
    print("="*80)
    print()

    # Verificar si ya hay sesión guardada
    if verificar_sesion_guardada():
        print("✓ Ya existe una sesión guardada")
        print()
        respuesta = input("¿Quieres crear una nueva sesión? (s/n): ").strip().lower()
        if respuesta != 's':
            print("\nCancelado. Usando sesión existente.")
            return

    print("="*80)
    print("INSTRUCCIONES:")
    print("="*80)
    print()
    print("1. Se abrirá Google Chrome")
    print("2. Inicia sesión en tu cuenta de Google")
    print("3. Navega a Drive y verifica que puedas ver las carpetas")
    print(f"4. Tienes {TIEMPO_INICIAL_LOGIN} segundos para hacer esto")
    print("5. La sesión se guardará automáticamente")
    print()
    print("="*80)
    print()

    input("Presiona ENTER para abrir Chrome...")

    # Configurar Chrome
    chrome_options = get_chrome_options()

    print("\n🌐 Abriendo Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # Navegar a Drive
        print(f"📂 Navegando a Google Drive...")
        driver.get(DRIVE_ROOT_URL)

        print()
        print("="*80)
        print("⏰ TIEMPO PARA INICIAR SESIÓN")
        print("="*80)
        print()
        print(f"Tienes {TIEMPO_INICIAL_LOGIN} segundos")
        print()
        print("Por favor:")
        print("  1. Inicia sesión si es necesario")
        print("  2. Verifica que ves las carpetas de Drive")
        print("  3. NO cierres el navegador")
        print()

        # Countdown
        for i in range(TIEMPO_INICIAL_LOGIN, 0, -5):
            print(f"   Tiempo restante: {i} segundos...")
            time.sleep(5)

        print()
        print("="*80)
        print("✅ SESIÓN GUARDADA")
        print("="*80)
        print()
        print("Tu sesión ha sido guardada exitosamente.")
        print("Los próximos scripts usarán esta sesión automáticamente.")
        print()
        print("NOTA: La sesión permanecerá activa incluso después de cerrar Chrome.")
        print()

        input("Presiona ENTER para cerrar Chrome...")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        input("\nPresiona ENTER para cerrar...")

    finally:
        driver.quit()
        print("\n✓ Navegador cerrado")
        print("\n✅ ¡Listo! Ahora puedes ejecutar los otros scripts sin iniciar sesión.")


if __name__ == "__main__":
    main()
