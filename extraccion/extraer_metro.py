import requests
import pandas as pd
import logging
from google.cloud import storage

# El log te dice cuándo (timestamp), qué tan grave (INFO), y de dónde (__main__).
# logging puede escribir a un archivo .log que queda guardado.
# logging es escribir en una bitácora — queda anotado con hora y firma, y cualquiera lo lee después.

logging.basicConfig(level=logging.INFO) # configura el SISTEMA de logs
logger = logging.getLogger(__name__)    # crea TU logger personal

FUENTES = {
    "simple":{
        "uuid": "0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb",
        "salida": "metro_simple_raw.csv",
        "columnas" : {"fecha", "anio", "mes", "linea", "estacion", "afluencia"},
    },
    "desglosada": {
        "uuid" : "cce544e1-dc6b-42b4-bc27-0d8e6eb3ed72",
        "salida": "metro_desglosada_raw.csv",
        "columnas": {"fecha", "anio", "mes", "linea", "estacion", "afluencia", "tipo_pago"}
    },
}

# Un bucket es como una carpeta raíz en Drive — un contenedor con nombre único.
BUCKET = "pulso-cdmx-raw-jesus"

def encontrar_recurso(recursos, uuid):
    # next(...) significa: "dame el primero que salga de ese generador"
    # None: "si el generador no entrega nada (ningún recurso empató), devuelve None en vez de tronar"
    recurso = next((r for r in recursos if r["id"] == uuid), None)
    if recurso is None:
        raise ValueError(f"No se encontró el recurso {uuid}")
    return recurso

def validar_recurso(recurso):
    if recurso["format"].upper() != "CSV":
        raise ValueError(f"Se esperaba CSV, llegó {recurso["format"]}")

url = "https://datos.cdmx.gob.mx/api/3/action/package_show"
params = {"id": "afluencia-diaria-del-metro-cdmx"}

def extraer(fuente):
    response = requests.get(url, params=params)
    # raise_for_status: Revisa el código HTTP de la respuesta.
    response.raise_for_status()
    package_data = response.json()
    recursos = package_data["result"]["resources"]
    
    recurso = encontrar_recurso(recursos, fuente["uuid"])
    validar_recurso(recurso)
    logger.info("Recurso encontrado: %s", recurso["name"])

    url_descarga = recurso["url"]
    resp = requests.get(url_descarga)
    logger.info("Descargando %s...", url_descarga)
    resp.raise_for_status()
    
    with open(fuente["salida"], "wb") as f: # write binary (wb)
        f.write(resp.content)
    
    # Sin ningún encoding, pandas asume UTF-8 por defecto, Latin-1 acepta cualquier byte sin quejarse.
    df = pd.read_csv(fuente["salida"], encoding="latin-1")
    if set(df.columns) != fuente["columnas"]:
        raise ValueError(f"Esquema inesperado. Llegaron: {set(df.columns)}")
    logger.info("Descarga y validación completa")
    subir_a_gcs(resp.content, fuente["salida"])

def main():
    for nombre, fuente in FUENTES.items():
        logger.info("Procesando fuente: %s", nombre)
        extraer(fuente)

def subir_a_gcs(contenido, nombre_destino):
    """sube bytes a un objeto en el bucket de GCS"""
    # Abre la conexión con Google Cloud Storage. storage.Client() es tu "teléfono" a GCS.
    client = storage.Client() # (1) abres Drive
    # Le dice al cliente cuál bucket quieres usar, por nombre. esto no sube nada todavía, solo apunta al bucket.
    bucket = client.bucket(BUCKET) # (2) eliges la carpeta
    # voy a poner un archivo llamado X en esta carpeta". Todavía no existe — solo estás nombrando el espacio donde va a vivir.
    blob = bucket.blob(nombre_destino) # (3) nombras el archivo
    # Toma contenido (los bytes de tu CSV, que vienen de resp.content) y los sube al blob. 
    blob.upload_from_string(contenido) # (4) subes los datos
    # Deja el rastro en el log. Ese gs:// es la forma en que Google nombra rutas en Storage
    logger.info("Subido a gs://%s/%s", BUCKET, nombre_destino)

# ejecuta main() solo si me están corriendo directamente, no si me están importando
if __name__ == "__main__": main()