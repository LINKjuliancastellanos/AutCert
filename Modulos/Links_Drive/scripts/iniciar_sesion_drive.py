"""
INICIAR SESIÓN EN GOOGLE DRIVE
================================
Script para iniciar sesión en Drive una sola vez.
Usa un perfil completamente aislado de tu Chrome personal.
NO necesitas cerrar tu Chrome actual.
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
    get_chrome_options,
    verificar_sesion_guardada
)

def main():
    print("="*80)
    print("INICIAR SESIÓN EN GOOGLE DRIVE")
    print("="*80)
    print()
    print("Este script usa un perfil aislado (como modo invitado).")
    print("NO interfiere con tu Chrome personal.")
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
    print("1. Se abrirá un Chrome SEPARADO (sin tus sesiones actuales)")
    print("2. Inicia sesión en Google manualmente")
    print("3. Navega a https://drive.google.com")
    print("4. Ve a tu carpeta de evidencias de HUs")
    print("5. Tienes 120 segundos (2 minutos)")
    print("6. La sesión se guardará automáticamente")
    print()
    print("NOTA: NO necesitas cerrar tu Chrome actual")
    print()
    print("="*80)
    print()

    input("Presiona ENTER para abrir Chrome aislado...")

    # Configurar Chrome con perfil aislado
    chrome_options = get_chrome_options()

    print("\n🌐 Abriendo Chrome aislado...")
    print("   (Completamente separado de tu Chrome normal)")
    print()

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        print("✓ Chrome abierto exitosamente")
        print()

        # Navegar a Google primero (más seguro que ir directo a Drive)
        print("📂 Navegando a Google...")
        driver.get("https://www.google.com")
        time.sleep(2)

        print()
        print("="*80)
        print("⏰ TIEMPO PARA INICIAR SESIÓN")
        print("="*80)
        print()
        print("PASOS:")
        print("-"*80)
        print()
        print("1. En la barra de direcciones, ve a: https://drive.google.com")
        print("2. Inicia sesión con tu cuenta de Google")
        print("3. Navega a tu carpeta de evidencias de HUs")
        print("4. ESPERA hasta que termine el tiempo (NO cierres el navegador)")
        print()
        print("⏰ Tiempo disponible: 120 segundos (2 minutos)")
        print()
        print("-"*80)
        print()

        # Countdown de 120 segundos
        intervalos = [120, 90, 60, 45, 30, 15, 10, 5]
        tiempo_anterior = 120

        for tiempo in intervalos:
            print(f"   ⏳ {tiempo} segundos restantes...")
            espera = tiempo_anterior - tiempo
            time.sleep(espera)
            tiempo_anterior = tiempo

        # Últimos 5 segundos
        time.sleep(5)
        print(f"   ⏳ Tiempo terminado!")
        print()

        print("="*80)
        print("✅ SESIÓN GUARDADA")
        print("="*80)
        print()
        print("Tu sesión ha sido guardada en un perfil aislado.")
        print()
        print("IMPORTANTE:")
        print("-"*80)
        print("• Este perfil es INDEPENDIENTE de tu Chrome normal")
        print("• Los scripts de Drive usarán este perfil automáticamente")
        print("• Tu Chrome personal NO fue afectado")
        print()
        print("Ahora puedes ejecutar: 2_Completar_HU.bat")
        print()
        print("="*80)
        print()

        input("Presiona ENTER para cerrar Chrome...")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print()
        print("SOLUCIÓN:")
        print("-"*80)
        print()
        print("Si el error persiste:")
        print("  1. Ejecuta: LIMPIAR_PERFIL_CHROME.bat")
        print("  2. Vuelve a ejecutar este script")
        print()
        input("\nPresiona ENTER para salir...")
        return

    finally:
        try:
            driver.quit()
            print("\n✓ Navegador cerrado")
        except:
            pass

        print("\n✅ ¡Proceso completado!")
        print()
        print("RECUERDA: Tu Chrome normal NO fue afectado.")
        print()


if __name__ == "__main__":
    main()
