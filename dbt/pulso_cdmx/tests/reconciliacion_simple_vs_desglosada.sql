-- Test de reconciliación: la suma de afluencia de la Desglosada (por tipo de pago)
-- debe igualar la afluencia de la Simple, para cada fecha-linea-estacion en el traslape.
-- Devuelve las combinaciones donde NO cuadran (si hay alguna, el test falla).

with desglosada_sumada as (
    select
        fecha_id,
        linea_id,
        estacion_id,
        sum(afluencia) as total_desglosada
    from {{ ref('fact_afluencia_tipo_pago') }}
    group by fecha_id, linea_id, estacion_id
),

simple as (
    select
        fecha_id,
        linea_id,
        estacion_id,
        afluencia as total_simple
    from {{ ref('fact_afluencia_diaria') }}
)

select
    s.fecha_id,
    s.linea_id,
    s.estacion_id,
    s.total_simple,
    d.total_desglosada
from simple s
inner join desglosada_sumada d
    on s.fecha_id = d.fecha_id
    and s.linea_id = d.linea_id
    and s.estacion_id = d.estacion_id
where s.total_simple != d.total_desglosada