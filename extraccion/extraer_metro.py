import requests
import pandas as pd
import logging

# El log te dice cuándo (timestamp), qué tan grave (INFO), y de dónde (__main__).
# logging puede escribir a un archivo .log que queda guardado.
# logging es escribir en una bitácora — queda anotado con hora y firma, y cualquiera lo lee después.

logging.basicConfig(level=logging.INFO) # configura el SISTEMA de logs
logger = logging.getLogger(__name__)    # crea TU logger personal

UUID_SIMPLE = "0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb"

COLUMNAS_ESPERADAS = {"fecha", "anio", "mes", "linea", "estacion", "afluencia"}

ARCHIVO_SALIDA = "metro_simple_raw.csv"

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

def main():
    response = requests.get(url, params=params)
    # raise_for_status: Revisa el código HTTP de la respuesta.
    response.raise_for_status()
    package_data = response.json()
    recursos = package_data["result"]["resources"]
    
    recurso = encontrar_recurso(recursos, UUID_SIMPLE)
    validar_recurso(recurso)
    logger.info("Recurso encontrado: %s", recurso["name"])

    url_descarga = recurso["url"]
    resp = requests.get(url_descarga)
    logger.info("Descargando %s...", url_descarga)
    resp.raise_for_status()
    
    with open(ARCHIVO_SALIDA, "wb") as f: # write binary (wb)
        f.write(resp.content)
    
    # Sin ningún encoding, pandas asume UTF-8 por defecto, Latin-1 acepta cualquier byte sin quejarse.
    df = pd.read_csv(ARCHIVO_SALIDA, encoding="latin-1")
    if set(df.columns) != COLUMNAS_ESPERADAS:
        raise ValueError(f"Esquema inesperado. Llegaron: {set(df.columns)}")
    logger.info("Descarga y validación completa")
    
# ejecuta main() solo si me están corriendo directamente, no si me están importando
if __name__ == "__main__": main()