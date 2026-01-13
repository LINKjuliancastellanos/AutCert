# 📹 Módulo: Copiar Videos de Evidencias

## 📋 Descripción

Este módulo permite copiar videos de evidencias desde carpetas externas (como las de Linktic/Asignaciones) hacia la estructura organizada en `EntregaCerts/Evidencias`.

**Incluye dos modos de operación:**
- **Modo Individual**: Procesa una HU a la vez
- **Modo Masivo**: Procesa múltiples HUs automáticamente

## 🚀 Inicio Rápido

### Archivos Ejecutables

En la raíz del proyecto (`AutCert/`):
- 🔵 **`copiar_videos.bat`** - Modo Individual (una HU)
- 🟢 **`copiar_videos_masivo.bat`** - Modo Masivo (múltiples HUs)

**Simplemente haz doble clic en el archivo `.bat` que necesites!**

### Scripts Python

Si prefieres ejecutar desde terminal:
```bash
# Modo Individual
python Modulos/Copiar_Videos/copiar_videos_evidencias.py

# Modo Masivo
python Modulos/Copiar_Videos/copiar_videos_masivo.py
```

## 🎯 Funcionalidades

- ✅ Detecta automáticamente el número de HU desde el nombre de la carpeta
- ✅ Identifica la categoría (AyN, RyC, Transversal) desde la ruta
- ✅ Copia videos organizados en carpetas CP
- ✅ Soporta múltiples formatos: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`, `.wmv`, `.m4v`
- ✅ Evita duplicados (compara tamaños)
- ✅ Mantiene la estructura organizada de EntregaCerts
- ✅ Genera log detallado de operaciones
- ✅ **[NUEVO] Modo masivo**: Procesa todas las HUs de una carpeta base automáticamente

## 📁 Estructura Esperada

### Carpeta de Origen (Ejemplo)

```
C:/Users/Julian/Linktic/Asignaciones/Evidencias/AyN/Evidencias HU83509/
├── CP123456/
│   ├── evidencia1.mp4
│   └── evidencia2.mp4
├── CP123457/
│   └── video_test.mp4
└── CP123458/
    └── grabacion.mp4
```

### Carpeta de Destino (Automática)

```
EntregaCerts/Evidencias/AyN/HU83509/
├── CP123456/
│   ├── evidencia1.mp4
│   └── evidencia2.mp4
├── CP123457/
│   └── video_test.mp4
└── CP123458/
    └── grabacion.mp4
```

## 🚀 Uso

Este módulo tiene **DOS MODOS** de operación:

---

## 🔵 MODO INDIVIDUAL - Procesar una HU

### Uso Rápido (Recomendado)

**Ejecuta el `.bat` desde la raíz del proyecto:**
- Haz doble clic en: `copiar_videos.bat`

**O ejecuta desde terminal:**
```bash
python Modulos/Copiar_Videos/copiar_videos_evidencias.py
```

### Paso 2: Proporcionar la Ruta

El script te pedirá la ruta de la carpeta con los videos:

```
Ingresa la ruta completa de la carpeta con los videos.
Ejemplo: C:\Users\Julian\Linktic\Evidencias\AyN\Evidencias HU83509

Ruta de la carpeta: [PEGA AQUÍ LA RUTA]
```

### Paso 3: Verificación Automática

El script detectará automáticamente:
- **Número de HU**: Extrae "83509" de "Evidencias HU83509"
- **Categoría**: Detecta "AyN" si está en la ruta

Si no puede detectar algo, te lo preguntará.

### Paso 4: Confirmación

Te mostrará un resumen antes de copiar:

```
Videos encontrados:
  Carpetas CP: 3
  Total de videos: 5
  Tamaño total: 245.3 MB

Carpeta de destino:
  C:/Users/Julian/Documents/EntregaCerts/Evidencias/AyN/HU83509

¿Proceder con la copia? (S/N):
```

### Paso 5: Resultado

```
COPIA COMPLETADA

Resultados:
  Copiados nuevos:  5
  Ya existían:      0
  Sobrescritos:     0
  Errores:          0
  Total procesados: 5
```

---

## 🟢 MODO MASIVO - Procesar múltiples HUs

**¡NUEVO!** Este modo procesa automáticamente TODAS las HUs que encuentre en una carpeta base.

### Uso Rápido (Recomendado)

**Ejecuta el `.bat` masivo:**
- Haz doble clic en: `copiar_videos_masivo.bat`

**O ejecuta desde terminal:**
```bash
python Modulos/Copiar_Videos/copiar_videos_masivo.py
```

### Flujo del Modo Masivo

#### Paso 1: Proporcionar Ruta Base

Le pasas la ruta de la carpeta que contiene múltiples HUs:

```
Ruta de la carpeta base: C:\Users\Julian\Linktic\Asignaciones\Evidencias
```

#### Paso 2: Escaneo Automático

El script busca **recursivamente** todas las carpetas que contengan HUs:

```
Escaneando carpetas de HU...

HUs encontradas: 15
```

#### Paso 3: Verificación de Categorías

Si alguna HU no tiene categoría detectada automáticamente, te pregunta:

```
No se pudo detectar la categoría para HU83509

Opciones:
  1. AyN (Afiliaciones y Novedades)
  2. RyC (Recaudo y Cartera)
  3. Transversal
  S. Saltar esta HU

Categoría para HU83509 (1/2/3/S): _
```

#### Paso 4: Resumen Completo

Te muestra un resumen detallado por categoría:

```
Resumen de videos encontrados

AyN:
  HUs:    8
  CPs:    45
  Videos: 120
  Tamaño: 1.2 GB

RyC:
  HUs:    5
  CPs:    28
  Videos: 75
  Tamaño: 850.5 MB

Transversal:
  HUs:    2
  CPs:    12
  Videos: 30
  Tamaño: 320.8 MB

TOTAL:
  HUs:    15
  CPs:    85
  Videos: 225
  Tamaño: 2.3 GB

¿Proceder con la copia masiva? (S/N): _
```

#### Paso 5: Copia Masiva

Procesa todas las HUs automáticamente con resumen por cada una:

```
COPIANDO VIDEOS...

HU83509 (AyN):
  CP123456 (2 videos): 2 copiados
  CP123457 (1 video): 1 copiado

HU83510 (AyN):
  CP123458 (3 videos): 3 copiados

HU83511 (RyC):
  CP123459 (1 video): 1 existía
  CP123460 (2 videos): 2 copiados

...

COPIA MASIVA COMPLETADA

Resultados totales:
  Copiados nuevos:  210
  Ya existían:      12
  Sobrescritos:     3
  Errores:          0
  Total procesados: 225

Estadísticas por categoría:
  AyN: 120 videos en 8 HUs
  RyC: 75 videos en 5 HUs
  Transversal: 30 videos en 2 HUs
```

### Estructura Base Esperada para Modo Masivo

```
Linktic/Asignaciones/Evidencias/
├── AyN/
│   ├── Evidencias HU83509/
│   │   ├── CP123456/
│   │   │   ├── video1.mp4
│   │   │   └── video2.mp4
│   │   └── CP123457/
│   │       └── video3.mp4
│   └── Evidencias HU83510/
│       └── CP123458/
│           └── video4.mp4
├── RyC/
│   └── Evidencias HU83511/
│       └── CP123459/
│           └── video5.mp4
└── Transversal/
    └── Evidencias HU83512/
        └── CP123460/
            └── video6.mp4
```

### Resultado del Modo Masivo

Todos los videos se copian a su ubicación correspondiente:

```
EntregaCerts/Evidencias/
├── AyN/
│   ├── HU83509/
│   │   ├── CP123456/
│   │   │   ├── video1.mp4
│   │   │   └── video2.mp4
│   │   └── CP123457/
│   │       └── video3.mp4
│   └── HU83510/
│       └── CP123458/
│           └── video4.mp4
├── RyC/
│   └── HU83511/
│       └── CP123459/
│           └── video5.mp4
└── Transversal/
    └── HU83512/
        └── CP123460/
            └── video6.mp4
```

---

## 🔄 ¿Cuándo usar cada modo?

### 🔵 Usa MODO INDIVIDUAL cuando:
- Tienes una sola HU para procesar
- Quieres copiar videos de una HU específica
- Necesitas control detallado sobre una HU particular
- Ejemplo: `C:\Linktic\Evidencias\AyN\Evidencias HU83509`

### 🟢 Usa MODO MASIVO cuando:
- Tienes múltiples HUs para procesar
- Quieres copiar todos los videos de una carpeta de una sola vez
- Trabajas con exportaciones completas de Linktic
- Ejemplo: `C:\Linktic\Evidencias` (procesa todas las HUs dentro)

**💡 Tip:** El modo masivo ahorra mucho tiempo cuando tienes 10+ HUs para procesar.

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Ruta de Linktic (Modo Individual)

```
Ruta: C:\Users\Julian\OneDrive\Documents\Linktic\Asignaciones\Evidencias\AyN\Evidencias HU83509

Resultado:
- HU detectada: 83509
- Categoría: AyN (detectada automáticamente)
- Destino: EntregaCerts/Evidencias/AyN/HU83509/
```

### Ejemplo 2: Ruta Sin Categoría

```
Ruta: D:\Proyectos\Videos\HU83510

Resultado:
- HU detectada: 83510
- Categoría: Te preguntará (AyN/RyC/Transversal)
- Destino: EntregaCerts/Evidencias/{Categoria}/HU83510/
```

### Ejemplo 3: Múltiples CPs (Modo Individual)

```
Carpeta de origen:
  Evidencias HU83509/
    ├── CP123456/ (2 videos)
    ├── CP123457/ (1 video)
    ├── CP123458/ (3 videos)
    └── CP123459/ (1 video)

Resultado: 7 videos copiados a sus respectivas carpetas CP
```

### Ejemplo 4: Carpeta Base con Múltiples HUs (Modo Masivo)

```
Ruta: C:\Users\Julian\Linktic\Asignaciones\Evidencias

Estructura encontrada:
  Evidencias/
    ├── AyN/
    │   ├── Evidencias HU83509/ (12 videos en 5 CPs)
    │   ├── Evidencias HU83510/ (8 videos en 3 CPs)
    │   └── Evidencias HU83511/ (15 videos en 7 CPs)
    ├── RyC/
    │   ├── Evidencias HU83512/ (6 videos en 2 CPs)
    │   └── Evidencias HU83513/ (10 videos en 4 CPs)
    └── Transversal/
        └── Evidencias HU83514/ (4 videos en 2 CPs)

Resultado:
- 6 HUs procesadas automáticamente
- 23 CPs totales
- 55 videos copiados en una sola operación
- Tiempo: ~30 segundos

Destino:
  EntregaCerts/Evidencias/
    ├── AyN/HU83509/, HU83510/, HU83511/
    ├── RyC/HU83512/, HU83513/
    └── Transversal/HU83514/
```

### Ejemplo 5: Carpeta Mixta Sin Categorías (Modo Masivo)

```
Ruta: D:\Evidencias_Sprint_15

Estructura encontrada:
  Evidencias_Sprint_15/
    ├── HU83515/ (sin categoría en la ruta)
    ├── HU83516/ (sin categoría en la ruta)
    └── HU83517/ (sin categoría en la ruta)

El script te preguntará por cada HU:

  No se pudo detectar la categoría para HU83515
  Categoría para HU83515 (1/2/3/S): 1

  No se pudo detectar la categoría para HU83516
  Categoría para HU83516 (1/2/3/S): 1

  No se pudo detectar la categoría para HU83517
  Categoría para HU83517 (1/2/3/S): 2

Resultado:
- HU83515 → EntregaCerts/Evidencias/AyN/HU83515/
- HU83516 → EntregaCerts/Evidencias/AyN/HU83516/
- HU83517 → EntregaCerts/Evidencias/RyC/HU83517/
```

## 🔍 Detección Automática

### Número de HU

El script busca patrones como:
- `Evidencias HU83509` → HU: 83509
- `HU 83509` → HU: 83509
- `evidencias_hu_83509` → HU: 83509
- `83509` (solo números de 5+ dígitos) → HU: 83509

### Número de CP

El script busca patrones como:
- `CP123456` → CP: 123456
- `TC123456` → CP: 123456 (alias de Test Case)
- `cp_123456` → CP: 123456

### Categoría

El script busca en la ruta:
- Si contiene `/AyN/` → Categoría: AyN
- Si contiene `/RyC/` → Categoría: RyC
- Si contiene `/Transversal/` → Categoría: Transversal

## ⚙️ Configuración

### Formatos de Video Soportados

Por defecto, soporta:
- `.mp4` (más común)
- `.avi`
- `.mov`
- `.mkv`
- `.webm`
- `.flv`
- `.wmv`
- `.m4v`

### Manejo de Duplicados

Si el archivo ya existe en el destino:
- Compara tamaños
- Si son iguales: **No sobrescribe** (marca como "Ya existe")
- Si son diferentes: **Sobrescribe** (marca como "Sobrescrito")

## 📊 Log de Operaciones

Ambos modos generan logs detallados:

### Modo Individual
```
AutCert/Logs/copiar_videos.log
```

Ejemplo de log individual:
```
[2026-01-13 14:30:15] INICIO DE COPIA DE VIDEOS
[2026-01-13 14:30:15] Carpeta de origen: C:/Users/Julian/Linktic/.../HU83509
[2026-01-13 14:30:15] HU detectada: 83509
[2026-01-13 14:30:15] Categoría: AyN
[2026-01-13 14:30:15] Videos encontrados: 5 en 3 CPs
[2026-01-13 14:30:20] Procesando CP123456 con 2 videos
[2026-01-13 14:30:20]   evidencia1.mp4: Copiado exitosamente
[2026-01-13 14:30:21]   evidencia2.mp4: Copiado exitosamente
...
[2026-01-13 14:30:25] RESUMEN: 5 copiados, 0 existían, 0 sobrescritos, 0 errores
[2026-01-13 14:30:25] FIN DE COPIA DE VIDEOS
```

### Modo Masivo
```
AutCert/Logs/copiar_videos_masivo.log
```

Ejemplo de log masivo:
```
[2026-01-13 15:00:00] INICIO DE COPIA MASIVA DE VIDEOS
[2026-01-13 15:00:00] Carpeta base: C:/Users/Julian/Linktic/Evidencias
[2026-01-13 15:00:05] Total: 6 HUs, 23 CPs, 55 videos, 1.2 GB
[2026-01-13 15:00:10] Procesando HU83509 (AyN)
[2026-01-13 15:00:10]   CP123456: 2 videos
[2026-01-13 15:00:10]     video1.mp4: Copiado
[2026-01-13 15:00:11]     video2.mp4: Copiado
[2026-01-13 15:00:15] Procesando HU83510 (AyN)
...
[2026-01-13 15:00:45] RESUMEN: 50 copiados, 5 existían, 0 sobrescritos, 0 errores
[2026-01-13 15:00:45] Procesadas: 6 HUs con 55 videos
[2026-01-13 15:00:45] FIN DE COPIA MASIVA DE VIDEOS
```

## 🛡️ Seguridad

- ✅ **No elimina archivos** de la carpeta origen (solo copia)
- ✅ **Crea carpetas automáticamente** si no existen
- ✅ **Preserva metadatos** del archivo (fecha, etc.)
- ✅ **Validación de rutas** antes de copiar
- ✅ **Confirmación del usuario** antes de proceder

## ⚠️ Consideraciones

1. **Espacio en disco**: Verifica que tengas suficiente espacio antes de copiar videos grandes
2. **Permisos**: Asegúrate de tener permisos de lectura en origen y escritura en destino
3. **Nombres de archivo**: Se preservan los nombres originales de los archivos
4. **Estructura de carpetas**: Debe seguir el patrón `CP{numero}/video.ext`

## 🔧 Solución de Problemas

### Error: "La carpeta no existe"

**Causa**: La ruta proporcionada no existe o está mal escrita

**Solución**:
1. Verifica que la ruta sea correcta
2. Usa comillas si la ruta tiene espacios
3. Puedes copiar la ruta desde el explorador de archivos

### Error: "No se encontraron videos en carpetas CP"

**Causa**: La estructura de carpetas no coincide con lo esperado

**Solución**:
1. Verifica que los videos estén dentro de carpetas llamadas `CP{numero}`
2. Ejemplo correcto:
   ```
   HU83509/
     └── CP123456/
         └── video.mp4
   ```
3. Ejemplo incorrecto:
   ```
   HU83509/
     └── video.mp4  (video suelto, no en carpeta CP)
   ```

### Error: "No se pudo detectar automáticamente el número de HU"

**Causa**: El nombre de la carpeta no contiene "HU" seguido de números

**Solución**:
1. El script te pedirá ingresar el número manualmente
2. Ingresa solo el número (ej: `83509`)

## 📚 Flujo Completo de Trabajo

1. **Capturar evidencias** con `capturar_evidencia_masivo.py`
   - Guarda screenshots en `EntregaCerts/Evidencias/`

2. **Grabar videos** externamente (ej: OBS, Zoom)
   - Guardar en carpeta organizada por CP

3. **Copiar videos** con `copiar_videos_evidencias.py`
   - Copia videos a `EntregaCerts/Evidencias/` junto a screenshots

4. **Resultado**: Evidencias completas (screenshots + videos) organizadas por CP

---

**Última actualización**: 2026-01-13
**Versión**: 1.0
