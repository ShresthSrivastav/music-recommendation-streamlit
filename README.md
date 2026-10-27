# Hybrid Music Recommendation Systems

An interactive Streamlit case-study project based on the supplied report. Users choose a listener from the built-in dataset; no personal data upload is required.

## What the app demonstrates

- Built-in catalogue, listener, and interaction datasets in `data/`
- Content-based cosine similarity from numeric track features
- Collaborative scores from Jaccard-similar listeners
- Hybrid score fusion controlled by the content weight alpha
- Genre and mood filters with explanations for every recommendation
- Like, skip, hide, and save-to-playlist feedback controls
- Precision@K, Recall@K, NDCG@K, coverage, and diversity evaluation
- Dataset analytics and the original report example

The dataset is synthetic for demonstration. The app does not use Spotify's private algorithm, scrape Spotify, or require API credentials.

## Run locally

On Windows, double-click `run_local.bat`. It starts the app and opens it at:

http://localhost:8501

Or run it from this folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8501
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
