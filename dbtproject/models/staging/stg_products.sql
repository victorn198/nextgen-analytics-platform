/*
STAGING: Products Cleaning & Standardization
*/



with source as (
    select * from {{ source('raw', 'PRODUCTS') }}
),
cleaned as (
    select
        upper(trim(PRODUCT_ID::STRING)) as product_id,
        trim(PRODUCT_NAME::STRING) as product_name,
        coalesce(nullif(trim(CATEGORY::STRING), ''), 'uncategorized') as category,
        UNIT_PRICE::NUMBER(10, 2) as price_raw,
        STOCK_QUANTITY::NUMBER(38, 0) as stock_quantity_raw,
        CURRENT_TIMESTAMP as dbt_loaded_at
    from source
    where PRODUCT_ID is not null
),
validated as (
    select
        product_id,
        iff(product_name is null or product_name = '', concat('Unknown Product ', product_id), product_name) as product_name,
        category,
        coalesce(price_raw, 0)::NUMBER(10,2) as price,
        greatest(coalesce(stock_quantity_raw, 0), 0)::NUMBER(38,0) as stock_quantity,
        dbt_loaded_at
    from cleaned
),
deduplicated as (
    select *
    from validated
    qualify row_number() over (
        partition by product_id
        order by dbt_loaded_at desc
    ) = 1
)
select * from deduplicated
where price > 0
