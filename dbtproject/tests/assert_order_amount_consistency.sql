-- Fails when order totals diverge from quantity * unit_price.

select
    order_id,
    quantity,
    unit_price,
    total_amount
from {{ ref('stg_orders') }}
where abs(total_amount - round(quantity * unit_price, 2)) > 0.01
