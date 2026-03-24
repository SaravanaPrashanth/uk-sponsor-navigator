with source as (
    select * from {{ source('raw_data', 'HOME_OFFICE_SPONSORS') }}
),
renamed as (
    select
        md5(cast(concat(coalesce(ORGANISATION_NAME, ''), coalesce(TOWN_CITY, '')) as varchar)) as sponsor_id,
        upper(trim(ORGANISATION_NAME)) as company_name,
        upper(trim(TOWN_CITY)) as city,
        coalesce(upper(trim(COUNTY)), 'NOT PROVIDED') as county,
        "TYPE_&_RATING" as visa_rating,
        ROUTE as visa_route,
        _INGESTED_AT as ingested_at
    from source
    WHERE ROUTE = 'Skilled Worker'
)

select * from renamed