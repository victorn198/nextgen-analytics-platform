/*
STAGING: Current customer state from native Snowflake SCD2 snapshot.
*/

with source as (
    select * from {{ source('snapshots_native', 'CUSTOMERS_SCD2_CURRENT') }}
),
renamed as (
    select
        CUSTOMER_ID::STRING as customer_id,
        CUSTOMER_NAME::STRING as customer_name,
        EMAIL::STRING as email,
        CITY::STRING as city,
        STATE::STRING as state,
        CREATED_DATE::TIMESTAMP_NTZ as created_date,
        VALID_FROM::TIMESTAMP_NTZ as snapshot_valid_from,
        UPDATED_AT::TIMESTAMP_NTZ as snapshot_updated_at,
        LOAD_TS::TIMESTAMP_NTZ as snapshot_loaded_at,
        current_timestamp as dbt_loaded_at
    from source
)
select * from renamed
