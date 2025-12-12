WITH tracks_daily AS (
    SELECT
        RECORD:track_id::STRING        AS track_id,
        MAX(RECORD:track_name)::STRING AS track_name,
        MAX(RECORD:artist_id)::STRING  AS artist_id,
        MAX(RECORD:popularity)::INTEGER AS popularity,
        MAX(RECORD:release_date)::DATE AS release_date,
        record_date
    FROM {{ source('transform_bronze', 'tracks_bronze') }}
    GROUP BY track_id, record_date
)

SELECT * FROM tracks_daily
