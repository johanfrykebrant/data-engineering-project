{{
    config(
        materialized='incremental'
		, schema='analytics'
		, unique_key= 'forecast_timestamp'
		, incremental_strategy='delete+insert'
    )
}}

WITH 	temperature_forecasts AS (
			SELECT 	forecast_timestamp,
					forecast_value, 
					created_timestamp_utc
			FROM staging.forecasts
				JOIN staging.forecast_name_codes
				ON forecast_code = code
			WHERE name = 'Air temperature')
		,ranked_forecasts AS (
			SELECT 	forecast_timestamp, 
					forecast_value,
					created_timestamp_utc,
					RANK() OVER (PARTITION BY forecast_timestamp 
								 ORDER BY created_timestamp_utc DESC) 
					AS w
			FROM temperature_forecasts)


SELECT 	forecast_timestamp, 
		forecast_value,
		created_timestamp_utc
FROM ranked_forecasts
WHERE w = 1
{% if is_incremental() %}
	AND created_timestamp_utc > (SELECT MAX(created_timestamp_utc) FROM {{ this }})
{% endif %}

