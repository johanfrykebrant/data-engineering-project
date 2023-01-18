{{
    config(
        materialized='incremental'
		, schema='analytics'
		, unique_key= ['observation_timestamp','observation_station']
    )
}}

SELECT 	observation_name,
		observation_timestamp,	
		observation_value,
		observation_unit,
		observation_station,
		created_timestamp_utc,
		NOW() AS dbt_timestamp_utc
FROM staging.observations 
	WHERE observation_name = 'Lufttemperatur'
		AND observation_unit = 'degree celsius'
		AND observation_station = 'Malmö A'

{% if is_incremental() %}
		AND created_timestamp_utc > (SELECT MAX(created_timestamp_utc) FROM {{ this }})
{% endif %}

