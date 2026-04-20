with stg as (
    select * from {{ ref('stg_sponsors') }}
),
final as (
select
    sponsor_id,
    company_name,
    city,
    county,
    CASE 
        WHEN visa_rating LIKE '%(A rating)%' then 'A'
        WHEN visa_rating LIKE '%(B rating)%' then 'B'
        ELSE 'Other'
    END AS rating_score,
    CASE
        WHEN company_name LIKE '%SOFTWARE%' or company_name LIKE '%TECH%' THEN 'Technology'
        WHEN company_name LIKE '%HEALTH%' or company_name LIKE '%CARE%' or company_name LIKE '%NHS%' THEN 'Healthcare'
        WHEN company_name LIKE '%SOLUTIONS%' or company_name LIKE '%CONSULT%' THEN 'Consulting/Services'
        ELSE 'Other / General'
    END AS estimated_industry,
    visa_route,
    CASE 
        WHEN city in ('SHEFFIELD', 'ROTHERHAM', 'BARNSLEY', 'DONCASTER') THEN 'South Yorkshire'
        WHEN city in ('LEEDS', 'MANCHESTER', 'LIVERPOOL') THEN 'Northern Hubs'
        WHEN city = 'LONDON' THEN 'London'
        ELSE 'Rest of UK'
    END AS geographic_priority,
    ingested_at
from stg
)

select * from final
qualify row_number() OVER(PARTITION BY company_name, city ORDER BY ingested_at DESC)= 1