WITH track_daily AS (

    SELECT
        t.track_id,
        t.track_name,
        t.artist_id,
        a.artist_name,
        a.market,
        t.popularity,
        t.record_date
    FROM {{ ref('silver_tracks_daily') }} t
    JOIN {{ ref('silver_artists_daily') }} a
        ON t.artist_id = a.artist_id
       AND t.record_date = a.record_date

),

aggregated AS (
    SELECT
        track_id,
        track_name,
        artist_id,
        artist_name,
        market,
        ROUND(AVG(popularity),2)  AS avg_popularity,
        MAX(popularity)  AS max_popularity,
        MIN(popularity)  AS min_popularity,
        MAX(popularity) - MIN(popularity) AS popularity_growth,
        MAX_BY(record_date, popularity) AS peak_date
    FROM track_daily
    WHERE track_name ILIKE '%christmas%'
    GROUP BY track_id, track_name, artist_id, artist_name, market
)

SELECT * FROM aggregated