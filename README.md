# Exportaciones Brasileñas de los 4 Principales Productos Agro

**Análisis de Datos, Ofimática e Instrumentos Visuales para la Gerencia — EQUIPO 03**

Dashboard ejecutivo e informe en Excel sobre las exportaciones de Brasil de sus cuatro
principales productos agropecuarios: **Soja, Milho, Café en granos y Algodón**, a partir de
los datos de exportación de los años **2025 y 2026 según el Gobierno Federal de Brasil 
Ministério do Desenvolvimento, Indústria, Comércio e Serviços 
https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta**.

---

## 1. Objetivo

Conocer el uso de herramientas ofimáticas ejecutivas (Excel), el análisis de datos y los
instrumentos visuales interactivos (Streamlit) orientados a la alta gerencia, aplicado a un
caso real de comercio exterior.

**Productos analizados y sus códigos NCM (Nomenclatura Comum do Mercosul en portugués):**

| Producto        | Códigos NCM                             |
|-----------------|-----------------------------------------|
| Soja            | 12010010, 12010090, 12011000, 12019000  |
| Milho           | 10051000, 10059010, 10059090            |
| Café en granos  | 09011110, 09011190, 09011200            |
| Algodón         | 52010010, 52010020, 52010090, 52030000  |

> Los códigos se normalizan a 8 dígitos con ceros a la izquierda (p. ej. `9011110` → `09011110`).

---

## 2. Fuentes de datos

| Archivo         | Contenido                                         | Filas     |
|-----------------|---------------------------------------------------|-----------|
| `EXP_2025.csv`  | Exportaciones brasileñas 2025 (sep `;`, latin-1)  | 1.709.746 |
| `EXP_2026.csv`  | Exportaciones brasileñas 2026                     | 1.272.295 |
| `PAIS.csv`      | Catálogo de países (CO_PAIS, ISO, nombres)        | 281       |
| `UF.csv`        | Catálogo de estados/UF y regiones de Brasil       | 34        |

Columnas de los archivos de exportación: `CO_ANO, CO_MES, CO_NCM, CO_UNID, CO_PAIS,
SG_UF_NCM, CO_VIA, CO_URF, QT_ESTAT, KG_LIQUIDO, VL_FOB`.

---

## 3. Estructura del proyecto

```
.
├── crear_excel.py                # Genera el libro Excel con pandas + openpyxl (no se suben al repo)
├── ejemplo_analisis_datos.xlsx   # Libro Excel resultante (6 hojas + tablas)
├── dashboard.py                  # Aplicación Streamlit (KPIs, gráficos y mapa)
├── br_states.geojson             # Fronteras de los 27 estados (propiedad "sigla")
├── requirements.txt              # Dependencias para el deploy
├── .gitignore                    # Excluye datos pesados (CSV de exportación, dbs/)
├── README.md
├── EXP_2025.csv / EXP_2026.csv   (fuente, no se suben al repo)
├── PAIS.csv / UF.csv             (fuente)
```

---

## 4. Proceso desarrollado paso a paso

### Paso 1 — Crear el archivo Excel
Se generó `ejemplo_analisis_datos.xlsx` con `crear_excel.py` usando **pandas** para la
lectura/limpieza y **openpyxl** para escribir hojas, tablas y fórmulas, por ser parte
de una ETL se descartar en el repositorio.

### Paso 2 — Pestaña `paises`
`PAIS.csv` se cargó como una hoja de Excel con nombre **`paises`**.

### Paso 3 — Pestaña `Base`
Se filtraron las filas de `EXP_2025.csv` y `EXP_2026.csv` cuyo campo clave `CO_NCM` coincide con
los NCM del diccionario `productos`, generando **17.986 filas**. Cada fila se enriqueció con
el nombre del producto. Columnas: `CO_ANO, CO_MES, CO_NCM, CO_PAIS, SG_UF_NCM, QT_ESTAT,
KG_LIQUIDO, VL_FOB, Producto`, son parte del original de la fuente de datos.

### Paso 4 — Relación para filtros interactivos
La hoja `Base` es la tabla matriz y se relaciona con las hojas excel:
- `paises` (por `CO_PAIS`)
- `productos` (por `CO_NCM`)
- `estados` (por `SG_UF_NCM`)

Estas relaciones permiten filtrar/segmentar por producto, país y estado/región.

### Paso 5 — Funciones de Excel
En la hoja `Base` y en la hoja `Formulas` se usan funciones nativas de Excel:

| Función     | Uso                                                                         |
|-------------|-----------------------------------------------------------------------------|
| `BUSCARV`   | Trae `Pais`, `Producto`, `Estado` y `Region` a la tabla `Base`              |
| `BUSCARX`   | Consultas por **nombre** (de producto, país y estado) en la hoja `Formulas` |
| `SI`        | Clasificación por rango de valor FOB (Alto/Medio/Bajo) y por totales        |
| `SI.ERROR`  | Manejo de no encontrados ("Sin dato")                                       |
| `SUMAR.SI`  | Totales de `VL_FOB` por producto, país y región                             |

> Compatibilidad: todas son funciones nativas de Excel (no requieren LibreOffice).
> `BUSCARX` requiere Excel 2019 / Microsoft 365.

### Paso 6 — Dashboard Streamlit
`dashboard.py` lee la hoja `Base` del Excel y genera gráficos interactivos con
**Plotly**, filtrables por producto, país, año y región:

- Valor FOB por producto (barras)
- Top países destino
- Evolución mensual del valor FOB
- Participación por producto (pastel)
- Treemap producto → país
- **Mapa coroplético por estado de Brasil** (origen de las exportaciones)
- Ranking de estados y mezcla de productos
- Valor FOB y composición por región de Brasil

### Paso 7 — KPIs
Se incluyen 8 indicadores clave en el panel superior:
Valor FOB total, Volumen total (kg), Países destino, Operaciones, Producto líder,
País líder, Participación 2026 y Variación 2026 vs 2025.

---

## 5. Cifras destacadas del período (2025–2026)

- **Valor FOB total:** US$ 131.969 millones
- **Volumen total:** 278.057.290.879 kg
- **Países destino:** 155

| Producto        | Valor FOB (US$) |
|-----------------|-----------------|
| Soja            | 86.431.550.289  |
| Café en granos  | 24.029.770.065  |
| Milho           | 13.009.528.766  |
| Algodón         | 8.498.603.831   |

**Regiones de origen (Valor FOB):** Centro Oeste (US$ 55.558 M), Sudeste (33.788 M),
Sur (18.237 M), Nordeste (13.244 M), Norte (10.067 M).

**Estados líderes:** Mato Grosso (MT), Minas Gerais (MG), Goiás (GO), Paraná (PR), São Paulo (SP).

---

## 6. Estructura del libro Excel

| Hoja        | Contenido                                                                 | Tabla           |
|-------------|---------------------------------------------------------------------------|-----------------|
| `Portada`   | Título, subtítulo y contenido del libro                                   | —               |
| `paises`    | Catálogo de países                                                        | `TablaPaises`   |
| `estados`   | Catálogo de UF y regiones de Brasil                                       | `TablaEstados`  |
| `productos` | Relación NCM → producto                                                   | `TablaProductos`|
| `Base`      | Exportaciones filtradas y relacionadas                                    | `TablaBase`     |
| `Formulas`  | Consultas por nombre (`BUSCARX`), totales `SUMAR.SI` y clasificación `SI` | —               |

El libro tiene activado el **recálculo completo al abrir**, de modo que todas las fórmulas
se calculan al abrirlo en Excel.

---

## 7. Ejecución local en Windows (DOS o PowerShell)

```bash
# 1. Crear entorno e instalar dependencias
python -m venv .venv
.venv/bin/activate
pip install -r requirements.txt

# 2. (Opcional) Regenerar el Excel a partir de los CSV fuente
python crear_excel.py

# 3. Levantar el dashboard
streamlit run dashboard.py
```

El dashboard abre en tu navegador en el url `http://localhost:8501`.

---

## 8. Pasos para el deploy en Streamlit Community Cloud

**Requisitos previos:** cuenta de GitHub y cuenta en https://share.streamlit.io

### 8.1 Preparar el repositorio

```bash
git init
git add dashboard.py crear_excel.py requirements.txt .gitignore \
        ejemplo_analisis_datos.xlsx br_states.geojson README.md
git commit -m "Dashboard exportaciones brasileras de los 4 productos agro"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```

> El `.gitignore` excluye los CSV de exportación (~113 MB y ~84 MB) y las bases DuckDB.
> El dashboard solo necesita `ejemplo_analisis_datos.xlsx` (1,2 MB) y `br_states.geojson`
> (3,3 MB), por lo que el repositorio queda liviano.

### 8.2 Desplegar

1. Ingresar a https://share.streamlit.io con GitHub.
2. Clic en **Create app** → **Deploy a public app from GitHub**.
3. Seleccionar el repositorio, la rama `main` y *Main file path*: `dashboard.py`.
4. En **Advanced settings**, elegir Python 3.12 (opcional) y pulsar **Deploy**.
5. Streamlit instala las dependencias de `requirements.txt` y publica la URL de la app.

### 8.3 Notas de deploy
- Las rutas a `ejemplo_analisis_datos.xlsx` y `br_states.geojson` son relativas y deben
  quedar en la raíz del repositorio.
- No es necesario subir los CSV fuente ni el entorno virtual `.venv/`.
- Para actualizar datos, regenerar el Excel y hacer `git add/commit/push`: la app se
  redespliega automáticamente.

---

## 9. Tecnologías utilizadas

- **Python 3.13.1**
- **pandas**      — lectura, limpieza y transformación de datos
- **openpyxl**    — escritura del libro Excel, tablas y fórmulas
- **Streamlit**   — aplicación web interactiva
- **Plotly**      — visualizaciones interactivas y mapa coroplético
- **Excel**       — funciones `BUSCARV`, `BUSCARX`, `SI`, `SI.ERROR`, `SUMAR.SI`
