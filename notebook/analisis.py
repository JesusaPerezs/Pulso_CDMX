# %%
import pandas as pd


df_metro_desg = pd.read_parquet("metro_desg_limpia.parquet")
df_metro_simple = pd.read_parquet("metro_simp_limpia.parquet")

# region info
"""
print(f"Datos del metro desgrozado: {df_metro_desg.info()}")
print(f"Datos del metro simple: {df_metro_simple.info()}")
"""
# endregion

# %%
df_fecha_min_desg = df_metro_desg["fecha"].min()
df_fecha_max_desg = df_metro_desg["fecha"].max()
df_fecha_min_simple = df_metro_simple["fecha"].min()
df_fecha_max_simple = df_metro_simple["fecha"].max()


print(f"fecha maxima del metro desglozada: {df_fecha_max_desg}")
print(f"fecha minima del metro desglozada: {df_fecha_min_desg}")
print(f"fecha maxima del metro simple: {df_fecha_max_simple}")
print(f"fecha minima del metro simple: {df_fecha_min_simple}")

filtro_balbuena_des = df_metro_desg[(df_metro_desg["fecha"] == "2021-01-01") & (df_metro_desg["estacion"] == "Balbuena")] 
filtro_balbuena_sim = df_metro_simple[(df_metro_simple["fecha"] == "2021-01-01") & (df_metro_simple["estacion"] == "Balbuena")]

print(filtro_balbuena_des)
print(filtro_balbuena_sim)
"""
#endregion

# region fechas faltantes
"""
rango_fecha_desg = pd.date_range(start=df_fecha_min_desg, end=df_fecha_max_desg, freq="D")
rango_fecha_simp = pd.date_range(start=df_fecha_min_simple, end=df_fecha_max_simple, freq="D")

fecha_unica_desg = df_metro_desg["fecha"].unique()
fecha_unica_simp = df_metro_simple["fecha"].unique()

dias_faltantes_des = rango_fecha_desg.difference(fecha_unica_desg)
dias_faltantes_sim = rango_fecha_simp.difference(fecha_unica_simp)

if len(dias_faltantes_des) == 0:
    print(f"no hay días faltantes para base desglozada")
else:
    print(f"faltan: {len(dias_faltantes_des)} días en el dataset de desglozada")
    print("Los días que no aparecen son:")
    print(dias_faltantes_des)

if len(dias_faltantes_sim) == 0:
    print(f"no hay días faltantes para base simple")
else:
    print(f"faltan: {len(dias_faltantes_sim)} días en el dataset de simple")
    print("Los días que no aparecen son:")
    print(dias_faltantes_sim)
    """
#endregion

# region duplicados
"""
llave_desg = ["fecha", "linea", "estacion", "tipo_pago"]
llave_sim = ["fecha", "linea", "estacion",]

dups_reales_desg = df_metro_desg.duplicated(subset=llave_desg, keep=False)
dups_reales_simp = df_metro_simple.duplicated(subset=llave_sim, keep=False)

print(f"Datos duplicados de la base desglozada: {dups_reales_desg.sum()}")
print(f"Datos duplicados de la base simple: {dups_reales_simp.sum()}")
print(repr(df_metro_desg["linea"].iloc[0]))

dups = df_metro_simple[dups_reales_simp].sort_values(["fecha", "linea", "estacion"])
#dups.to_csv("duplicados.xlsx")
filtro_duplicados = df_metro_simple[(df_metro_simple["fecha"] == "2020-12-01") & (df_metro_simple["linea"] == "Linea B")]
#filtro_duplicados.to_csv("duplicado_desglozado.csv")
print(dups)

#endregion

# region validaciones 

# %%
dep_ocenia_sim = df_metro_simple[
    (df_metro_simple['linea'] == 'Linea B') & 
    (df_metro_simple['estacion'].str.contains('Deportivo', case=False, na=False)) & 
    (df_metro_simple['fecha'].dt.year == 2020) & 
    (df_metro_simple['fecha'].dt.month == 12)
    ]
print(f"Numero de registros de diciembre 2020 de la linea deportivo {len(dep_ocenia_sim)}")

filas_por_dia = df_metro_simple[
    (df_metro_simple["fecha"].dt.year == 2020) &
    (df_metro_simple["fecha"].dt.month == 12)
    ].groupby("fecha").size()

print(f"Conteo de filas por día de diciembre 2020 {len(filas_por_dia)}")

dep_ocenia_sim_enero = df_metro_simple[
    (df_metro_simple['linea'] == 'Linea B') & 
    (df_metro_simple['estacion'].str.contains('Deportivo', case=False, na=False)) & 
    (df_metro_simple['fecha'].dt.year == 2021) & 
    (df_metro_simple['fecha'].dt.month == 1)
    ]
print(f"Numero de registros de enero 2021 de la linea deportivo {len(dep_ocenia_sim_enero)}")

dep_ocenia_sim_nov = df_metro_simple[
    (df_metro_simple['linea'] == 'Linea B') & 
    (df_metro_simple['estacion'].str.contains('Deportivo', case=False, na=False)) & 
    (df_metro_simple['fecha'].dt.year == 2020) & 
    (df_metro_simple['fecha'].dt.month == 11)
    ]
print(f"Numero de registros de noviembre 2020 de la linea deportivo {len(dep_ocenia_sim_nov)}")

# %%
dep = df_metro_simple[df_metro_simple["estacion"].str.contains("Deportivo Oceanía", na=False)]
print(dep["fecha"].min(), dep["fecha"].max())

# ¿Qué valores de linea tiene Deportivo Oceanía en su historia?
print(dep["linea"].unique())


# ¿En qué meses exactamente falta o cambia?
print(dep.groupby([dep["fecha"].dt.year, dep["fecha"].dt.month]).size())
# %%

# 1. ¿Cuántas variantes de linea hay en toda la base?
print(df_metro_simple["linea"].unique())

# 2. ¿Cuándo cambia la convención? (¿hay una fecha de corte?)
print(df_metro_simple.groupby([df_metro_simple["fecha"].dt.year, "linea"]).size())

# 3. Re-corre duplicados DESPUÉS de normalizar linea, y compara contra 62

# %%
# Con acento
con_aciento_des = df_metro_desg[df_metro_desg["linea"].str.contains("í")]
sin_aciento_des = df_metro_desg[~df_metro_desg["linea"].str.contains("í")]
con_aciento_sim = df_metro_simple[df_metro_simple["linea"].str.contains("í")]
sin_aciento_sim = df_metro_simple[~df_metro_simple["linea"].str.contains("í")]

print(f"con aciento base desglosada: {con_aciento_des["fecha"].min()}, con aciento: {con_aciento_des['fecha'].max()}")
print(f"sin aciento base desglosada: {sin_aciento_des["fecha"].min()}, con aciento: {sin_aciento_des['fecha'].max()}")
print(f"con aciento base simple: {con_aciento_sim["fecha"].min()}, con aciento: {con_aciento_sim['fecha'].max()}")
print(f"sin aciento base simple: {sin_aciento_sim["fecha"].min()}, con aciento: {sin_aciento_sim['fecha'].max()}")

# %%

# Estaciones por día
estacion_por_día_des = (df_metro_desg.groupby("fecha")["estacion"].nunique().rename("n_estaciones").reset_index())
estacion_por_día_sim = (df_metro_simple.groupby("fecha")["estacion"].nunique().rename("n_estaciones").reset_index())

print(f"Estacines por día base desglozada: {estacion_por_día_des["n_estaciones"].describe()}")
print(f"Estacines por día base simple: {estacion_por_día_sim["n_estaciones"].describe()}")


# %%
filtro_sim = estacion_por_día_sim[estacion_por_día_sim["n_estaciones"] == 162]
print(f"total de días con 162 días: {len(filtro_sim)}")