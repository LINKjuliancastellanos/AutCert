# Sistema de Automatizacion de Certificaciones QA - AutCert

Sistema automatizado para generar certificaciones QA en Excel, capturar evidencias, y gestionar el flujo completo de documentacion de testing.

---

## Descripcion

Este sistema automatiza el proceso completo de certificaciones QA:

1. **Analisis de datos** - Estadisticas y reportes del CSV
2. **Generacion de certificaciones** - Excel prellenado por Historia de Usuario
3. **Creacion de carpetas de evidencias** - Estructura organizada por modulo
4. **Captura de evidencias** - Screenshots automaticos desde Azure DevOps
5. **Renombrado de evidencias** - Nombres descriptivos segun Test Case
6. **Extraccion de links Drive** - Links de carpetas de evidencias
7. **Conversion a PDF** - Certificaciones Excel a PDF optimizado
8. **Control de ejecucion** - Reporte consolidado de estado

---

## Estructura del Proyecto

```
AutCert/
|
|-- Assets/
|   |-- Base de datos/
|   |   |-- data.csv                    # Datos exportados de Azure DevOps
|   |   +-- missing_testcases.csv       # TCs faltantes
|   +-- Formatos/
|       +-- Formato Oficial.xlsx        # Plantilla de certificacion
|
|-- Modulos/
|   |
|   |-- Certificaciones/                # Generacion de certificaciones
|   |   |-- crear_certificacion.py      # Modo individual
|   |   |-- crear_certificacion_masivo.py
|   |   |-- test_validacion.py
|   |   |-- Crear_Certificacion.bat
|   |   +-- Crear_Certificaciones_Masivo.bat
|   |
|   |-- Analisis/                       # Analisis de datos
|   |   |-- analizar_datos.py
|   |   +-- Analizar_Datos.bat
|   |
|   |-- Evidencias_Azure/               # Captura de evidencias
|   |   |-- scripts/
|   |   |   |-- configuracion_evidencias.py
|   |   |   |-- iniciar_sesion_azure.py
|   |   |   |-- capturar_evidencia_single.py
|   |   |   |-- capturar_evidencia_hu.py
|   |   |   +-- capturar_evidencia_masivo.py
|   |   |-- 1_Iniciar_Sesion.bat
|   |   |-- 2_Capturar_Single.bat
|   |   |-- 3_Capturar_HU.bat
|   |   +-- 4_Capturar_Masivo.bat
|   |
|   |-- Links_Drive/                    # Extraccion de links
|   |   |-- scripts/
|   |   |   |-- configuracion_drive.py
|   |   |   |-- iniciar_sesion_drive.py
|   |   |   +-- completar_certificacion_interactivo.py
|   |   |-- 1_Iniciar_Sesion.bat
|   |   +-- 2_Completar_HU.bat
|   |
|   |-- Renombrado/                     # Renombrar evidencias
|   |   |-- renombrar_evidencias.py
|   |   +-- Renombrar_Evidencias.bat
|   |
|   |-- Conversion_PDF/                 # Conversion a PDF
|   |   |-- convertir_a_pdf.py
|   |   +-- Convertir_a_PDF.bat
|   |
|   +-- Control_Ejecucion/              # Control de ejecucion
|       |-- generar_control.py
|       +-- Generar_Control.bat
|
|-- Certificaciones/                    # Certificaciones Excel generadas
|   |-- AyN/
|   |-- RyC/
|   +-- Transversal/
|
|-- Certificaciones_PDF/                # Certificaciones PDF generadas
|   |-- AyN/
|   |-- RyC/
|   +-- Transversal/
|
|-- Evidencias/                         # Carpetas de evidencias
|   |-- AyN/
|   |   +-- HU{id}/
|   |       +-- CP{tc_id}/
|   |-- RyC/
|   +-- Transversal/
|
|-- Logs/                               # Logs de ejecucion
|
|-- config_paths.py                     # Configuracion centralizada de rutas
+-- README.md
```

---

## Requisitos

### Python
- Python 3.8 o superior
- Microsoft Excel instalado (para generacion de certificaciones y PDF)

### Dependencias Python
```bash
pip install selenium webdriver-manager pandas pywin32
```

### Otros
- Google Chrome instalado (para captura de evidencias)

---

## Instalacion

### 1. Preparar archivos

1. Colocar el CSV exportado de Azure DevOps en:
   ```
   Assets\Base de datos\data.csv
   ```

2. Verificar que existe la plantilla Excel en:
   ```
   Assets\Formatos\Formato Oficial.xlsx
   ```

### 2. Instalar dependencias Python

```bash
pip install selenium webdriver-manager pandas pywin32
```

---

## Flujo de Trabajo

### Paso 1: Analisis de datos (opcional)
```
Modulos\Analisis\Analizar_Datos.bat
```
Genera estadisticas del CSV: HUs por tester, por modulo, calidad de datos.

### Paso 2: Generacion de certificaciones
```
Modulos\Certificaciones\Crear_Certificacion.bat           # Una HU
Modulos\Certificaciones\Crear_Certificaciones_Masivo.bat  # Multiples HUs
```
Genera Excel prellenado y carpetas de evidencias.

### Paso 3: Captura de evidencias
```
Modulos\Evidencias_Azure\1_Iniciar_Sesion.bat   # Primera vez (login Azure)
Modulos\Evidencias_Azure\2_Capturar_Single.bat  # Un TC
Modulos\Evidencias_Azure\3_Capturar_HU.bat      # Todos los TCs de una HU
Modulos\Evidencias_Azure\4_Capturar_Masivo.bat  # Todas las HUs
```

### Paso 4: Renombrar evidencias
```
Modulos\Renombrado\Renombrar_Evidencias.bat
```
Aplica nombres descriptivos a los screenshots.

### Paso 5: Links de Drive
```
Modulos\Links_Drive\1_Iniciar_Sesion.bat  # Primera vez (login Drive)
Modulos\Links_Drive\2_Completar_HU.bat    # Completar certificacion con links
```

### Paso 6: Conversion a PDF
```
Modulos\Conversion_PDF\Convertir_a_PDF.bat
```
Convierte certificaciones Excel a PDF con:
- Columnas ajustadas al ancho de pagina
- Sin filas vacias
- Orientacion vertical
- Centrado horizontal

### Paso 7: Control de ejecucion (opcional)
```
Modulos\Control_Ejecucion\Generar_Control.bat
```
Genera reporte consolidado del estado de certificaciones.

---

## Modulos Disponibles

| Modulo | Ubicacion | Funcion |
|--------|-----------|---------|
| Certificaciones | Modulos/Certificaciones/ | Generar Excel y carpetas |
| Analisis | Modulos/Analisis/ | Estadisticas y reportes |
| Evidencias_Azure | Modulos/Evidencias_Azure/ | Captura screenshots |
| Links_Drive | Modulos/Links_Drive/ | Extraccion links Drive |
| Renombrado | Modulos/Renombrado/ | Renombrar evidencias |
| Conversion_PDF | Modulos/Conversion_PDF/ | Excel a PDF |
| Control_Ejecucion | Modulos/Control_Ejecucion/ | Reporte de estado |

---

## Nomenclatura

### Certificaciones
```
Certificaciones/{Modulo}/Certificacion_QA_{HU_ID}.xlsx
Certificaciones_PDF/{Modulo}/Certificacion_QA_{HU_ID}.pdf
```

### Evidencias
```
Evidencias/{Modulo}/HU{id}/CP{tc_id}/
```

Ejemplo:
```
Evidencias/AyN/HU100895/CP104946/
```

---

## Formato del CSV

| Columna | Descripcion |
|---------|-------------|
| ID | ID del work item (numerico) |
| Title | Titulo (contiene HU o CP) |
| Work Item Type | "User Story" o "Test Case" |
| Tester | Nombre del tester |
| Iteration Path | Sprint |
| Modulo Balu | Modulo funcional |
| Aprobador QA | Nombre y email del aprobador |

### Modulos validos:
- `Afiliaciones y Novedades` -> AyN
- `Recaudo y Cartera` -> RyC
- `Transversal` -> Transversal

---

## Solucion de Problemas

| Problema | Solucion |
|----------|----------|
| CSV no encontrado | Verificar ruta en Assets/Base de datos/ |
| Excel en uso | Cerrar archivo antes de ejecutar |
| Chrome no inicia | Verificar instalacion de Chrome |
| Selenium falla | Ejecutar 1_Iniciar_Sesion.bat primero |
| PDF no genera | Verificar que Excel no este abierto |

### Forzar cierre de Excel
```bash
taskkill /f /im excel.exe
```

---

## Configuracion

Todas las rutas estan centralizadas en `config_paths.py`. El sistema detecta automaticamente la ubicacion del proyecto.

---

## Autor

Sistema desarrollado para automatizacion de certificaciones QA.
