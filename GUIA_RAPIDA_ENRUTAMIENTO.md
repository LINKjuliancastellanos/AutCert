# 🚀 Guía Rápida: Enrutamiento Dinámico

## En 3 Pasos Simples

### 1️⃣ El Script Detecta Dónde Está

```python
PROJECT_ROOT = Path(__file__).parent.resolve()
```

**Traducción:** "¿Dónde estoy yo (el script)?"

**Ejemplo:** Si el script está en `C:/Proyectos/AutCert/config_paths.py`
- Resultado: `PROJECT_ROOT = C:/Proyectos/AutCert`

---

### 2️⃣ Sube Un Nivel y Encuentra la Carpeta Hermana

```python
PARENT_DIR = PROJECT_ROOT.parent
DATA_ROOT = PARENT_DIR / "EntregaCerts"
```

**Traducción:** "Sube un nivel y busca la carpeta EntregaCerts"

**Ejemplo:** Si `PROJECT_ROOT = C:/Proyectos/AutCert`
- `PARENT_DIR = C:/Proyectos`
- `DATA_ROOT = C:/Proyectos/EntregaCerts`

---

### 3️⃣ Construye Todas las Rutas Desde Ahí

```python
CERTIFICACIONES_ROOT = DATA_ROOT / "Certificaciones"
PDF_ROOT = DATA_ROOT / "Certificaciones_PDF"
EVIDENCIAS_ROOT = DATA_ROOT / "Evidencias"
```

**Resultado:**
- `CERTIFICACIONES_ROOT = C:/Proyectos/EntregaCerts/Certificaciones`
- `PDF_ROOT = C:/Proyectos/EntregaCerts/Certificaciones_PDF`
- `EVIDENCIAS_ROOT = C:/Proyectos/EntregaCerts/Evidencias`

---

## 📍 Visualización

```
📂 C:/Proyectos/                          ← PARENT_DIR
│
├── 📂 EntregaCerts/                      ← DATA_ROOT = PARENT_DIR / "EntregaCerts"
│   ├── 📂 Certificaciones/               ← CERTIFICACIONES_ROOT = DATA_ROOT / "Certificaciones"
│   ├── 📂 Certificaciones_PDF/           ← PDF_ROOT = DATA_ROOT / "Certificaciones_PDF"
│   └── 📂 Evidencias/                    ← EVIDENCIAS_ROOT = DATA_ROOT / "Evidencias"
│
└── 📂 AutCert/                           ← PROJECT_ROOT = Path(__file__).parent
    ├── 📄 config_paths.py                ← __file__ (este archivo)
    ├── 📂 Modulos/
    ├── 📂 Assets/
    └── 📂 Logs/
```

---

## 🎯 La Magia del Operador `/`

En Python con `pathlib`, el operador `/` une rutas de forma inteligente:

```python
# Ejemplo 1: Construir ruta paso a paso
base = Path("C:/Proyectos")
datos = base / "EntregaCerts"
certs = datos / "Certificaciones"
ayn = certs / "AyN"

print(ayn)  # C:/Proyectos/EntregaCerts/Certificaciones/AyN

# Ejemplo 2: Todo en una línea
ruta = Path("C:/Proyectos") / "EntregaCerts" / "Certificaciones" / "AyN"
print(ruta)  # C:/Proyectos/EntregaCerts/Certificaciones/AyN
```

**¿Por qué es mágico?**
- Funciona en Windows (`\`), Linux (`/`) y Mac (`/`) automáticamente
- No hay que preocuparse por los separadores
- Es más legible que usar `os.path.join()`

---

## 🔄 Ejemplo Completo Paso a Paso

### Escenario: Ejecutas un script en Windows

```python
# Paso 1: Python detecta dónde está el archivo
__file__ = "C:/Users/Julian/Documentos/AutCert/config_paths.py"

# Paso 2: Convierte a Path y obtiene el directorio
PROJECT_ROOT = Path(__file__).parent.resolve()
# PROJECT_ROOT = Path("C:/Users/Julian/Documentos/AutCert")

# Paso 3: Sube un nivel
PARENT_DIR = PROJECT_ROOT.parent
# PARENT_DIR = Path("C:/Users/Julian/Documentos")

# Paso 4: Define la carpeta de datos
DATA_ROOT = PARENT_DIR / "EntregaCerts"
# DATA_ROOT = Path("C:/Users/Julian/Documentos/EntregaCerts")

# Paso 5: Construye las rutas finales
CERTIFICACIONES_ROOT = DATA_ROOT / "Certificaciones"
# CERTIFICACIONES_ROOT = Path("C:/Users/Julian/Documentos/EntregaCerts/Certificaciones")

PDF_ROOT = DATA_ROOT / "Certificaciones_PDF"
# PDF_ROOT = Path("C:/Users/Julian/Documentos/EntregaCerts/Certificaciones_PDF")

EVIDENCIAS_ROOT = DATA_ROOT / "Evidencias"
# EVIDENCIAS_ROOT = Path("C:/Users/Julian/Documentos/EntregaCerts/Evidencias")
```

---

## 🌐 Mismo Código, Diferentes PCs

### PC 1: Julian (Windows)
```
C:/Users/Julian/Documentos/
├── EntregaCerts/
│   ├── Certificaciones/      ← Ruta final: C:/Users/Julian/Documentos/EntregaCerts/Certificaciones
│   ├── Certificaciones_PDF/
│   └── Evidencias/
└── AutCert/
    └── config_paths.py       ← __file__ está aquí
```

### PC 2: María (Windows, otro disco)
```
D:/Trabajo/MisProyectos/
├── EntregaCerts/
│   ├── Certificaciones/      ← Ruta final: D:/Trabajo/MisProyectos/EntregaCerts/Certificaciones
│   ├── Certificaciones_PDF/
│   └── Evidencias/
└── AutCert/
    └── config_paths.py       ← __file__ está aquí
```

### PC 3: Pedro (Linux)
```
/home/pedro/proyectos/
├── EntregaCerts/
│   ├── Certificaciones/      ← Ruta final: /home/pedro/proyectos/EntregaCerts/Certificaciones
│   ├── Certificaciones_PDF/
│   └── Evidencias/
└── AutCert/
    └── config_paths.py       ← __file__ está aquí
```

**El código es EXACTAMENTE el mismo** en los 3 PCs. Las rutas se adaptan automáticamente.

---

## 💡 Analogía del Mundo Real

Imagina que eres un cartero:

### ❌ Rutas Hardcodeadas (Mal)
```
"Entregar en: Calle Falsa 123, Springfield"
```
- Solo funciona si el destinatario vive en esa dirección exacta
- Si se muda, la dirección deja de funcionar

### ✅ Rutas Dinámicas (Bien)
```
"Entregar a: Juan Pérez"
1. Buscar dónde vive Juan Pérez (detectar ubicación)
2. Ir a su casa (calcular ruta)
3. Entregar el paquete
```
- Funciona sin importar dónde viva Juan
- Si se muda, el cartero lo encuentra en la nueva ubicación

---

## 🎓 Términos Clave

### `__file__`
- Variable especial de Python
- Contiene la ruta del archivo .py que se está ejecutando
- Ejemplo: `"C:/Proyectos/AutCert/config_paths.py"`

### `Path()`
- Clase de Python para manejar rutas
- Más moderna y poderosa que strings
- Funciona en Windows, Linux y Mac

### `.parent`
- Propiedad que sube un nivel en la ruta
- Ejemplo: `Path("C:/a/b/c").parent` → `"C:/a/b"`

### `.resolve()`
- Convierte rutas relativas en absolutas
- Ejemplo: `Path("../carpeta").resolve()` → `"C:/ruta/completa/carpeta"`

---

## ✅ Checklist de Instalación

Cuando copies el proyecto a un nuevo PC:

- [ ] Copiar la carpeta `AutCert` completa
- [ ] Colocarla en cualquier ubicación
- [ ] Ejecutar cualquier script
- [ ] La carpeta `EntregaCerts` se crea automáticamente al lado
- [ ] ¡Listo! Todo funciona sin configuración

**No necesitas:**
- ❌ Editar archivos de configuración
- ❌ Cambiar rutas manualmente
- ❌ Preocuparte por qué usuario está ejecutando
- ❌ Crear carpetas manualmente

---

## 🎬 Demo en Código

```python
# Este es el ÚNICO código que necesitas para rutas dinámicas:

from pathlib import Path

# Detectar ubicación del proyecto
PROJECT_ROOT = Path(__file__).parent.resolve()

# Calcular carpeta de datos
DATA_ROOT = PROJECT_ROOT.parent / "EntregaCerts"

# Usar las rutas
certificaciones = DATA_ROOT / "Certificaciones"
print(f"Las certificaciones están en: {certificaciones}")

# Crear carpetas si no existen
certificaciones.mkdir(parents=True, exist_ok=True)
```

**¡Eso es todo!** Solo 3 líneas de lógica:
1. Detectar dónde está el código
2. Calcular dónde están los datos
3. Usar las rutas

---

## 📞 ¿Dudas?

Si algo no funciona:

1. **Verifica la estructura de carpetas:**
   ```
   ¿Tienes esto?
   - Alguna carpeta/
     ├── EntregaCerts/
     └── AutCert/
   ```

2. **Ejecuta un test:**
   ```bash
   python -c "from config_paths import *; print(f'Datos en: {DATA_ROOT}')"
   ```

3. **Revisa el archivo de inicialización:**
   - La primera vez que se ejecuta, se crea: `EntregaCerts/.inicializado`
   - Esto confirma que la carpeta se creó correctamente

---

**¡Eso es todo!** Con este sistema, tu código es 100% portable entre cualquier PC. 🎉
