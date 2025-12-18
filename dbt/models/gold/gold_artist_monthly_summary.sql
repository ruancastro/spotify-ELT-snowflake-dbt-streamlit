WITH artist_daily AS (

    SELECT
        artist_id,
        artist_name,
        market,
        popularity,
        record_date
    FROM {{ ref('silver_artists_daily') }}

),
aggregated AS (

    SELECT
        artist_id,
        artist_name,
        market,
        ROUND(AVG(popularity), 2)  AS avg_popularity,
        MAX(popularity)  AS max_popularity,
        MIN(popularity)  AS min_popularity,
        MAX(popularity) - MIN(popularity) AS popularity_growth,
        COUNT(DISTINCT record_date) AS days_observed
    FROM artist_daily
    GROUP BY artist_id, artist_name, market

)

SELECT * FROM aggregated