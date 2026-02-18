/*
STAGING: Orders Cleaning & Standardization
*/



with source as (
    select * from {{ source('raw', 'ORDERS') }}
),
cleaned as (
    select
        upper(trim(ORDER_ID::STRING)) as order_id,
        upper(trim(CUSTOMER_ID::STRING)) as customer_id,
        upper(trim(PRODUCT_ID::STRING)) as product_id,
        try_to_timestamp_ntz(ORDER_DATE::STRING) as order_date,
        QUANTITY::NUMBER(38, 0) as quantity_raw,
        UNIT_PRICE::NUMBER(10, 2) as unit_price_raw,
        TOTAL_AMOUNT::NUMBER(10, 2) as total_amount_raw,
        lower(trim(STATUS::STRING)) as status_raw,
        CURRENT_TIMESTAMP as dbt_loaded_at
    from source
    where ORDER_ID is not null
),
validated as (
    select
        order_id,
        customer_id,
        product_id,
        least(coalesce(order_date, current_timestamp), current_timestamp) as order_date,
        coalesce(quantity_raw, 0)::NUMBER(38,0) as quantity,
        coalesce(unit_price_raw, 0)::NUMBER(10,2) as unit_price,
        round(coalesce(quantity_raw, 0) * coalesce(unit_price_raw, 0), 2)::NUMBER(10,2) as total_amount,
        case
            when status_raw in ('pending','paid','cancelled','shipped','completed') then status_raw
            when status_raw in ('canceled') then 'cancelled'
            else 'pending'
        end as status,
        dbt_loaded_at,
        case
            when coalesce(quantity_raw, 0) <= 0 then 'invalid_quantity'
            when coalesce(unit_price_raw, 0) <= 0 then 'invalid_unit_price'
            when customer_id is null or customer_id = '' then 'invalid_customer'
            when product_id is null or product_id = '' then 'invalid_product'
            else 'valid'
        end as data_quality_flag
    from cleaned
    where least(coalesce(order_date, current_timestamp), current_timestamp) >= to_timestamp_ntz('2023-01-01')
),
deduplicated as (
    select *
    from validated
    qualify row_number() over (
        partition by order_id
        order by order_date desc, dbt_loaded_at desc
    ) = 1
)
select *
from deduplicated
where data_quality_flag = 'valid'
