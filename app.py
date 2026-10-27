from __future__ import annotations

import streamlit as st

from src.recommender import LISTENED_TRACKS, TRACKS, exact_report_example, recommend


st.set_page_config(page_title="Hybrid Music Recommender", page_icon="🎧", layout="wide")

st.markdown(
    """
    <style>
    .main { background: #faf9f6; }
    [data-testid="stMetricValue"] { color: #1f6f5b; }
    .report-note { padding: 0.9rem 1rem; border-left: 4px solid #1f6f5b; background: #eef7f2; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Hybrid Music Recommendation Systems")
st.caption("An interactive case-study demo based on content-based, collaborative, and hybrid filtering")

with st.sidebar:
    st.header("Recommendation controls")
    content_weight = st.slider(
        "Content weight (α)", 0.0, 1.0, 0.4, 0.05,
        help="α controls the content score. The remaining weight goes to the collaborative score.",
    )
    genre = st.selectbox("Genre filter", ["All"] + sorted({track.genre for track in TRACKS}))
    limit = st.slider("Number of recommendations", 3, 8, 5)
    st.divider()
    st.write("**Listener history**")
    for track in LISTENED_TRACKS:
        st.write(f"✓ {track}")

recommendations = recommend(content_weight=content_weight, genre=genre, limit=limit)

col1, col2, col3 = st.columns(3)
col1.metric("Candidate tracks", len(recommendations))
col2.metric("Content weight α", f"{content_weight:.2f}")
col3.metric("Collaborative weight", f"{1 - content_weight:.2f}")

st.subheader("Ranked recommendations")
st.markdown(
    '<div class="report-note">These scores are illustrative, not Spotify production data. '
    'The demo makes the report\'s hybrid score equation visible.</div>',
    unsafe_allow_html=True,
)

table_rows = [
    {
        "Rank": index,
        "Track": row["title"],
        "Artist": row["artist"],
        "Genre": row["genre"],
        "Content": f"{float(row['content_score']):.2f}",
        "Collaborative": f"{float(row['collaborative_score']):.2f}",
        "Hybrid": f"{float(row['hybrid_score']):.2f}",
        "Why it appears": row["reason"],
    }
    for index, row in enumerate(recommendations, 1)
]
st.dataframe(table_rows, use_container_width=True, hide_index=True)

if recommendations:
    st.subheader("Hybrid score comparison")
    chart_rows = {row["title"]: float(row["hybrid_score"]) for row in recommendations}
    st.bar_chart(chart_rows, horizontal=True)

tab1, tab2, tab3 = st.tabs(["How it works", "Report example", "Evaluation lens"])
with tab1:
    st.markdown(
        """
        1. **Content-based filtering** compares the candidate's track characteristics with the listener's history.
        2. **Collaborative filtering** uses the response of listeners with similar behaviour.
        3. **Hybrid filtering** combines the signals:

        `Hybrid Score = α × Content Score + (1 − α) × Collaborative Score`

        Adjust α in the sidebar to see whether the ranking favours similarity or discovery.
        """
    )
with tab2:
    st.write("At the report's default α = 0.4, the three illustrative candidates rank as follows:")
    example = exact_report_example()
    st.dataframe(
        [
            {"Rank": i, "Candidate": row["title"], "Hybrid score": f"{float(row['hybrid_score']):.2f}"}
            for i, row in enumerate(example, 1)
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Track B = 0.81, Track A = 0.72, Track C = 0.54. The values are invented for demonstration.")
with tab3:
    st.markdown(
        """
        **Precision@K** = relevant recommendations in the top K ÷ K.

        **Recall@K** = relevant recommendations in the top K ÷ all relevant test items.

        Offline metrics are useful for controlled comparisons, but they do not fully capture satisfaction, novelty,
        diversity, changing preferences, privacy, or the fact that an unplayed track is not necessarily disliked.
        """
    )

st.divider()
st.caption("Scope: educational case-study prototype. It does not reverse-engineer Spotify's proprietary algorithm or call the Spotify API.")
