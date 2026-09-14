
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Spotify Hit Lab",
    page_icon="🎵",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🎵 Spotify Hit Lab")

st.markdown(
    """
    ### Interactive 3D Spotify Analysis
    Explore the patterns behind streaming success, tempo evolution,
    and solo artists versus collaborations.
    """
)


# ============================================================
# LOAD DATA
# ============================================================

FILE_PATH = "/content/spotify dataset final.xlsm"

try:
    df = pd.read_excel(FILE_PATH)
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()


# ============================================================
# RENAME COLUMNS
# ============================================================

expected_columns = [
    "track_name",
    "artist_name",
    "artist_count",
    "released_year",
    "released_month",
    "released_day",
    "in_spotify_playlists",
    "in_spotify_charts",
    "streams",
    "in_apple_playlists",
    "in_apple_charts",
    "in_deezer_playlists",
    "in_deezer_charts",
    "in_shazam_charts",
    "bpm",
    "key",
    "mode",
    "danceability",
    "valence",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "cover_url"
]

if len(df.columns) == len(expected_columns):
    df.columns = expected_columns
else:
    st.error(
        f"Dataset has {len(df.columns)} columns, "
        f"but the app expects {len(expected_columns)} columns."
    )
    st.stop()


# ============================================================
# NUMERIC CLEANING
# ============================================================

numeric_columns = [
    "artist_count",
    "released_year",
    "released_month",
    "released_day",
    "in_spotify_playlists",
    "in_spotify_charts",
    "streams",
    "in_apple_playlists",
    "in_apple_charts",
    "in_deezer_playlists",
    "in_deezer_charts",
    "in_shazam_charts",
    "bpm",
    "danceability",
    "valence",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Spotify Hit Lab")

question = st.sidebar.radio(
    "Choose a question:",
    [
        "Question 1 — Hit DNA",
        "Question 2 — Tempo Evolution",
        "Question 3 — Solo vs Collaboration"
    ]
)


# ============================================================
# COMMON YEAR INFORMATION
# ============================================================

available_years = sorted(
    df["released_year"]
    .dropna()
    .astype(int)
    .unique()
)

if len(available_years) == 0:
    st.error("No valid release years were found.")
    st.stop()

min_year = min(available_years)
max_year = max(available_years)

default_start = max(
    min_year,
    max_year - 9
)

year_range = st.sidebar.slider(
    "📅 Release year range",
    min_value=min_year,
    max_value=max_year,
    value=(default_start, max_year),
    step=1
)


# ============================================================
# QUESTION 1
# ============================================================

if question == "Question 1 — Hit DNA":

    st.header("🧬 Question 1 — Spotify Hit DNA")

    st.markdown(
        """
        **What audio features most strongly correlate with high stream counts?**
        """
    )

    audio_features = [
        "danceability",
        "energy",
        "valence",
        "acousticness",
        "instrumentalness",
        "liveness",
        "speechiness",
        "bpm"
    ]

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    df_q1 = df[
        (df["released_year"] >= year_range[0]) &
        (df["released_year"] <= year_range[1])
    ].copy()

    df_q1 = df_q1.dropna(
        subset=["streams"] + audio_features
    )

    df_q1 = df_q1[
        df_q1["streams"] > 0
    ]

    # --------------------------------------------------------
    # LOG STREAMS
    # --------------------------------------------------------

    df_q1["log_streams"] = np.log10(
        df_q1["streams"]
    )

    # --------------------------------------------------------
    # CORRELATIONS
    # --------------------------------------------------------

    correlations = (
        df_q1[audio_features + ["streams"]]
        .corr()["streams"]
        .drop("streams")
        .sort_values(
            key=lambda x: abs(x),
            ascending=False
        )
    )

    top_feature_1 = correlations.index[0]
    top_feature_2 = correlations.index[1]

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🥇 Strongest relationship",
            top_feature_1.title(),
            f"{correlations[top_feature_1]:.3f}"
        )

    with col2:
        st.metric(
            "🥈 Second strongest",
            top_feature_2.title(),
            f"{correlations[top_feature_2]:.3f}"
        )

    with col3:
        st.metric(
            "🎵 Tracks analyzed",
            f"{len(df_q1):,}"
        )

    # --------------------------------------------------------
    # AXIS CONTROLS
    # --------------------------------------------------------

    st.markdown(
        "### 🌌 Rotate the Spotify Hit Universe"
    )

    feature_x = st.sidebar.selectbox(
        "Q1 — X-axis feature",
        audio_features,
        index=audio_features.index(top_feature_1)
    )

    feature_y = st.sidebar.selectbox(
        "Q1 — Y-axis feature",
        audio_features,
        index=audio_features.index(top_feature_2)
    )

    # --------------------------------------------------------
    # 3D FIGURE
    # --------------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(

            x=df_q1[feature_x],

            y=df_q1[feature_y],

            z=df_q1["log_streams"],

            mode="markers",

            name="Spotify Tracks",

            marker=dict(
                size=7,
                color=df_q1["log_streams"],
                colorscale="Turbo",
                opacity=0.78,
                colorbar=dict(
                    title="Log₁₀ Streams"
                )
            ),

            text=df_q1["track_name"],

            customdata=np.column_stack([
                df_q1["artist_name"],
                df_q1["streams"],
                df_q1["released_year"],
                df_q1[feature_x],
                df_q1[feature_y]
            ]),

            hovertemplate=
                "<b>🎵 %{text}</b><br><br>"
                "🎤 Artist: %{customdata[0]}<br>"
                "📅 Year: %{customdata[2]:.0f}<br>"
                f"🎚️ {feature_x.title()}: "
                "<b>%{customdata[3]:.1f}</b><br>"
                f"🎚️ {feature_y.title()}: "
                "<b>%{customdata[4]:.1f}</b><br>"
                "▶️ Streams: "
                "<b>%{customdata[1]:,.0f}</b>"
                "<extra></extra>"
        )
    )

    fig.update_layout(

        title=(
            f"Spotify Hit DNA — "
            f"{feature_x.title()} × "
            f"{feature_y.title()} × Streams"
        ),

        template="plotly_dark",

        height=800,

        scene=dict(

            xaxis_title=feature_x.title(),

            yaxis_title=feature_y.title(),

            zaxis_title="Log₁₀(Streams)",

            camera=dict(
                eye=dict(
                    x=1.6,
                    y=1.6,
                    z=1.3
                )
            )
        ),

        margin=dict(
            l=0,
            r=0,
            b=0,
            t=60
        )
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "displaylogo": False,
            "modeBarButtonsToAdd": [
                "resetCameraDefault3d",
                "resetCameraLastSave3d"
            ]
        }
    )

    # --------------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------------

    with st.expander("🧠 Q1 — What does this mean?"):

        st.write(
            f"""
            **{top_feature_1.title()}** has the strongest Pearson
            correlation with streams in the selected dataset:

            **r = {correlations[top_feature_1]:.3f}**

            The relationship is relatively weak, suggesting that
            audio features alone do not strongly explain streaming
            success.

            **Important:** correlation does not imply causation.
            """
        )


# ============================================================
# QUESTION 2
# ============================================================

elif question == "Question 2 — Tempo Evolution":

    st.header("🥁 Question 2 — Tempo Evolution")

    st.markdown(
        """
        **How has the average tempo of top hits changed over recent years?**
        """
    )

    # --------------------------------------------------------
    # TOP HIT CONTROL
    # --------------------------------------------------------

    top_percent = st.sidebar.select_slider(
        "🔥 Define a Top Hit",

        options=[
            5,
            10,
            15,
            20,
            25
        ],

        value=10,

        format_func=lambda x:
            f"Top {x}% streamed tracks"
    )

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    df_q2 = df[
        (df["released_year"] >= year_range[0]) &
        (df["released_year"] <= year_range[1])
    ].copy()

    df_q2 = df_q2.dropna(
        subset=[
            "released_year",
            "streams",
            "bpm"
        ]
    )

    df_q2 = df_q2[
        (df_q2["streams"] > 0) &
        (df_q2["bpm"] > 0)
    ]

    # --------------------------------------------------------
    # IDENTIFY TOP HITS WITHIN EACH YEAR
    # --------------------------------------------------------

    df_q2["stream_percentile"] = (
        df_q2
        .groupby("released_year")["streams"]
        .rank(
            pct=True,
            ascending=True
        )
    )

    df_q2["is_top_hit"] = (
        df_q2["stream_percentile"]
        >= (1 - top_percent / 100)
    )

    top_hits = df_q2[
        df_q2["is_top_hit"]
    ].copy()

    # --------------------------------------------------------
    # YEARLY SUMMARY
    # --------------------------------------------------------

    yearly = (
        top_hits
        .groupby("released_year")
        .agg(
            average_bpm=("bpm", "mean"),
            median_bpm=("bpm", "median"),
            tracks=("track_name", "count"),
            average_streams=("streams", "mean")
        )
        .reset_index()
        .sort_values("released_year")
    )

    if len(yearly) == 0:
        st.warning(
            "Not enough data for the selected filters."
        )
        st.stop()

    top_hits["log_streams"] = np.log10(
        top_hits["streams"]
    )

    yearly["log_average_streams"] = np.log10(
        yearly["average_streams"]
    )

    yearly["rolling_bpm"] = (
        yearly["average_bpm"]
        .rolling(
            window=3,
            min_periods=1
        )
        .mean()
    )

    # --------------------------------------------------------
    # CHANGE
    # --------------------------------------------------------

    first_year = yearly.iloc[0]
    latest_year = yearly.iloc[-1]

    bpm_change = (
        latest_year["average_bpm"]
        - first_year["average_bpm"]
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📅 First year",
            f"{int(first_year['released_year'])}"
        )

    with col2:
        st.metric(
            "🥁 First average BPM",
            f"{first_year['average_bpm']:.1f}"
        )

    with col3:
        st.metric(
            "🚀 Latest average BPM",
            f"{latest_year['average_bpm']:.1f}"
        )

    with col4:
        st.metric(
            "📈 BPM change",
            f"{bpm_change:+.1f}"
        )

    # --------------------------------------------------------
    # 3D GRAPH
    # --------------------------------------------------------

    st.markdown(
        "### 🌌 Spin through the evolution of top hits"
    )

    fig = go.Figure()

    # Individual tracks
    fig.add_trace(
        go.Scatter3d(

            x=top_hits["released_year"],

            y=top_hits["bpm"],

            z=top_hits["log_streams"],

            mode="markers",

            name="Top Hit Tracks",

            marker=dict(
                size=7,
                color=top_hits["bpm"],
                colorscale="Turbo",
                opacity=0.78,
                colorbar=dict(
                    title="BPM"
                )
            ),

            text=top_hits["track_name"],

            customdata=np.column_stack([
                top_hits["artist_name"],
                top_hits["streams"],
                top_hits["released_year"],
                top_hits["bpm"]
            ]),

            hovertemplate=
                "<b>🎵 %{text}</b><br><br>"
                "🎤 Artist: %{customdata[0]}<br>"
                "📅 Year: %{customdata[2]:.0f}<br>"
                "🥁 Tempo: "
                "<b>%{customdata[3]:.1f} BPM</b><br>"
                "▶️ Streams: "
                "<b>%{customdata[1]:,.0f}</b>"
                "<extra>TOP HIT</extra>"
        )
    )

    # Yearly average
    fig.add_trace(
        go.Scatter3d(

            x=yearly["released_year"],

            y=yearly["average_bpm"],

            z=yearly["log_average_streams"],

            mode="lines+markers",

            name="Average BPM",

            line=dict(
                width=10
            ),

            marker=dict(
                size=13,
                color=yearly["average_bpm"],
                colorscale="Turbo",
                showscale=False
            ),

            customdata=np.column_stack([
                yearly["tracks"],
                yearly["median_bpm"],
                yearly["rolling_bpm"],
                yearly["average_streams"]
            ]),

            hovertemplate=
                "<b>📅 %{x:.0f}</b><br><br>"
                "🔥 Average Tempo: "
                "<b>%{y:.1f} BPM</b><br>"
                "Median Tempo: "
                "%{customdata[1]:.1f} BPM<br>"
                "Top Hits: "
                "%{customdata[0]:.0f}<br>"
                "3-Year Rolling BPM: "
                "%{customdata[2]:.1f}<br>"
                "Average Streams: "
                "%{customdata[3]:,.0f}"
                "<extra>YEARLY AVERAGE</extra>"
        )
    )

    fig.update_layout(

        title="Spotify Top-Hit Tempo Evolution",

        template="plotly_dark",

        height=800,

        scene=dict(

            xaxis_title="Release Year",

            yaxis_title="BPM",

            zaxis_title="Log₁₀(Streams)",

            camera=dict(
                eye=dict(
                    x=1.6,
                    y=1.6,
                    z=1.3
                )
            )
        ),

        margin=dict(
            l=0,
            r=0,
            b=0,
            t=60
        )
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "displaylogo": False,
            "modeBarButtonsToAdd": [
                "resetCameraDefault3d",
                "resetCameraLastSave3d"
            ]
        }
    )

    # --------------------------------------------------------
    # AUTOMATIC INSIGHT
    # --------------------------------------------------------

    if bpm_change > 2:

        st.success(
            "📈 Top-hit tempo has generally increased "
            "over the selected period."
        )

    elif bpm_change < -2:

        st.success(
            "📉 Top-hit tempo has generally decreased "
            "over the selected period."
        )

    else:

        st.info(
            "➡️ Top-hit tempo has remained relatively stable "
            "over the selected period."
        )

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    with st.expander("🧠 Q2 — Methodology"):

        st.write(
            f"""
            A **Top Hit** is defined as a track belonging to the
            highest **{top_percent}% of streamed tracks within its
            release year**.

            This prevents older years from automatically dominating
            the comparison because older tracks have had more time
            to accumulate streams.

            The connected 3D line represents the yearly average BPM.
            """
        )


# ============================================================
# QUESTION 3
# ============================================================

else:

    st.header("🤝 Question 3 — Solo vs Collaboration")

    st.markdown(
        """
        **Do solo artists or collaborations tend to have higher
        streaming success?**
        """
    )

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    df_q3 = df[
        (df["released_year"] >= year_range[0]) &
        (df["released_year"] <= year_range[1])
    ].copy()

    df_q3 = df_q3.dropna(
        subset=[
            "streams",
            "artist_count",
            "released_year"
        ]
    )

    df_q3 = df_q3[
        (df_q3["streams"] > 0) &
        (df_q3["artist_count"] >= 1)
    ]

    if len(df_q3) == 0:
        st.warning(
            "Not enough data for the selected filters."
        )
        st.stop()

    # --------------------------------------------------------
    # CLASSIFY
    # --------------------------------------------------------

    df_q3["artist_type"] = np.where(
        df_q3["artist_count"] == 1,
        "Solo",
        "Collaboration"
    )

    df_q3["log_streams"] = np.log10(
        df_q3["streams"]
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = (
        df_q3
        .groupby("artist_type")
        .agg(
            average_streams=("streams", "mean"),
            median_streams=("streams", "median"),
            average_artist_count=("artist_count", "mean"),
            tracks=("track_name", "count")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # GET VALUES SAFELY
    # --------------------------------------------------------

    solo_rows = summary[
        summary["artist_type"] == "Solo"
    ]

    collab_rows = summary[
        summary["artist_type"] == "Collaboration"
    ]

    if len(solo_rows) > 0:
        solo_avg = solo_rows["average_streams"].iloc[0]
        solo_median = solo_rows["median_streams"].iloc[0]
    else:
        solo_avg = np.nan
        solo_median = np.nan

    if len(collab_rows) > 0:
        collab_avg = collab_rows["average_streams"].iloc[0]
        collab_median = collab_rows["median_streams"].iloc[0]
    else:
        collab_avg = np.nan
        collab_median = np.nan

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if not np.isnan(solo_avg):
            st.metric(
                "🎤 Solo average streams",
                f"{solo_avg:,.0f}"
            )
        else:
            st.metric(
                "🎤 Solo average streams",
                "N/A"
            )

    with col2:
        if not np.isnan(collab_avg):
            st.metric(
                "🤝 Collaboration average streams",
                f"{collab_avg:,.0f}"
            )
        else:
            st.metric(
                "🤝 Collaboration average streams",
                "N/A"
            )

    with col3:
        if not np.isnan(solo_median):
            st.metric(
                "🎤 Solo median streams",
                f"{solo_median:,.0f}"
            )
        else:
            st.metric(
                "🎤 Solo median streams",
                "N/A"
            )

    with col4:
        if not np.isnan(collab_median):
            st.metric(
                "🤝 Collaboration median streams",
                f"{collab_median:,.0f}"
            )
        else:
            st.metric(
                "🤝 Collaboration median streams",
                "N/A"
            )

    # --------------------------------------------------------
    # 3D VISUAL
    # --------------------------------------------------------

    st.markdown(
        "### 🌌 The Collaboration Streaming Universe"
    )

    fig = go.Figure()

    # --------------------------------------------------------
    # INDIVIDUAL TRACKS
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter3d(

            x=df_q3["artist_count"],

            y=df_q3["released_year"],

            z=df_q3["log_streams"],

            mode="markers",

            name="Tracks",

            marker=dict(
                size=7,
                color=df_q3["log_streams"],
                colorscale="Turbo",
                opacity=0.75,
                colorbar=dict(
                    title="Log₁₀ Streams"
                )
            ),

            text=df_q3["track_name"],

            customdata=np.column_stack([
                df_q3["artist_name"],
                df_q3["artist_type"],
                df_q3["artist_count"],
                df_q3["released_year"],
                df_q3["streams"]
            ]),

            hovertemplate=
                "<b>🎵 %{text}</b><br><br>"
                "🎤 Artist(s): %{customdata[0]}<br>"
                "👥 Type: "
                "<b>%{customdata[1]}</b><br>"
                "👤 Artist Count: "
                "<b>%{customdata[2]:.0f}</b><br>"
                "📅 Release Year: "
                "%{customdata[3]:.0f}<br>"
                "▶️ Streams: "
                "<b>%{customdata[4]:,.0f}</b>"
                "<extra>TRACK</extra>"
        )
    )

    # --------------------------------------------------------
    # GROUP AVERAGES
    # --------------------------------------------------------

    group_average = (
        df_q3
        .groupby("artist_type")
        .agg(
            avg_artist_count=("artist_count", "mean"),
            avg_year=("released_year", "mean"),
            avg_streams=("streams", "mean"),
            median_streams=("streams", "median"),
            track_count=("track_name", "count")
        )
        .reset_index()
    )

    group_average["log_avg_streams"] = np.log10(
        group_average["avg_streams"]
    )

    # --------------------------------------------------------
    # GROUP AVERAGE MARKERS
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter3d(

            x=group_average["avg_artist_count"],

            y=group_average["avg_year"],

            z=group_average["log_avg_streams"],

            mode="markers+text",

            name="Group Average",

            marker=dict(
                size=22,
                opacity=1,
                line=dict(
                    width=3,
                    color="white"
                )
            ),

            text=group_average["artist_type"],

            textposition="top center",

            customdata=np.column_stack([
                group_average["avg_streams"],
                group_average["median_streams"],
                group_average["track_count"]
            ]),

            hovertemplate=
                "<b>%{text}</b><br><br>"
                "⭐ Average Streams: "
                "<b>%{customdata[0]:,.0f}</b><br>"
                "📊 Median Streams: "
                "%{customdata[1]:,.0f}<br>"
                "🎵 Tracks: "
                "%{customdata[2]:,.0f}"
                "<extra>GROUP AVERAGE</extra>"
        )
    )

    # --------------------------------------------------------
    # 3D LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        title="Solo Artists vs Collaborations — Streaming Success",

        template="plotly_dark",

        height=850,

        scene=dict(

            xaxis_title="Number of Artists",

            yaxis_title="Release Year",

            zaxis_title="Log₁₀(Streams)",

            camera=dict(
                eye=dict(
                    x=1.7,
                    y=1.7,
                    z=1.4
                )
            )
        ),

        margin=dict(
            l=0,
            r=0,
            b=0,
            t=60
        ),

        legend=dict(
            x=0.02,
            y=0.98
        )
    )

    # --------------------------------------------------------
    # INTERACTIVE PLOT
    # --------------------------------------------------------

    st.plotly_chart(
        fig,

        width="stretch",

        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "displaylogo": False,
            "modeBarButtonsToAdd": [
                "resetCameraDefault3d",
                "resetCameraLastSave3d"
            ]
        }
    )

    # --------------------------------------------------------
    # AUTOMATIC CONCLUSION
    # --------------------------------------------------------

    if (
        not np.isnan(solo_avg)
        and not np.isnan(collab_avg)
    ):

        if solo_avg > collab_avg:

            difference = (
                (solo_avg - collab_avg)
                / collab_avg
                * 100
            )

            st.success(
                f"🎤 **Solo artists have the higher average "
                f"streaming count** in the selected period, "
                f"by approximately **{difference:.1f}%**."
            )

        elif collab_avg > solo_avg:

            difference = (
                (collab_avg - solo_avg)
                / solo_avg
                * 100
            )

            st.success(
                f"🤝 **Collaborations have the higher average "
                f"streaming count** in the selected period, "
                f"by approximately **{difference:.1f}%**."
            )

        else:

            st.info(
                "➡️ Solo artists and collaborations have "
                "the same average streaming count."
            )

    # --------------------------------------------------------
    # MEDIAN INSIGHT
    # --------------------------------------------------------

    if (
        not np.isnan(solo_median)
        and not np.isnan(collab_median)
    ):

        if collab_median > solo_median:

            st.info(
                "📊 The collaboration group also has a higher "
                "median stream count, suggesting the pattern "
                "is not driven only by a few extremely popular tracks."
            )

        elif solo_median > collab_median:

            st.info(
                "📊 Solo artists also have a higher median "
                "stream count, suggesting the pattern persists "
                "beyond the average."
            )

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    with st.expander(
        "🧠 Q3 — Methodology"
    ):

        st.write(
            """
            **Solo artist:** `artist_count = 1`

            **Collaboration:** `artist_count > 1`

            Streaming success is measured using Spotify stream counts.

            Because streams are highly skewed, the vertical dimension
            uses **log₁₀(streams)**. This makes very large differences
            easier to visualize.

            Individual tracks are shown as floating 3D points.

            The large markers represent the average streaming performance
            of the two artist categories.

            The median is also reported because averages can be strongly
            affected by extremely popular tracks.

            **Important:** A higher streaming count does not prove that
            being solo or collaborating causes greater success. Other
            factors such as artist popularity, release year, genre,
            promotion, and playlist exposure can influence streams.
            """
        )

    # --------------------------------------------------------
    # SUMMARY TABLE
    # --------------------------------------------------------

    st.markdown(
        "### 📊 Streaming Success Summary"
    )

    display_summary = summary[
        [
            "artist_type",
            "tracks",
            "average_streams",
            "median_streams",
            "average_artist_count"
        ]
    ].copy()

    display_summary.columns = [
        "Artist Type",
        "Tracks",
        "Average Streams",
        "Median Streams",
        "Average Artist Count"
    ]

    st.dataframe(
        display_summary,
        width="stretch",
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🎵 Spotify Hit Lab • Interactive 3D Plotly Analysis • Hackathon Edition"
)
