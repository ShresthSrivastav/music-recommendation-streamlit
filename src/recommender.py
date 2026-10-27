"""Dataset-driven content, collaborative, and hybrid recommendation logic."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


FEATURES = ["energy", "valence", "acousticness", "danceability", "tempo"]
POSITIVE_EVENTS = {"like": 1.0, "save": 1.0, "complete": 0.9, "play": 0.6}
EVENT_WEIGHTS = {**POSITIVE_EVENTS, "skip": -0.8, "hide": -1.0}


@dataclass(frozen=True)
class Track:
    """Small report example retained for the report-example tab and tests."""

    title: str
    artist: str
    genre: str
    mood: str
    content_score: float
    collaborative_score: float
    reason: str


REPORT_TRACKS = (
    Track("Track A: acoustic pop", "The Daybreaks", "Acoustic pop", "calm", 0.90, 0.60, "Strong match to the listener's track features"),
    Track("Track B: indie folk", "Northbound", "Indie folk", "calm", 0.75, 0.85, "Similar listeners respond positively"),
    Track("Track C: electronic dance", "Pulse Theory", "Electronic", "energetic", 0.30, 0.70, "A discovery option with collaborative support"),
)


def load_dataset(data_dir: str | Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the built-in catalogue, users, and interaction history."""
    root = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
    tracks = pd.read_csv(root / "tracks.csv")
    users = pd.read_csv(root / "users.csv")
    interactions = pd.read_csv(root / "interactions.csv")
    interactions["row_order"] = np.arange(len(interactions))
    return tracks, users, interactions


def hybrid_score(track: Track, content_weight: float) -> float:
    """Fuse the report example's content and collaborative signals."""
    if not 0 <= content_weight <= 1:
        raise ValueError("content_weight must be between 0 and 1")
    return content_weight * track.content_score + (1 - content_weight) * track.collaborative_score


def recommend(
    tracks: Iterable[Track] = REPORT_TRACKS,
    content_weight: float = 0.4,
    genre: str = "All",
    limit: int = 5,
) -> list[dict[str, object]]:
    """Return the report's small illustrative ranking."""
    if limit < 1:
        raise ValueError("limit must be positive")
    rows = []
    for track in tracks:
        if genre != "All" and track.genre != genre:
            continue
        rows.append({**asdict(track), "hybrid_score": hybrid_score(track, content_weight)})
    return sorted(rows, key=lambda row: row["hybrid_score"], reverse=True)[:limit]


def exact_report_example() -> list[dict[str, object]]:
    return recommend(REPORT_TRACKS, content_weight=0.4, limit=3)


def _cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    return float(np.dot(left, right) / denominator) if denominator else 0.0


def _normalise(values: pd.Series) -> pd.Series:
    low, high = float(values.min()), float(values.max())
    if high == low:
        return pd.Series(0.0, index=values.index)
    return (values - low) / (high - low)


def _positive_history(user_id: str, interactions: pd.DataFrame) -> pd.DataFrame:
    history = interactions[interactions["user_id"] == user_id].copy()
    history["weight"] = history["event"].map(EVENT_WEIGHTS).fillna(0.0)
    return history


def _content_scores(user_id: str, tracks: pd.DataFrame, interactions: pd.DataFrame) -> pd.Series:
    history = _positive_history(user_id, interactions)
    liked = history[history["weight"] > 0].merge(tracks, on="track_id", how="inner")
    matrix = tracks[FEATURES].to_numpy(dtype=float)
    if liked.empty:
        profile = matrix.mean(axis=0)
    else:
        profile = np.average(liked[FEATURES].to_numpy(dtype=float), axis=0, weights=liked["weight"])
    return pd.Series([_cosine(row, profile) for row in matrix], index=tracks["track_id"])


def _collaborative_scores(user_id: str, tracks: pd.DataFrame, interactions: pd.DataFrame) -> pd.Series:
    positive = interactions[interactions["event"].isin(POSITIVE_EVENTS)].copy()
    user_items = {uid: set(group["track_id"]) for uid, group in positive.groupby("user_id")}
    mine = user_items.get(user_id, set())
    other_users: list[tuple[float, str]] = []
    for other_id, items in user_items.items():
        if other_id == user_id:
            continue
        union = mine | items
        similarity = len(mine & items) / len(union) if union else 0.0
        if similarity:
            other_users.append((similarity, other_id))

    popularity = positive.groupby("track_id")["event"].count().reindex(tracks["track_id"], fill_value=0).astype(float)
    raw = pd.Series({
        track_id: sum(similarity for similarity, other_id in other_users if track_id in user_items.get(other_id, set()))
        for track_id in tracks["track_id"]
    }, dtype=float)
    if raw.max() == 0:
        raw = popularity
    return _normalise(raw)


def _reason(content: float, collaborative: float, track: pd.Series) -> str:
    if collaborative > content + 0.12:
        return f"Similar listeners liked this {track['genre']} track; it adds discovery."
    if content > collaborative + 0.12:
        return f"Its {track['genre']} and {track['mood']} characteristics match the user's history."
    return "It balances track similarity with evidence from similar listeners."


def recommend_for_user(
    user_id: str,
    tracks: pd.DataFrame,
    interactions: pd.DataFrame,
    *,
    content_weight: float = 0.4,
    genre: str = "All",
    mood: str = "All",
    limit: int = 5,
    extra_excluded: Iterable[str] = (),
) -> list[dict[str, object]]:
    """Rank unseen tracks for a selected dataset user."""
    if not 0 <= content_weight <= 1:
        raise ValueError("content_weight must be between 0 and 1")
    if limit < 1:
        raise ValueError("limit must be positive")

    history = _positive_history(user_id, interactions)
    listened = set(history["track_id"]) | set(extra_excluded)
    candidates = tracks[~tracks["track_id"].isin(listened)].copy()
    if genre != "All":
        candidates = candidates[candidates["genre"] == genre]
    if mood != "All":
        candidates = candidates[candidates["mood"] == mood]
    if candidates.empty:
        return []

    content = _content_scores(user_id, tracks, interactions).reindex(candidates["track_id"]).fillna(0.0)
    collaborative = _collaborative_scores(user_id, tracks, interactions).reindex(candidates["track_id"]).fillna(0.0)
    candidates["content_score"] = content.to_numpy()
    candidates["collaborative_score"] = collaborative.to_numpy()
    candidates["hybrid_score"] = content_weight * candidates["content_score"] + (1 - content_weight) * candidates["collaborative_score"]
    candidates["reason"] = candidates.apply(lambda row: _reason(row["content_score"], row["collaborative_score"], row), axis=1)
    candidates = candidates.sort_values(["hybrid_score", "title"], ascending=[False, True]).head(limit)
    return candidates.to_dict("records")


def evaluate_dataset(
    user_ids: Iterable[str],
    tracks: pd.DataFrame,
    interactions: pd.DataFrame,
    *,
    content_weight: float = 0.4,
    k: int = 5,
) -> tuple[dict[str, float], pd.DataFrame]:
    """Leave-one-positive-out evaluation for the built-in dataset."""
    rows = []
    for user_id in user_ids:
        positives = _positive_history(user_id, interactions)
        positives = positives[positives["weight"] > 0].sort_values("row_order")
        if positives.empty:
            continue
        holdout = positives.iloc[-1]
        train = interactions.drop(index=holdout.name)
        ranked = recommend_for_user(user_id, tracks, train, content_weight=content_weight, limit=k)
        recommended_ids = [row["track_id"] for row in ranked]
        hit = holdout["track_id"] in recommended_ids
        rank = recommended_ids.index(holdout["track_id"]) + 1 if hit else 0
        rows.append({
            "user_id": user_id,
            "held_out_track": holdout["track_id"],
            "hit@k": int(hit),
            "precision@k": float(hit) / k,
            "recall@k": float(hit),
            "ndcg@k": 1 / np.log2(rank + 1) if rank else 0.0,
        })
    per_user = pd.DataFrame(rows)
    if per_user.empty:
        return {"precision@k": 0.0, "recall@k": 0.0, "ndcg@k": 0.0, "coverage": 0.0, "diversity": 0.0}, per_user
    recs = []
    genres = []
    for user_id in per_user["user_id"]:
        ranked = recommend_for_user(user_id, tracks, interactions, content_weight=content_weight, limit=k)
        recs.extend(row["track_id"] for row in ranked)
        genres.extend(row["genre"] for row in ranked)
    metrics = {
        "precision@k": float(per_user["precision@k"].mean()),
        "recall@k": float(per_user["recall@k"].mean()),
        "ndcg@k": float(per_user["ndcg@k"].mean()),
        "coverage": len(set(recs)) / len(tracks),
        "diversity": len(set(genres)) / len(tracks["genre"].unique()),
    }
    return metrics, per_user


if __name__ == "__main__":
    report_result = exact_report_example()
    assert [row["title"] for row in report_result] == ["Track B: indie folk", "Track A: acoustic pop", "Track C: electronic dance"]
    tracks, users, interactions = load_dataset()
    assert recommend_for_user(users.iloc[0]["user_id"], tracks, interactions, limit=3)
    print("recommender self-check passed")
