/*
STAGING: Customers Cleaning & Standardization
*/



with source as (
    select * from {{ source('raw', 'CUSTOMERS') }}
),
cleaned as (
    select
        upper(trim(CUSTOMER_ID::STRING)) as customer_id,
        initcap(trim(CUSTOMER_NAME::STRING)) as customer_name,
        lower(trim(EMAIL::STRING)) as email_raw,
        initcap(trim(CITY::STRING)) as city,
        upper(trim(STATE::STRING)) as state,
        coalesce(CREATED_DATE::TIMESTAMP_NTZ, current_timestamp) as created_date,
        CURRENT_TIMESTAMP as dbt_loaded_at
    from source
    where CUSTOMER_ID is not null
),
validated as (
    select
        customer_id,
        customer_name,
        case
            when regexp_like(email_raw, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') then email_raw
            else concat(replace(lower(customer_id), ' ', ''), '@portfolio-company.com')
        end as email,
        nullif(city, '') as city,
        nullif(state, '') as state,
        created_date,
        dbt_loaded_at
    from cleaned
),
deduplicated as (
    select *
    from validated
    qualify row_number() over (
        partition by customer_id
        order by created_date desc, dbt_loaded_at desc
    ) = 1
)
select * from deduplicated
