{{
    config(
        materialized='incremental'
		, schema='analytics'
    )
}}


WITH 	temperature_observations AS (
			SELECT 	observation_timestamp, 
					observation_value,
					created_timestamp_utc
			FROM staging.observations
			WHERE observation_name = 'Lufttemperatur'
			ORDER BY created_timestamp_utc desc
			)
		,ranked_observations AS (
			SELECT 	observation_timestamp, 
					observation_value,
					created_timestamp_utc,
					RANK() OVER (PARTITION BY observation_timestamp 
								 ORDER BY created_timestamp_utc DESC) 
					AS w
			FROM temperature_observations
			)
SELECT 	observation_timestamp, 
		observation_value,
		created_timestamp_utc
FROM ranked_observations 
WHERE	W = 1

		


{% if is_incremental() %}
	AND observation_timestamp > (SELECT MAX(observation_timestamp) FROM {{ this }})
{% endif %} 

