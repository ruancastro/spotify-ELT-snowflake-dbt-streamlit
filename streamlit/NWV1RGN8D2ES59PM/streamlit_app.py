import streamlit as st
from snowflake.snowpark.context import get_active_session

# Get Snowflake session
session = get_active_session()

st.set_page_config(
    page_title="🎄 Spotify Christmas Analytics",
    layout="wide"
)

st.title("🎄 Spotify Christmas Music Trends")
st.caption("Streamlit running natively inside Snowflake")

query = """
SELECT
    track_name,
    artist_name,
    market,
    avg_popularity,
    popularity_growth,
    peak_date
FROM gold_top_christmas_tracks
ORDER BY popularity_growth DESC
LIMIT 10
"""

df = session.sql(query).to_pandas()

st.subheader("🔥 Top Christmas Tracks")
st.dataframe(df, use_container_width=True)

# Graphics 
tracks = session.sql("""
    SELECT DISTINCT track_name
    FROM gold_daily_track_popularity
    ORDER BY track_name
""").to_pandas()["TRACK_NAME"]

selected_track = st.selectbox("Select a track", tracks)

# Query diaria

query_daily = f"""
SELECT
    record_date,
    popularity
FROM gold_daily_track_popularity
WHERE track_name = '{selected_track}'
ORDER BY record_date
"""

df_daily = session.sql(query_daily).to_pandas()

st.subheader("📈 Popularity Over Time")
st.line_chart(df_daily.set_index("RECORD_DATE"))

# Por artista

query_artists = """
SELECT
    artist_name,
    market,
    avg_popularity,
    popularity_growth
FROM gold_artist_monthly_summary
ORDER BY popularity_growth DESC
"""

df_artists = session.sql(query_artists).to_pandas()

st.subheader("👑 Artist Performance")
st.bar_chart(
    df_artists.set_index("ARTIST_NAME")["POPULARITY_GROWTH"]
)

