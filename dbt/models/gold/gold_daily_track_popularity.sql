WITH base AS (

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

)

SELECT * FROM base
