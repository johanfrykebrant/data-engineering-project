CREATE SCHEMA staging

CREATE TABLE observations (
    observation_timestamp           TIMESTAMP,
    observation_station             TEXT,
    observation_value               REAL,
    observation_name                TEXT,
    observation_unit                TEXT,
    created_timestamp_utc           TIMESTAMP NOT NULL DEFAULT NOW()
    )

CREATE TABLE forecasts (
    forecast_code                   TEXT,
    forecast_approved_timestamp     TIMESTAMP,
    forecast_coordinates            TEXT,
    forecast_timestamp              TIMESTAMP,
    forecast_value                  REAL,
    forecast_unit                   TEXT,
    created_timestamp_utc           TIMESTAMP NOT NULL DEFAULT NOW()
)

CREATE TABLE energy_prices (
    price_timestamp                 TIMESTAMP,
    price                           REAL,
    bidding_zone                    TEXT,
    unit                            TEXT,
    created_timestamp_utc           TIMESTAMP NOT NULL DEFAULT NOW()
    )

;
