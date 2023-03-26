{{
    config(
        materialized='incremental'
		, schema='analytics'
    )
}}

SELECT 	name AS forecast_name,
		forecast_timestamp,	
		CAST(EXTRACT(epoch FROM (forecast_timestamp - forecast_approved_timestamp)/(60*60)) AS INT) AS hours_diff,
		forecast_value,
		forecast_unit,
		created_timestamp_utc ,
		NOW() AS dbt_timestamp_utc 
FROM staging.forecasts
	JOIN staging.forecast_name_codes
	ON forecast_code = code


{% if is_incremental() %}
WHERE created_timestamp_utc > (SELECT MAX(created_timestamp_utc) FROM {{ this }})
{% endif %}
