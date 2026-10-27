# Hybrid Music Recommendation Systems

An interactive Streamlit case-study prototype based on the supplied report. It demonstrates content-based, collaborative, and hybrid filtering using a small, transparent catalogue of illustrative scores.

## What the app demonstrates

- Content-based similarity from track characteristics
- Collaborative scores from similar-listener behaviour
- Hybrid score fusion: `α × content + (1 − α) × collaborative`
- Ranking changes as the content weight changes
- Genre filtering and recommendation explanations
- Precision@K and Recall@K definitions with offline-evaluation caveats

The example values are hypothetical. The app does not use Spotify's private algorithm, scrape Spotify, or require API credentials.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Deployment

The repository is ready for Streamlit Community Cloud. Select `app.py` as the main file and use Python 3.12 or newer.

One-click deployment: https://share.streamlit.io/deploy?repository=ShresthSrivastav/music-recommendation-streamlit&branch=main&mainModule=app.py

## Source

The original case-study report is preserved in `docs/` for traceability.
