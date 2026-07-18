import pandas as pd
import ftfy
import pyarrow
import fastparquet

df_metro_desg = pd.read_csv("afluenciastc_metro_desglosado_05_2026.csv", encoding="utf-8")
df_metro_simple = pd.read_csv("afluenciastc_metro_simple_05_2026.csv", encoding="latin-1")

df_metro_desg["fecha"] = pd.to_datetime(df_metro_desg["fecha"])
df_metro_simple["fecha"] = pd.to_datetime(df_metro_simple["fecha"])

def reparar_texto(df, columnas):
    for col in columnas:
        mapa = {v: ftfy.fix_text(v) for v in df[col].unique()}
        df[col] = df[col].map(mapa)
    return df

df_metro_desg = reparar_texto(df_metro_desg, ["linea", "estacion"])
df_metro_simple = reparar_texto(df_metro_simple, ["linea", "estacion"])

df_metro_desg.to_parquet("metro_desg_limpia.parquet")
df_metro_simple.to_parquet("metro_simp_limpia.parquet")

print(repr(df_metro_desg["estacion"].unique()[:10]))
print(repr(df_metro_simple["estacion"].unique()[:10]))
print("Archivos limpios generados")

print(df_metro_desg.head(10))
print("___________________________")
print(df_metro_simple.head(10))

