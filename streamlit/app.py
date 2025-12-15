import streamlit as st
import pandas as pd
from snowflake_connection import get_connection

st.set_page_config(
    page_title="🎄 Spotify Christmas Analytics",
    layout="wide"
)

st.title("🎄 Spotify Christmas Music Trends")
st.caption("Streamlit connected directly to Snowflake")

conn = get_connection()

# -----------------------------
# Top Christmas Tracks
# -----------------------------
query = """
SELECT
    track_name,
    artist_name,
    market,
    avg_popularity,
    popularity_growth,
    peak_date
FROM SPOTIFY.TRANSFORM_GOLD.GOLD_TOP_CHRISTMAS_TRACKS
ORDER BY popularity_growth DESC
LIMIT 10
"""

df = pd.read_sql(query, conn)

st.subheader("🔥 Top Christmas Tracks")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Track selection
# -----------------------------
tracks = pd.read_sql("""
    SELECT DISTINCT track_name
    FROM SPOTIFY.TRANSFORM_GOLD.gold_daily_track_popularity
    ORDER BY track_name
""", conn)["TRACK_NAME"]

selected_track = st.selectbox("Select a track", tracks)

# -----------------------------
# Daily popularity
# -----------------------------
query_daily = """
SELECT
    record_date,
    popularity
FROM SPOTIFY.TRANSFORM_GOLD.gold_daily_track_popularity
WHERE track_name = %s
ORDER BY record_date
"""

df_daily = pd.read_sql(query_daily, conn, params=(selected_track,))

st.subheader("📈 Popularity Over Time")
st.line_chart(df_daily.set_index("RECORD_DATE"))

# -----------------------------
# Artist performance
# -----------------------------
query_artists = """
SELECT
    artist_name,
    market,
    avg_popularity,
    popularity_growth
FROM SPOTIFY.TRANSFORM_GOLD.gold_artist_monthly_summary
ORDER BY popularity_growth DESC
"""

df_artists = pd.read_sql(query_artists, conn)

st.subheader("👑 Artist Performance")
st.bar_chart(
    df_artists.set_index("ARTIST_NAME")["POPULARITY_GROWTH"]
)
