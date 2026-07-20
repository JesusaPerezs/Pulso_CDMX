with fechas as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2010-01-01' as date)",
        end_date="cast('2027-01-01' as date)"
    ) }}
)

select
    {{ dbt_utils.generate_surrogate_key(['date_day']) }} as fecha_id,
    date_day as fecha,
    extract(year from date_day) as anio,
    extract(month from date_day) as mes,
    extract(day from date_day) as dia,
    extract(quarter from date_day) as trimestre,
    extract(dayofweek from date_day) as dia_semana,
    case when extract(dayofweek from date_day) in (1, 7) then true else false end as es_fin_semana
from fechas