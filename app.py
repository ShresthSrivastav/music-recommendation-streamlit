from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from src.recommender import (
    EVENT_WEIGHTS,
    evaluate_dataset,
    exact_report_example,
    load_dataset,
    recommend_for_user,
)


st.set_page_config(page_title="Hybrid Music Recommender", page_icon="M", layout="wide")

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


@st.cache_data
def get_data():
    return load_dataset()


tracks, users, base_interactions = get_data()

if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "playlist" not in st.session_state:
    st.session_state.playlist = []


def selected_user_id(user_name: str) -> str:
    return str(users.loc[users["user_name"] == user_name, "user_id"].iloc[0])


def working_interactions() -> pd.DataFrame:
    if not st.session_state.feedback:
        return base_interactions
    feedback = pd.DataFrame(st.session_state.feedback)
    feedback["row_order"] = np.arange(len(base_interactions), len(base_interactions) + len(feedback))
    return pd.concat([base_interactions, feedback], ignore_index=True)


def add_feedback(user_id: str, track_id: str, event: str) -> None:
    st.session_state.feedback.append({"user_id": user_id, "track_id": track_id, "event": event})


with st.sidebar:
    st.header("Choose a dataset listener")
    user_name = st.selectbox("Listener", users["user_name"].tolist())
    user_id = selected_user_id(user_name)
    user_profile = users.loc[users["user_id"] == user_id, "profile"].iloc[0]
    st.caption(user_profile)
    st.divider()
    st.header("Recommendation controls")
    content_weight = st.slider(
        "Content weight (alpha)", 0.0, 1.0, 0.4, 0.05,
        help="The remaining weight is given to collaborative filtering.",
    )
    genre = st.selectbox("Genre filter", ["All"] + sorted(tracks["genre"].unique().tolist()))
    mood = st.selectbox("Mood filter", ["All"] + sorted(tracks["mood"].unique().tolist()))
    limit = st.slider("Number of recommendations", 3, 10, 5)
    st.divider()
    if st.button("Clear this user's feedback", width="stretch"):
        st.session_state.feedback = [row for row in st.session_state.feedback if row["user_id"] != user_id]
        st.rerun()
    if st.button("Clear this user's playlist", width="stretch"):
        st.session_state.playlist = [row for row in st.session_state.playlist if row["user_id"] != user_id]
        st.rerun()


interactions = working_interactions()
user_history = interactions[interactions["user_id"] == user_id].merge(tracks, on="track_id", how="left")
playlist_rows = [row for row in st.session_state.playlist if row["user_id"] == user_id]
playlist_ids = {row["track_id"] for row in playlist_rows}
recommendations = recommend_for_user(
    user_id,
    tracks,
    interactions,
    content_weight=content_weight,
    genre=genre,
    mood=mood,
    limit=limit,
)
metrics, per_user = evaluate_dataset(users["user_id"], tracks, base_interactions, content_weight=content_weight, k=limit)


st.title("Hybrid Music Recommendation Systems")
st.caption("Choose a listener from the built-in dataset. No upload or personal data is required.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Selected listener", user_name)
col2.metric("History events", len(user_history))
col3.metric("Recommendations", len(recommendations))
col4.metric("Playlist items", len(playlist_rows))

st.markdown(
    '<div class="report-note">This app uses a self-contained synthetic dataset. '
    'Content scores use track features, collaborative scores use similar listeners, and the hybrid score combines both.</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(["Recommendations", "Evaluation", "Dataset", "Report example"])

with tab1:
    st.subheader(f"Recommendations for {user_name}")
    if not recommendations:
        st.warning("No unseen tracks match these filters. Try All for genre and mood.")
    for rank, row in enumerate(recommendations, 1):
        track_id = str(row["track_id"])
        left, score, like, skip, hide, save = st.columns([4, 1, 1, 1, 1, 1])
        left.markdown(f"**{rank}. {row['title']}**\n\n{row['artist']} - {row['genre']} - {row['mood']}")
        score.metric("Hybrid", f"{float(row['hybrid_score']):.2f}")
        if like.button("Like", key=f"like-{user_id}-{track_id}"):
            add_feedback(user_id, track_id, "like")
            st.rerun()
        if skip.button("Skip", key=f"skip-{user_id}-{track_id}"):
            add_feedback(user_id, track_id, "skip")
            st.rerun()
        if hide.button("Hide", key=f"hide-{user_id}-{track_id}"):
            add_feedback(user_id, track_id, "hide")
            st.rerun()
        if save.button("Save", key=f"save-{user_id}-{track_id}"):
            if track_id not in playlist_ids:
                st.session_state.playlist.append({"user_id": user_id, "track_id": track_id})
            st.rerun()
        st.progress(float(row["hybrid_score"]), text=f"Content {float(row['content_score']):.2f} - Collaborative {float(row['collaborative_score']):.2f}")
        st.caption(f"Why it appears: {row['reason']}")
        st.divider()

    if recommendations:
        st.subheader("Score comparison")
        chart = pd.DataFrame(
            {
                "Content": [row["content_score"] for row in recommendations],
                "Collaborative": [row["collaborative_score"] for row in recommendations],
                "Hybrid": [row["hybrid_score"] for row in recommendations],
            },
            index=[row["title"] for row in recommendations],
        )
        st.bar_chart(chart)

    st.subheader("Selected listener history")
    history_table = user_history[["title", "artist", "genre", "event"]].rename(columns={"title": "Track", "artist": "Artist", "genre": "Genre", "event": "Feedback"})
    st.dataframe(history_table, width="stretch", hide_index=True)

    if playlist_rows:
        playlist = tracks[tracks["track_id"].isin(playlist_ids)][["title", "artist", "genre"]]
        st.subheader("Saved playlist")
        st.dataframe(playlist, width="stretch", hide_index=True)

with tab2:
    st.subheader("Offline evaluation on the built-in dataset")
    st.caption("Leave-one-positive-out evaluation: one positive interaction per user is held out and tested in the top K.")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Precision@K", f"{metrics['precision@k']:.2f}")
    m2.metric("Recall@K", f"{metrics['recall@k']:.2f}")
    m3.metric("NDCG@K", f"{metrics['ndcg@k']:.2f}")
    m4.metric("Coverage", f"{metrics['coverage']:.2f}")
    m5.metric("Diversity", f"{metrics['diversity']:.2f}")
    if not per_user.empty:
        detail = per_user.merge(users[["user_id", "user_name"]], on="user_id", how="left")
        st.dataframe(detail[["user_name", "held_out_track", "hit@k", "precision@k", "recall@k", "ndcg@k"]], width="stretch", hide_index=True)
    st.info("These are offline metrics on a tiny synthetic dataset. They are useful for demonstrating the evaluation method, not for claiming production performance.")

with tab3:
    st.subheader("Built-in catalogue")
    st.dataframe(tracks, width="stretch", hide_index=True)
    st.subheader("Available listeners")
    st.dataframe(users, width="stretch", hide_index=True)
    st.subheader("Interaction analytics")
    event_counts = interactions["event"].value_counts().rename_axis("event").to_frame("count")
    st.bar_chart(event_counts)

with tab4:
    st.subheader("The report's illustrative score-fusion example")
    example = exact_report_example()
    st.dataframe(
        [
            {"Rank": index, "Candidate": row["title"], "Content": row["content_score"], "Collaborative": row["collaborative_score"], "Hybrid": f"{float(row['hybrid_score']):.2f}"}
            for index, row in enumerate(example, 1)
        ],
        width="stretch",
        hide_index=True,
    )
    st.caption("At alpha = 0.4: Track B = 0.81, Track A = 0.72, Track C = 0.54. These values remain intentionally hypothetical.")
    st.markdown(
        """
        **Hybrid Score = alpha x Content Score + (1 - alpha) x Collaborative Score**

        Content-based filtering uses track characteristics. Collaborative filtering uses patterns among listeners. The app's main tab applies these ideas to the built-in dataset rather than only showing the report's three invented rows.
        """
    )

st.divider()
st.caption("Educational prototype. The dataset is synthetic and the app does not reverse-engineer Spotify's proprietary algorithm or call the Spotify API.")
