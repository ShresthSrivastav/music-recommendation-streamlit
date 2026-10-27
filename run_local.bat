@echo off
cd /d "%~dp0"
echo Starting Hybrid Music Recommendation Systems...
echo Open http://localhost:8501 if the browser does not open automatically.
python -m streamlit run app.py
pause
