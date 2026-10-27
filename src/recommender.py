"""Small, transparent hybrid recommender used by the Streamlit demo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class Track:
    title: str
    artist: str
    genre: str
    mood: str
    content_score: float
    collaborative_score: float
    reason: str


LISTENED_TRACKS = (
    "Acoustic Morning",
    "Mellow Indie Nights",
    "Folk Roads",
)


TRACKS = (
    Track("Track A: acoustic pop", "The Daybreaks", "Acoustic pop", "calm", 0.90, 0.60, "Strong match to the listener's track features"),
    Track("Track B: indie folk", "Northbound", "Indie folk", "calm", 0.75, 0.85, "Similar listeners respond positively"),
    Track("Track C: electronic dance", "Pulse Theory", "Electronic", "energetic", 0.30, 0.70, "A discovery option with collaborative support"),
    Track("Warm Vinyl", "June Harbor", "Indie pop", "calm", 0.82, 0.64, "Close to the listener's mellow indie history"),
    Track("Open Highway", "Mira Lane", "Folk", "uplifting", 0.70, 0.78, "Balances folk similarity with a strong community signal"),
    Track("Neon Steps", "Signal Bloom", "Electronic", "energetic", 0.42, 0.88, "A high collaborative score supports discovery"),
    Track("Paper Lanterns", "Cedar House", "Acoustic folk", "calm", 0.88, 0.55, "Very similar acoustic and folk characteristics"),
    Track("Afterglow Drive", "Static Summer", "Synth pop", "energetic", 0.48, 0.73, "Adds variety while retaining collaborative evidence"),
)


def hybrid_score(track: Track, content_weight: float) -> float:
    """Fuse content and collaborative signals using the report's equation."""
    if not 0 <= content_weight <= 1:
        raise ValueError("content_weight must be between 0 and 1")
    return content_weight * track.content_score + (1 - content_weight) * track.collaborative_score


def recommend(
    tracks: Iterable[Track] = TRACKS,
    content_weight: float = 0.4,
    genre: str = "All",
    limit: int = 5,
) -> list[dict[str, object]]:
    """Return ranked, explainable recommendations for the demo listener."""
    if limit < 1:
        raise ValueError("limit must be positive")
    rows = []
    for track in tracks:
        if genre != "All" and track.genre != genre:
            continue
        rows.append({
            **asdict(track),
            "hybrid_score": hybrid_score(track, content_weight),
        })
    return sorted(rows, key=lambda row: row["hybrid_score"], reverse=True)[:limit]


def exact_report_example() -> list[dict[str, object]]:
    """Reproduce the three candidates and ordering from the report."""
    return recommend(TRACKS[:3], content_weight=0.4, limit=3)


if __name__ == "__main__":
    result = exact_report_example()
    assert [row["title"] for row in result] == [
        "Track B: indie folk",
        "Track A: acoustic pop",
        "Track C: electronic dance",
    ]
    assert [round(float(row["hybrid_score"]), 2) for row in result] == [0.81, 0.72, 0.54]
    print("recommender self-check passed")
