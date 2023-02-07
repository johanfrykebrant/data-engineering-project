{{
    config(
        materialized='incremental'
		, schema='analytics'
		, unique_key= ['temperature_timestamp']
    )
}}

WITH cte_forecasts AS (
SELECT 	--name AS forecast_name,
		forecast_timestamp AS temperature_timestamp,
		--CAST(EXTRACT(epoch FROM (forecast_timestamp - forecast_approved_timestamp)/(60*60)) AS INT) AS hours_diff,
		forecast_value AS observed_xhrs_temperature_value_degc,
		--forecast_unit,
		created_timestamp_utc ,
		NOW() AS dbt_timestamp_utc 
FROM staging.forecasts
	JOIN staging.forecast_name_codes
	ON forecast_code = code
WHERE forecast_name = 'xxxx'
	AND observation_unit = 'degree celsius'
	AND CAST(EXTRACT(epoch FROM (forecast_timestamp - forecast_approved_timestamp)/(60*60)) AS INT) - x <= 0.5  

)



WITH cte_observations AS (

SELECT	observation_timestamp AS temperature_timestamp,
		observation_value AS observed_temperature_value_degc,
		created_timestamp_utc,
		NOW() AS dbt_timestamp_utc
FROM staging.observations 
WHERE observation_name = 'Lufttemperatur'
	AND observation_unit = 'degree celsius'
	AND observation_station = 'Malmö A'

)


{% if is_incremental() %}
	AND created_timestamp_utc > (SELECT MAX(created_timestamp_utc) FROM {{ this }})
{% endif %}

