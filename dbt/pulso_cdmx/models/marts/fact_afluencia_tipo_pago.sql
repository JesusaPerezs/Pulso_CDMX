with staging as (
    select * from {{ ref('stg_metro_desglosada')}}
),

fact as (
    select
        f.fecha_id,
        l.linea_id,
        e.estacion_id,
        s.afluencia,
        s.calidad_dato,
        s.tipo_pago
    from staging s
    left join {{ref('dim_fecha') }} f
        on s.fecha = f.fecha
    left join {{ref('dim_linea') }} l
        on s.linea = l.linea
    left join {{ ref('dim_estacion') }} e
        on s.estacion = e.estacion and s.linea = e.linea
)

select * from fact