with fuente as (
    select * 
    from {{ source('raw', 'metro_desglosada_raw') }}
),

limpio as (
    select
        fecha,
        anio,
        mes,
        -- Normaliza mojibake: 'LÃ­nea X' -> 'Linea X'
        replace(linea, 'LÃ­nea', 'Linea') as linea,
        replace(replace(replace(replace(replace(replace(replace(
        estacion,
        'Miguel Ã ngel', 'Miguel Ángel'),
        'Ã­', 'í'),
        'Ã¡', 'á'),
        'Ã³', 'ó'),
        'Ã©', 'é'),
        'Ã±', 'ñ'),
        'Ãº', 'ú') as estacion,
        tipo_pago,
        afluencia
    from fuente
),
marcado as (
    select *,
        'ok' as calidad_dato
        from limpio
)

select * from marcado