with lineas as (
    select distinct linea
    from {{ ref('stg_metro_simple')}}
)

select
    {{ dbt_utils.generate_surrogate_key(['linea']) }} as linea_id,
    linea
from lineas
order by linea