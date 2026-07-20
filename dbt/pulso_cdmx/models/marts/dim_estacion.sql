with estaciones as (
    select distinct
        estacion,
        linea
    from {{ ref('stg_metro_simple') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['estacion', 'linea']) }} as estacion_id,
    estacion,
    linea
from estaciones
order by estacion, linea