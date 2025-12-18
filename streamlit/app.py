import streamlit as st
import pandas as pd
from snowflake_connection import get_connection
import altair as alt

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="🎄 Spotify Christmas Analytics", layout="wide")

st.title("🎄 Spotify Christmas Music Analytics")
st.caption("Analysis of Christmas-related artists and tracks during Nov–Dec 2025")

# --------------------------------------------------
# Snowflake connection
# --------------------------------------------------
conn = get_connection()

# --------------------------------------------------
# Global Market Filter
# --------------------------------------------------
st.subheader("🌍 Market Filter")

market_filter = st.radio("Select market", ["ALL", "BR", "GB"], horizontal=True)

# --------------------------------------------------
# Summary ingestion metrics
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

kpis = pd.read_sql(
    """
    SELECT
        COUNT(DISTINCT track_id)     AS total_tracks,
        COUNT(DISTINCT artist_id)    AS total_artists,
        MAX(record_date)             AS last_update,
        COUNT(DISTINCT record_date)  AS days_tracked
    FROM SPOTIFY.TRANSFORM_GOLD.gold_daily_track_popularity
    WHERE (%s = 'ALL' OR market = %s)
    """,
    conn,
    params=(market_filter, market_filter),
)

kpi_row = kpis.iloc[0]

col1.metric("🎵 Tracks Analyzed", int(kpi_row["TOTAL_TRACKS"]))
col2.metric("🎤 Artists Analyzed", int(kpi_row["TOTAL_ARTISTS"]))
col3.metric("📅 Last Update", kpi_row["LAST_UPDATE"].strftime("%Y-%m-%d"))
col4.metric("📊 Days Tracked", int(kpi_row["DAYS_TRACKED"]))

# --------------------------------------------------
# Most Popular Christmas Tracks
# --------------------------------------------------
st.subheader("🔥 Most Popular Tracks by Market")

if market_filter == "ALL":
    query_popularity = """
    SELECT
        track_name,
        artist_name,
        market,
        max_popularity,
        avg_popularity,
        peak_date
    FROM (
        SELECT
            track_name,
            artist_name,
            market,
            max_popularity,
            avg_popularity,
            peak_date,
            ROW_NUMBER() OVER (
                ORDER BY max_popularity DESC
            ) AS rn
        FROM SPOTIFY.TRANSFORM_GOLD.gold_track_popularity_summary
    )
    WHERE rn <= 10
    ORDER BY max_popularity DESC
    """
    params_popularity = ()
else:
    query_popularity = """
    SELECT
        track_name,
        artist_name,
        market,
        max_popularity,
        avg_popularity,
        peak_date
    FROM (
        SELECT
            track_name,
            artist_name,
            market,
            max_popularity,
            avg_popularity,
            peak_date,
            ROW_NUMBER() OVER (
                PARTITION BY market
                ORDER BY max_popularity DESC
            ) AS rn
        FROM SPOTIFY.TRANSFORM_GOLD.gold_track_popularity_summary
        WHERE market = %s
    )
    WHERE rn <= 10
    ORDER BY max_popularity DESC
    """
    params_popularity = (market_filter,)

df_popularity = pd.read_sql(query_popularity, conn, params=params_popularity)

st.dataframe(df_popularity, use_container_width=True)

# --------------------------------------------------
# Top Growing Christmas Tracks
# --------------------------------------------------
st.subheader("📈 Top Tracks by Popularity Growth")


if market_filter == "ALL":
    query_growth = """
    SELECT
        track_name,
        artist_name,
        market,
        popularity_growth,
        max_popularity,
        peak_date
    FROM (
        SELECT
            track_name,
            artist_name,
            market,
            popularity_growth,
            max_popularity,
            peak_date,
            ROW_NUMBER() OVER (
                ORDER BY popularity_growth DESC
            ) AS rn
        FROM SPOTIFY.TRANSFORM_GOLD.gold_track_popularity_summary
    )
    WHERE rn <= 10
    ORDER BY popularity_growth DESC
    """
    params_growth = ()
else:
    query_growth = """
    SELECT
        track_name,
        artist_name,
        market,
        popularity_growth,
        max_popularity,
        peak_date
    FROM (
        SELECT
            track_name,
            artist_name,
            market,
            popularity_growth,
            max_popularity,
            peak_date,
            ROW_NUMBER() OVER (
                PARTITION BY market
                ORDER BY popularity_growth DESC
            ) AS rn
        FROM SPOTIFY.TRANSFORM_GOLD.gold_track_popularity_summary
        WHERE market = %s
    )
    WHERE rn <= 10
    ORDER BY popularity_growth DESC
    """
    params_growth = (market_filter,)

df_growth = pd.read_sql(query_growth, conn, params=params_growth)

st.dataframe(df_growth, use_container_width=True)

# --------------------------------------------------
# Track Popularity Over Time
# --------------------------------------------------


st.subheader("📊 Track Popularity Over Time")

# --------------------------------------------------
# Track selector (label != key)
# --------------------------------------------------
df_tracks = pd.read_sql(
    """
    SELECT DISTINCT
        track_id,
        track_name,
        artist_name
    FROM SPOTIFY.TRANSFORM_GOLD.gold_track_popularity_summary
    WHERE (%s = 'ALL' OR market = %s)
    ORDER BY track_name
    """,
    conn,
    params=(market_filter, market_filter),
)

df_tracks["label"] = df_tracks["TRACK_NAME"] + " — " + df_tracks["ARTIST_NAME"]

selected_label = st.selectbox("Select a track to explore", df_tracks["label"])

selected_track_id = df_tracks.loc[
    df_tracks["label"] == selected_label, "TRACK_ID"
].iloc[0]

# --------------------------------------------------
# Daily popularity (track_id-based)
# --------------------------------------------------
df_daily = pd.read_sql(
    """
    SELECT
        record_date,
        popularity
    FROM SPOTIFY.TRANSFORM_GOLD.gold_daily_track_popularity
    WHERE track_id = %s
      AND (%s = 'ALL' OR market = %s)
    ORDER BY record_date
    """,
    conn,
    params=(selected_track_id, market_filter, market_filter),
)

days_observed = len(df_daily)

st.caption(f"📅 Observed on {days_observed} day(s)")


# --------------------------------------------------
# Identify peak
# --------------------------------------------------
peak_row = df_daily.loc[df_daily["POPULARITY"].idxmax()]

# --------------------------------------------------
# Line chart
# --------------------------------------------------
line = (
    alt.Chart(df_daily)
    .mark_line(point=True, color="#2ecc71")
    .encode(
        x=alt.X("RECORD_DATE:T", title="Date"),
        y=alt.Y("POPULARITY:Q", title="Popularity", scale=alt.Scale(zero=False)),
        tooltip=["RECORD_DATE:T", "POPULARITY:Q"],
    )
)

# --------------------------------------------------
# Peak marker
# --------------------------------------------------
peak = (
    alt.Chart(pd.DataFrame([peak_row]))
    .mark_point(size=180, color="#f1c40f", filled=True)
    .encode(
        x="RECORD_DATE:T",
        y="POPULARITY:Q",
        tooltip=[
            alt.Tooltip("RECORD_DATE:T", title="Peak Date"),
            alt.Tooltip("POPULARITY:Q", title="Peak Popularity"),
        ],
    )
)

# --------------------------------------------------
# Annotation
# --------------------------------------------------
annotation = (
    alt.Chart(pd.DataFrame([peak_row]))
    .mark_text(
        align="left", dx=12, dy=-14, color="#e74c3c", fontSize=12, fontWeight="bold"
    )
    .encode(x="RECORD_DATE:T", y="POPULARITY:Q", text=alt.value("🎄 Peak"))
)


chart = (line + peak + annotation).properties(height=350)

st.altair_chart(chart, use_container_width=True)


# --------------------------------------------------
# Artist Popularity Growth Performance
# --------------------------------------------------
st.subheader("👑 Artist Popularity Growth Performance")

if market_filter == "ALL":
    query_artists = """
    SELECT
        artist_name,
        market,
        avg_popularity,
        popularity_growth
    FROM (
        SELECT
            artist_name,
            market,
            avg_popularity,
            popularity_growth,
            ROW_NUMBER() OVER (
                ORDER BY popularity_growth DESC
            ) AS rn
        FROM SPOTIFY.TRANSFORM_GOLD.gold_artist_monthly_summary
    )
    WHERE rn <= 10
    ORDER BY popularity_growth DESC
    """
    params_artists = ()
else:
    query_artists = """
    SELECT
        artist_name,
        market,
        avg_popularity,
        popularity_growth
    FROM (
        SELECT
            artist_name,
            market,
            avg_popularity,
            popularity_growth,
            ROW_NUMBER() OVER (
                PARTITION BY market
                ORDER BY popularity_growth DESC
            ) AS rn
        FROM SPOTIFY.TRANSFORM_GOLD.gold_artist_monthly_summary
        WHERE market = %s
    )
    WHERE rn <= 10
    ORDER BY popularity_growth DESC
    """
    params_artists = (market_filter,)

df_artists = pd.read_sql(query_artists, conn, params=params_artists)

top_artist = df_artists.loc[df_artists["POPULARITY_GROWTH"].idxmax()]

bars = (
    alt.Chart(df_artists)
    .mark_bar(color="#3CB371")
    .encode(
        x=alt.X(
            "POPULARITY_GROWTH:Q", title="Popularity Growth", axis=alt.Axis(grid=True)
        ),
        y=alt.Y("ARTIST_NAME:N", sort="-x", title="Artist"),
        tooltip=[
            alt.Tooltip("ARTIST_NAME:N", title="Artist"),
            alt.Tooltip("MARKET:N", title="Market"),
            alt.Tooltip("POPULARITY_GROWTH:Q", title="Growth"),
            alt.Tooltip("AVG_POPULARITY:Q", title="Avg Popularity"),
        ],
    )
)

highlight = (
    alt.Chart(pd.DataFrame([top_artist]))
    .mark_bar(color="#C9A227")
    .encode(x="POPULARITY_GROWTH:Q", y=alt.Y("ARTIST_NAME:N", sort="-x"),
    tooltip=[
        alt.Tooltip("ARTIST_NAME:N", title="Artist"),
        alt.Tooltip("MARKET:N", title="Market"),
        alt.Tooltip("POPULARITY_GROWTH:Q", title="Growth"),
        alt.Tooltip("AVG_POPULARITY:Q", title="Avg Popularity"),
    ])
)


annotation = (
    alt.Chart(pd.DataFrame([top_artist]))
    .mark_text(align="left", dx=8, color="#C9A227", fontSize=14, fontWeight="bold")
    .encode(x="POPULARITY_GROWTH:Q", y="ARTIST_NAME:N", text=alt.value("👑"))
)

chart = (bars + highlight + annotation).properties(height=400)

st.altair_chart(chart, use_container_width=True)
