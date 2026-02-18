-- dbt macro: cents_to_dollars.sql
-- Description: Converts a column from cents to dollars (or any currency's primary unit).

{% macro cents_to_dollars(column_name, precision=2) %}
    ({{ column_name }} / 100)::numeric(16, {{ precision }})
{% endmacro %}
