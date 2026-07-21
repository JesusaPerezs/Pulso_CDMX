# Pulso CDMX 🚇

**ES** · Pipeline de datos de extremo a extremo (ELT) que ingesta, modela y sirve la afluencia diaria del Metro de la Ciudad de México sobre Google Cloud Platform.

**EN** · End-to-end data pipeline (ELT) that ingests, models and serves the daily ridership of the Mexico City Metro on Google Cloud Platform.

---

## 🧭 Resumen / Overview

**ES** · Pulso CDMX toma datos públicos de afluencia del Metro (más de 15 años, ~2.3 millones de registros entre dos fuentes) desde el portal de datos abiertos de la CDMX y los convierte en un almacén de datos analítico, limpio y consultable, expuesto a través de una API REST. El proyecto implementa un flujo ELT moderno con extracción automatizada, un data lake, un warehouse modelado en esquema estrella, pruebas de calidad de datos, CI/CD sin llaves y una capa de servicio.

**EN** · Pulso CDMX takes public Metro ridership data (15+ years, ~2.3M records across two sources) from Mexico City's open data portal and turns it into a clean, queryable analytical warehouse, exposed through a REST API. The project implements a modern ELT flow with automated extraction, a data lake, a star-schema warehouse, data quality tests, keyless CI/CD, and a serving layer.

---

## 🏗️ Arquitectura / Architecture

```
Portal Datos Abiertos CDMX (API CKAN)
        │
        ▼
Extracción · Python           →  descubre recursos vía API, valida esquema, logging
        │
        ▼
Cloud Storage (data lake)     →  CSV crudos, capa raw inmutable
        │
        ▼
BigQuery · raw                →  espejo crudo de los CSV
        │
        ▼
dbt · transformación          →  staging (limpieza) → marts (modelo estrella)
        │                        28 tests + reconciliación cruzada
        ▼
API de consumo · FastAPI      →  endpoints REST, JSON

        ⟲ CI/CD: GitHub Actions + Workload Identity Federation (keyless)
```

![Arquitectura del pipeline](pulso_cdmx_pipeline_architecture.png)

---

## 🛠️ Stack

| Categoría / Category | Tecnologías / Technologies |
|---|---|
| Lenguajes / Languages | Python, SQL |
| Cloud | Google Cloud Platform (Cloud Storage, BigQuery, IAM) |
| Transformación / Transformation | dbt (dbt-core, dbt-bigquery, dbt_utils) |
| API | FastAPI, Uvicorn |
| CI/CD | GitHub Actions, Workload Identity Federation |
| Extracción / Extraction | requests, CKAN API |
| Control de versiones / Version control | Git, GitHub |

---

## 📦 Componentes / Components

### 1. Extracción / Extraction (`extraccion/`)

**ES** · Script en Python que descarga los CSV de afluencia sin intervención manual:
- Descubre las URLs de descarga dinámicamente vía la **API de CKAN** (usa el UUID del recurso como ancla estable, no la URL que cambia cada mes).
- Valida el formato y el esquema de columnas antes de subir.
- Sube a Cloud Storage con autenticación **ADC** (sin archivos de llave).
- Diseño parametrizado (`FUENTES` dict): agregar Metrobús o RTP es una entrada más en el diccionario.
- `logging`, manejo de errores, `main()` con guarda `if __name__`.

**EN** · Python script that downloads the ridership CSVs with no manual intervention: dynamic resource discovery via the CKAN API (UUID as stable anchor), schema validation before upload, keyless auth (ADC), and a parametrized design (`FUENTES` dict) so adding new transit sources is a one-line change.

### 2. Data lake + Warehouse (GCS + BigQuery)

**ES** · El lake (Cloud Storage) guarda los CSV crudos como **evidencia inmutable**; el warehouse (BigQuery) guarda las tablas modeladas. Separarlos permite reprocesar desde el origen sin volver a extraer. Lake y warehouse co-ubicados en `us-west1` para evitar costos de transferencia.

**EN** · The lake stores raw CSVs as immutable evidence; the warehouse stores modeled tables. Separation enables reprocessing from source without re-extraction. Co-located in `us-west1` to avoid transfer costs.

### 3. Transformación / Transformation (`dbt/`)

**ES** · Modelo por capas siguiendo la metodología Kimball:
- **staging** — repara la calidad de datos (ver tabla abajo) y normaliza.
- **marts** — modelo estrella con **dimensiones conformadas** (`dim_fecha`, `dim_linea`, `dim_estacion`) y **dos tablas de hechos** (`fact_afluencia_diaria`, `fact_afluencia_tipo_pago`) por sus granos distintos.
- Surrogate keys generadas con `dbt_utils`.

**EN** · Layered model (Kimball): staging cleans and normalizes; marts is a star schema with conformed dimensions and two fact tables (distinct grains). Surrogate keys via `dbt_utils`.

### 4. Calidad de datos / Data quality

**ES** · 27 tests genéricos (`unique`, `not_null`, `relationships`, `accepted_values`) + 1 test custom de **reconciliación cruzada**: verifica que la suma de la afluencia desglosada por tipo de pago iguale la afluencia total, para cada fecha-línea-estación en el traslape 2021-2026.

**EN** · 27 generic tests + 1 custom cross-reconciliation test verifying that the sum of ridership by payment type equals the total, for every date-line-station in the 2021-2026 overlap.

### 5. CI/CD (`.github/workflows/`)

**ES** · GitHub Actions corre `dbt build` (modelos + tests) en cada push y pull request. Autenticación mediante **Workload Identity Federation** — sin llaves JSON almacenadas, siguiendo la práctica de seguridad moderna.

**EN** · GitHub Actions runs `dbt build` on every push and PR. Auth via Workload Identity Federation — no stored JSON keys, following modern security practice.

### 6. API de consumo / Serving API (`api/`)

**ES** · API REST con FastAPI que sirve los datos del modelo estrella como JSON, con documentación interactiva automática en `/docs`. Conexión a BigQuery vía ADC, permisos de solo lectura (privilegio mínimo).

**EN** · FastAPI REST API serving star-schema data as JSON, with auto-generated interactive docs at `/docs`. BigQuery connection via ADC, read-only permissions (least privilege).

---

## 🔍 Hallazgos de calidad de datos / Data quality findings

**ES** · El perfilado reveló cinco problemas documentados en la fuente. Cada uno se resuelve en la capa correspondiente:

| Problema / Problem | Evidencia / Evidence | Impacto / Impact | Resuelto en / Resolved in |
|---|---|---|---|
| **Mojibake de doble capa** | `LÃ­nea`, `OceanÃ­a`, `CatÃ³lica` en ambas bases | JOINs fallan; `dim_estacion` se duplica | staging (reemplazos SQL) |
| **Nomenclatura inconsistente en `linea`** | 24 variantes para 12 líneas; isla acentuada 2021-01→2023-05; corte de proceso el 2023-06-01 en ambas bases | `dim_linea` tendría 24 filas; series de tiempo se rompen | staging (canonización) |
| **Mislabeling dic-2020** | Deportivo Oceanía publicada como "Oceanía"; 31 días con 162 estaciones; 62 filas afectadas | Doble conteo en Oceanía | staging (bandera `calidad_dato`) + test `unique` |
| **Granos distintos entre fuentes** | Simple: fecha-línea-estación · Desglosada: +tipo_pago | Un solo hecho no puede vivir en una tabla sin fingir un grano | marts (dos facts) |
| **Actualizaciones retroactivas** | El portal advierte que datos históricos pueden cambiar | Carga incremental ingenua desactualiza el histórico | Fase 2 (merge/upsert) |

**Decisión destacada / Notable decision** — El mislabeling de diciembre 2020 **no era reparable con confianza**: los rangos de afluencia de Oceanía y Deportivo Oceanía se solapan (5625 vs 7310 promedio, rangos 2735-7295 y 4743-9491), así que asignar cada fila sería inventar datos. En vez de eliminar o adivinar, las 62 filas se **marcan** con una bandera de calidad — el consumidor decide si las incluye. *No borrar, marcar.*

---

## 🧩 Decisiones de diseño / Design decisions

**ES**
- **Dos tablas de hechos, no una** — los granos distintos (con/sin tipo de pago) justifican dos facts con dimensiones conformadas, en vez de una fact con un grano fingido o `tipo_pago = 'N/D'` antes de 2021.
- **`tipo_pago` como atributo directo, no dimensión** — baja cardinalidad (3 valores) sin atributos derivados; una dimensión sería sobre-ingeniería.
- **Raw como espejo crudo** — la capa raw preserva el mojibake; la limpieza vive en staging. Raw es evidencia, no producto.
- **CI/CD sin llaves (WIF)** — más seguro que almacenar una llave JSON en secrets, y es la práctica de producción real.

**EN** · Two fact tables for distinct grains; `tipo_pago` as a direct attribute (low cardinality); raw kept as an untouched mirror; keyless CI/CD via WIF.

---

## 🚀 Cómo ejecutar / How to run

```bash
# 1. Extracción / Extraction
cd extraccion
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
gcloud auth application-default login
python extraer_metro.py

# 2. Transformación / Transformation
cd dbt/pulso_cdmx
python -m venv venv-dbt && venv-dbt\Scripts\activate   # Python 3.13
pip install dbt-bigquery
dbt deps
dbt build          # corre modelos + tests / runs models + tests
dbt docs generate && dbt docs serve   # documentación con linaje

# 3. API
cd api
pip install -r requirements.txt
uvicorn api:app --reload
# → http://127.0.0.1:8000/docs
```

## 📊 Fuente de datos / Data source

[Portal de Datos Abiertos de la CDMX](https://datos.cdmx.gob.mx/dataset/afluencia-diaria-del-metro-cdmx) — Afluencia diaria del Metro (API CKAN).

---

*Autor / Author: Jesús Pérez · [github.com/JesusaPerezs/Pulso_CDMX](https://github.com/JesusaPerezs/Pulso_CDMX)*
