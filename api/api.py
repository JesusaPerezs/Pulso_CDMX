from fastapi import FastAPI
from google.cloud import bigquery

app = FastAPI(title = "API de metro CDMX")

client = bigquery.Client(project="pulso-cdmx")

@app.get("/")
def healt():
    return {"Status": "API corriendo correctamente"}

@app.get("/datos_metro")
def get_marts_data():
    query = """
        SELECT b.estacion, b.linea, a.afluencia, a.tipo_pago
        FROM `pulso-cdmx.dbt_jesus.fact_afluencia_tipo_pago` a
        JOIN `pulso-cdmx.dbt_jesus.dim_estacion` b
            ON a.estacion_id = b.estacion_id
        ORDER BY b.estacion, b.linea
        LIMIT 20
        """
    
    query_job = client.query(query)
    result = query_job.result()

    data = [dict(row) for row in result]

    return {
        "total_filas": len(data),
        "data": data
    }