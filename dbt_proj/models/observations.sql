{{ config(materialized='table',schema='analytics') }}

SELECT name AS forecast_name,
	forecast_timestamp,	
	EXTRACT(epoch FROM (forecast_timestamp - forecast_approved_timestamp)/(60*60)) AS hours_diff,
	forecast_value,
	forecast_unit
FROM staging.forecasts
	JOIN staging.forecast_name_codes
	ON forecast_code = code