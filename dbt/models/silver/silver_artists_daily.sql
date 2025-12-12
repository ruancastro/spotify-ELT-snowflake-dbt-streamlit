WITH artists_daily AS (
    SELECT
        RECORD:id::STRING AS artist_id,
        MAX(RECORD:name)::STRING AS artist_name,
        MAX(RECORD:market)::STRING AS market,
        MAX(RECORD:popularity)::INTEGER AS popularity,
        MAX(RECORD:followers)::INTEGER AS followers,
        record_date
    FROM {{ source('transform_bronze', 'artists_bronze') }}
    GROUP BY artist_id, record_date
)
SELECT * FROM artists_daily
