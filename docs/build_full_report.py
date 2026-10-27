from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.recommender import evaluate_dataset, load_dataset  # noqa: E402


OUTPUT = Path(__file__).with_name("Music_Recommendation_Systems_Project_Report.docx")
NAVY = "1F4E78"
TEAL = "1F6F5B"
PALE_BLUE = "EAF2F8"
PALE_GREEN = "EEF7F2"
PALE_GOLD = "FFF7E1"
GRID = "D9D9D9"
TEXT = RGBColor(29, 43, 39)


def set_font(run, name="Arial", size=10.5, bold=False, italic=False, color=TEXT):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_borders(cell, color=GRID, size="6"):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn("w:" + side))
        if node is None:
            node = OxmlElement("w:" + side)
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    set_font(run, size=9, color=RGBColor(100, 100, 100))
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)


def add_para(doc, text="", *, style=None, size=10.5, bold=False, italic=False, color=TEXT, align=None, space_after=6, keep=False):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.12
    p.paragraph_format.keep_with_next = keep
    if text:
        run = p.add_run(text)
        set_font(run, size=size, bold=bold, italic=italic, color=color)
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.line_spacing = 1.08
        run = p.add_run(item)
        set_font(run, size=10.5)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, size=15 if level == 1 else 12, bold=True, color=RGBColor(0, 0, 0))
    return p


def add_table(doc, headers, rows, widths=None, font_size=9.2):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    header = table.rows[0]
    repeat_header(header)
    for i, label in enumerate(headers):
        cell = header.cells[i]
        if widths:
            cell.width = Inches(widths[i])
        set_cell_shading(cell, NAVY)
        set_cell_borders(cell)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(str(label))
        set_font(run, size=font_size, bold=True, color=RGBColor(255, 255, 255))
    for row_index, values in enumerate(rows):
        row = table.add_row()
        for col_index, value in enumerate(values):
            cell = row.cells[col_index]
            if widths:
                cell.width = Inches(widths[col_index])
            set_cell_shading(cell, "FFFFFF" if row_index % 2 == 0 else PALE_BLUE)
            set_cell_borders(cell)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            run = p.add_run(str(value))
            set_font(run, size=font_size)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(7)
    run = p.add_run(text)
    set_font(run, size=9, italic=True, color=RGBColor(90, 90, 90))


def build_report():
    tracks, users, interactions = load_dataset(ROOT / "data")
    metrics, per_user = evaluate_dataset(users["user_id"], tracks, interactions, content_weight=0.4, k=5)

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    section.header_distance = Inches(0.3)
    section.footer_distance = Inches(0.35)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = TEXT
    for style_name, size in (("Title", 26), ("Heading 1", 15), ("Heading 2", 12)):
        style = doc.styles[style_name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = True

    footer = section.footer
    add_page_number(footer.paragraphs[0])

    # Cover page
    add_para(doc, "MANIPAL UNIVERSITY JAIPUR", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_para(doc, "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)
    add_para(doc, "PROJECT REPORT", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run("Hybrid Music Recommendation Systems")
    set_font(run, size=27, bold=True, color=RGBColor(0, 0, 0))
    add_para(doc, "A dataset-driven implementation of content-based, collaborative, and hybrid filtering", size=15, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=34)
    add_table(doc, ["Project detail", "Value"], [
        ("Submitted by", "Shresth Srivastav and Tanishq Mehta"),
        ("Course", "Recommender System (CSE4143)"),
        ("Application", "Streamlit local application"),
        ("Dataset", "Built-in synthetic catalogue with six demo listeners"),
        ("Year", "2026"),
    ], widths=[1.8, 4.7], font_size=10)
    add_para(doc, "", space_after=30)
    add_para(doc, "This report documents the implemented project, its recommendation methodology, interactive features, evaluation procedure, testing evidence, and known limitations.", size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(80, 80, 80), space_after=0)
    doc.add_page_break()

    # Executive summary
    add_heading(doc, "Executive Summary", 1)
    add_para(doc, "This project converts the supplied case study on music recommendation systems into a working Streamlit application. The application allows a user to choose one of six listeners from a built-in dataset and receive ranked recommendations without uploading any personal data. It demonstrates content-based filtering from track features, collaborative filtering from similar listener behaviour, and a hybrid score that combines both signals.")
    add_para(doc, "The final implementation contains a catalogue of 20 tracks, six listeners, and 43 interactions representing likes, saves, plays, completions, and skips. A selected listener's positive history is used to construct a content profile. Similar listeners are identified using overlap in positive interactions. Candidate songs are scored, filtered for tracks already heard or rejected, and presented with an explanation of why each song appears.")
    add_para(doc, "At the default content weight of 0.4 and top K of 5, the built-in evaluation produced Precision@5 of 0.13, Recall@5 of 0.67, NDCG@5 of 0.51, catalogue coverage of 0.80, and genre diversity of 0.92. These values are demonstrations on a small synthetic dataset, not production performance claims. The primary contribution is a reproducible educational system that makes the recommendation workflow visible and testable.")
    add_para(doc, "Keywords: music recommendation, content-based filtering, collaborative filtering, hybrid recommendation, Streamlit, cosine similarity, cold start, Precision@K, Recall@K, NDCG.", italic=True, size=10)

    add_heading(doc, "Contents", 1)
    contents = [
        "1. Introduction",
        "2. Problem Statement and Objectives",
        "3. Scope and Assumptions",
        "4. Recommendation Approaches",
        "5. System Requirements and Architecture",
        "6. Dataset and Preprocessing",
        "7. Recommendation Methodology",
        "8. Streamlit Application Design",
        "9. Evaluation Methodology",
        "10. Results and Discussion",
        "11. Testing and Validation",
        "12. Limitations and Responsible Use",
        "13. Future Improvements",
        "14. Conclusion",
        "References",
        "Appendices",
    ]
    for item in contents:
        add_para(doc, item, size=10.5, space_after=2)

    add_heading(doc, "1 Introduction", 1)
    add_para(doc, "Music streaming services expose listeners to catalogues that are too large to browse manually. A recommendation system reduces this search effort by ranking tracks that may be relevant to a listener's interests. The ranking problem is more demanding than identifying globally popular songs because preferences differ across people and change with mood, activity, context, and time.")
    add_para(doc, "The supplied case study describes three major approaches. Content-based filtering uses track characteristics. Collaborative filtering learns from patterns across listeners. Hybrid filtering combines the two approaches so that the system can use both the descriptive information in a song and the behaviour of listeners with related tastes. This project implements that design as a local, inspectable application rather than attempting to reproduce a proprietary production system.")
    add_para(doc, "The project is intentionally transparent. Every track, listener, interaction, score component, and evaluation result is available in the repository. The user selects a dataset listener and can change the content weight, filters, and feedback. This makes the system suitable for demonstrating recommendation concepts in a classroom or project presentation.")

    add_heading(doc, "2 Problem Statement and Objectives", 1)
    add_heading(doc, "2.1 Problem Statement", 2)
    add_para(doc, "Given a catalogue of tracks and an interaction history for several listeners, the system must rank unseen songs for a selected listener. The ranking should use the listener's own preferences and patterns from related listeners while avoiding tracks that have already been consumed, skipped, or hidden. It should also expose enough information for the user to understand the recommendation.")
    add_heading(doc, "2.2 Objectives", 2)
    add_bullets(doc, [
        "Implement content-based, collaborative, and hybrid recommendation methods.",
        "Allow the user to select an existing listener from the built-in dataset rather than entering personal data.",
        "Provide controls for content weight, genre, mood, and the number of recommendations.",
        "Explain each recommendation using its content and collaborative components.",
        "Support interactive like, skip, hide, and save-to-playlist feedback.",
        "Calculate ranking quality, coverage, and diversity metrics on the dataset.",
        "Validate the recommendation logic and local application through automated tests.",
    ])

    add_heading(doc, "3 Scope and Assumptions", 1)
    add_para(doc, "The application is an educational prototype. The dataset is synthetic and was created to make the system self-contained. It is not a measurement of a real streaming platform and it does not use Spotify's proprietary algorithm or Spotify API. The application demonstrates a method and an evaluation workflow; it does not claim that the chosen heuristics are optimal for a production service.")
    add_para(doc, "The system assumes that a positive event such as a like, save, completed listen, or play is evidence of interest with different strengths. A skip or hide is treated as negative feedback. These weights are design choices for the prototype. In a production system they would need to be learned or calibrated using a larger, representative dataset and careful online evaluation.")

    add_heading(doc, "4 Recommendation Approaches", 1)
    add_heading(doc, "4.1 Content Based Filtering", 2)
    add_para(doc, "Content-based filtering represents every track with features and compares a candidate with the listener's profile. The implementation uses five numeric features: energy, valence, acousticness, danceability, and tempo. The profile is a weighted average of tracks in the listener's positive history. Cosine similarity between the profile and a candidate track becomes the content score.")
    add_heading(doc, "4.2 Collaborative Filtering", 2)
    add_para(doc, "Collaborative filtering uses interaction patterns rather than track descriptions. The implementation represents a listener by the set of tracks associated with positive events. Similarity between two listeners is calculated using Jaccard overlap. Tracks liked by similar listeners receive a stronger collaborative score. If no similar listener signal is available, the system falls back to catalogue popularity from positive events, which provides a simple cold-start fallback.")
    add_heading(doc, "4.3 Hybrid Filtering", 2)
    add_para(doc, "The final ranking combines the two normalized components using the same score-fusion idea described in the source case study:")
    p = add_para(doc, "Hybrid Score = alpha x Content Score + (1 - alpha) x Collaborative Score", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
    add_para(doc, "The Streamlit slider exposes alpha. When alpha is high, the result favours similarity to the listener's track profile. When alpha is low, it favours patterns from similar listeners and catalogue discovery.")
    add_table(doc, ["Approach", "Primary signal", "Strength", "Main risk"], [
        ("Content-based", "Track features", "Explainable similarity", "Can become repetitive"),
        ("Collaborative", "Listener interactions", "Unexpected discovery", "Sparse data and cold start"),
        ("Hybrid", "Both signals", "Balances weaknesses", "Requires score calibration"),
    ], widths=[1.25, 1.6, 1.8, 1.85])
    add_caption(doc, "Table 1. Comparison of the recommendation approaches used in the project.")

    add_heading(doc, "5 System Requirements and Architecture", 1)
    add_heading(doc, "5.1 Functional Requirements", 2)
    add_table(doc, ["ID", "Requirement", "Implementation"], [
        ("FR1", "Select a listener", "Selectbox populated from users.csv"),
        ("FR2", "Generate recommendations", "Hybrid ranking over unseen tracks"),
        ("FR3", "Adjust ranking behaviour", "Content weight alpha slider"),
        ("FR4", "Filter results", "Genre, mood, and recommendation count"),
        ("FR5", "Show explanations", "Reason generated from component scores"),
        ("FR6", "Capture feedback", "Like, skip, hide, and save buttons"),
        ("FR7", "Evaluate quality", "Precision, recall, NDCG, coverage, diversity"),
    ], widths=[0.55, 2.45, 3.5], font_size=9)
    add_heading(doc, "5.2 Architecture", 2)
    add_para(doc, "The application follows a small data-to-interface pipeline:")
    add_table(doc, ["Stage", "Description"], [
        ("Data layer", "Read tracks.csv, users.csv, and interactions.csv."),
        ("Profile layer", "Convert positive listener events into a feature profile."),
        ("Candidate layer", "Remove heard, skipped, hidden, and filtered tracks."),
        ("Scoring layer", "Calculate content, collaborative, and hybrid scores."),
        ("Presentation layer", "Show ranked results, explanations, controls, and charts."),
        ("Evaluation layer", "Run leave-one-positive-out metrics across all users."),
    ], widths=[1.35, 5.15])
    add_caption(doc, "Table 2. Logical architecture of the implemented application.")

    add_heading(doc, "6 Dataset and Preprocessing", 1)
    add_para(doc, "The repository includes a small synthetic dataset so the application can be run locally without a data upload or external account. The catalogue contains 20 tracks by recurring demo artists, six selectable listeners, and 43 interaction records. The catalogue spans 13 genre labels and three broad moods: calm, uplifting, energetic, and reflective.")
    add_table(doc, ["Dataset component", "Size", "Purpose"], [
        ("tracks.csv", "20 tracks", "Metadata and five numeric feature values"),
        ("users.csv", "6 users", "Listener names and short profiles"),
        ("interactions.csv", "43 events", "Likes, saves, plays, completions, and skips"),
    ], widths=[1.6, 1.2, 3.7])
    add_caption(doc, "Table 3. Built-in dataset summary.")
    add_table(doc, ["Event", "Count", "Prototype weight", "Interpretation"], [
        ("like", "20", "+1.0", "Strong positive preference"),
        ("save", "6", "+1.0", "Strong positive preference"),
        ("complete", "6", "+0.9", "Completed listening session"),
        ("play", "5", "+0.6", "Moderate positive signal"),
        ("skip", "6", "-0.8", "Negative signal and exclusion"),
    ], widths=[1.1, 0.75, 1.25, 3.4])
    add_caption(doc, "Table 4. Interaction events and the weights used by the prototype.")
    add_para(doc, "Preprocessing is deliberately light. CSV files are loaded into data frames, numeric features are converted to floating-point values, and an event weight is assigned. The application preserves interaction order so that the evaluation procedure can hold out the last positive event for each listener.")

    add_heading(doc, "7 Recommendation Methodology", 1)
    add_heading(doc, "7.1 Listener Profile", 2)
    add_para(doc, "For the selected listener, the system extracts positive events and joins them with track features. The listener profile is the weighted average of the five feature columns. This profile is compared against every candidate track using cosine similarity. Tracks already present in the listener's history are excluded from the candidate set.")
    add_heading(doc, "7.2 Collaborative Score", 2)
    add_para(doc, "The collaborative component forms a positive track set for each listener. Jaccard similarity is calculated between the selected listener and every other listener with overlapping positive history. A candidate receives a larger score when it appears in the positive set of more similar listeners. The values are normalized to the interval from 0 to 1. If no collaborative vote exists, positive-event popularity supplies a fallback signal.")
    add_heading(doc, "7.3 Candidate Ranking and Explanations", 2)
    add_para(doc, "The system applies genre and mood filters after excluding the user's known tracks. It then calculates the hybrid score and sorts candidates in descending order. The explanation is generated from the relative component values: a collaborative explanation is shown when similar-listener evidence is substantially stronger, a content explanation is shown when feature similarity is stronger, and a balance explanation is shown when the two components are close.")
    add_heading(doc, "7.4 Feedback Loop", 2)
    add_para(doc, "Like, skip, and hide actions are stored in the current Streamlit session and appended to the working interaction history. A like can influence the next profile calculation, while a skip or hide removes the track from the candidate set. Save adds the track to the selected listener's session playlist. This provides an observable demonstration of feedback without storing personal data outside the session.")

    add_heading(doc, "8 Streamlit Application Design", 1)
    add_para(doc, "The application is organized around a listener-first workflow. The sidebar contains the listener selector and recommendation controls. The main page shows a recommendation list with component scores, progress bars, explanations, and feedback buttons. Separate tabs expose evaluation results, the full dataset, interaction analytics, and the original three-track example from the supplied report.")
    add_table(doc, ["Interface area", "User-visible function"], [
        ("Listener selector", "Choose Aisha, Ben, Carla, Dev, Elena, or Farhan from the built-in dataset."),
        ("Controls", "Change alpha, genre, mood, and result count."),
        ("Recommendation list", "Inspect ranking, scores, reasons, and feedback actions."),
        ("Evaluation tab", "Review ranking metrics and per-user holdout results."),
        ("Dataset tab", "Inspect tracks, listeners, and event distributions."),
        ("Report example tab", "Compare the implemented app with the original illustrative calculation."),
    ], widths=[1.7, 4.8])
    add_caption(doc, "Table 5. Main Streamlit interface areas.")
    add_para(doc, "A local Windows launcher is included as run_local.bat. It starts the application with Python's module invocation and uses port 8501. The same app can be deployed from the public GitHub repository to Streamlit Community Cloud by selecting app.py as the entrypoint.")

    add_heading(doc, "9 Evaluation Methodology", 1)
    add_para(doc, "The evaluation uses a leave-one-positive-out procedure. For each listener, the last positive interaction is selected as a held-out relevant item. The model is trained on the remaining interactions and asked for the top five recommendations. A hit occurs when the held-out item appears in that ranking.")
    add_table(doc, ["Metric", "Definition used in the project"], [
        ("Precision@K", "Hits in the top K divided by K."),
        ("Recall@K", "Hits in the top K divided by held-out relevant items."),
        ("NDCG@K", "Higher score when the held-out item appears near the top."),
        ("Coverage", "Unique recommended tracks divided by catalogue size."),
        ("Diversity", "Unique recommendation genres divided by catalogue genre count."),
    ], widths=[1.35, 5.15])
    add_caption(doc, "Table 6. Evaluation metrics used by the application.")
    add_para(doc, "Because each user contributes one held-out item, the reported recall is a hit rate for this small experiment. It should not be interpreted as recall over a large, fully labelled test set. The purpose is to demonstrate a reproducible evaluation mechanism and expose the trade-off between ranking quality, coverage, and diversity.")

    add_heading(doc, "10 Results and Discussion", 1)
    add_heading(doc, "10.1 Aggregate Results", 2)
    add_table(doc, ["Metric", "Result", "Interpretation"], [
        ("Precision@5", f"{metrics['precision@k']:.2f}", "Average fraction of five recommendations that matched the held-out item."),
        ("Recall@5", f"{metrics['recall@k']:.2f}", "Four of six users received their held-out item in the top five."),
        ("NDCG@5", f"{metrics['ndcg@k']:.2f}", "Hits were generally placed within the upper part of the ranking."),
        ("Coverage", f"{metrics['coverage']:.2f}", "The recommendation set exposed 80 percent of the catalogue."),
        ("Diversity", f"{metrics['diversity']:.2f}", "The recommendation set covered most catalogue genres."),
    ], widths=[1.35, 0.9, 4.25])
    add_caption(doc, "Table 7. Evaluation results at alpha = 0.4 and K = 5.")
    add_heading(doc, "10.2 Per Listener Results", 2)
    names = dict(zip(users["user_id"], users["user_name"]))
    per_rows = []
    for _, row in per_user.iterrows():
        per_rows.append((names[row["user_id"]], row["held_out_track"], int(row["hit@k"]), f"{row['ndcg@k']:.2f}"))
    add_table(doc, ["Listener", "Held-out track", "Hit@5", "NDCG@5"], per_rows, widths=[1.35, 1.65, 0.8, 0.8])
    add_caption(doc, "Table 8. Leave-one-positive-out results by listener.")
    add_para(doc, "The results show why a single average metric is insufficient. Four users received a top-five hit, while two users did not. The misses indicate that the small interaction graph does not always connect a listener's most recent positive track to a strong candidate signal. In a larger dataset, the model could use richer features, more users, time-aware weighting, and learned parameters to reduce these cases.")
    add_heading(doc, "10.3 Relation to the Original Report Example", 2)
    add_table(doc, ["Candidate", "Content", "Collaborative", "Hybrid"], [
        ("Track B: indie folk", "0.75", "0.85", "0.81"),
        ("Track A: acoustic pop", "0.90", "0.60", "0.72"),
        ("Track C: electronic dance", "0.30", "0.70", "0.54"),
    ], widths=[2.5, 1.1, 1.25, 1.1])
    add_caption(doc, "Table 9. The hypothetical score-fusion example retained from the source case study.")
    add_para(doc, "The application retains this example as a separate tab so that the report's arithmetic can be compared with the dataset-driven implementation. The report example uses invented component scores, while the main application calculates its component scores from the built-in tracks and interactions.")

    add_heading(doc, "11 Testing and Validation", 1)
    add_para(doc, "Testing was performed at both the recommendation-logic level and the Streamlit interface level. The tests validate the original score-fusion calculation, dataset recommendations, metric generation, invalid input handling, and a basic user feedback action.")
    add_table(doc, ["Test", "Result"], [
        ("Report example order and scores", "Passed: B, A, C with 0.81, 0.72, 0.54."),
        ("Content versus collaborative weight", "Passed: ranking changes when alpha changes."),
        ("Unseen-track filtering", "Passed: selected users do not receive already-heard tracks."),
        ("Evaluation metric generation", "Passed: metrics and per-user rows produced."),
        ("Invalid input handling", "Passed: invalid weights and limits raise ValueError."),
        ("Streamlit AppTest", "Passed: zero exceptions; Like action increased history events."),
        ("Local smoke test", "Passed: http://localhost:8501 returned HTTP 200."),
    ], widths=[2.7, 3.8])
    add_caption(doc, "Table 10. Verification evidence for the implemented project.")
    add_para(doc, "The application can be run locally with Python and Streamlit. The repository includes requirements.txt, a one-click Windows launcher, unit tests, the data directory, and the original report source for traceability.")

    add_heading(doc, "12 Limitations and Responsible Use", 1)
    add_bullets(doc, [
        "The dataset is synthetic, small, and intentionally balanced for demonstration. Results cannot be generalized to real listeners.",
        "The feature values are illustrative audio-style descriptors, not measurements extracted from audio files.",
        "Jaccard similarity is a simple collaborative heuristic. Matrix factorization, nearest-neighbour models, or learned ranking could be stronger on larger data.",
        "The event weights are hand-selected. A real service would calibrate them against observed outcomes and product goals.",
        "Session feedback is not persisted. Restarting the local app resets the interactive feedback and playlist state.",
        "Offline evaluation can reward replaying known patterns and does not fully measure satisfaction, novelty, fairness, or exposure for emerging artists.",
        "Listening histories can reveal sensitive interests and routines. A production system would require clear consent, access controls, retention rules, and user controls.",
    ])

    add_heading(doc, "13 Future Improvements", 1)
    add_para(doc, "The next development stage should replace the synthetic dataset with a public, appropriately licensed listening-history dataset while preserving the same data contract. The recommendation pipeline can then be extended without changing the user workflow.")
    add_table(doc, ["Priority", "Improvement", "Expected benefit"], [
        ("High", "Use a larger public listening-history dataset and train/test split.", "More credible evaluation and stronger collaborative signal."),
        ("High", "Add time-aware profiles and recency decay.", "Better response to changing preferences."),
        ("High", "Add diversity-aware re-ranking and novelty controls.", "Reduce repetition and improve discovery."),
        ("Medium", "Persist feedback in a small database or user session store.", "Recommendations survive app restarts."),
        ("Medium", "Add audio embeddings or richer metadata.", "More expressive content similarity."),
        ("Medium", "Add experiment controls for alpha and ranking policies.", "Make trade-offs easier to compare."),
        ("Low", "Add authentication and privacy settings.", "Support multiple real users safely."),
    ], widths=[0.75, 3.45, 2.3])
    add_caption(doc, "Table 11. Prioritized improvement roadmap.")

    add_heading(doc, "14 Conclusion", 1)
    add_para(doc, "This project demonstrates a complete, local music recommendation workflow built from the concepts in the supplied case study. A selected listener is represented through positive interactions and track features. Content similarity and collaborative evidence are normalized and combined in a transparent hybrid score. The Streamlit interface lets the user inspect the ranking, change the balance between familiarity and discovery, provide feedback, save tracks, and review evaluation metrics.")
    add_para(doc, "The project meets its educational objective: it turns abstract recommender-system approaches into an executable system whose data, scores, and limitations can be inspected. Its current evaluation is intentionally modest because the dataset is synthetic. The most important next step is to use a larger, licensed listening-history dataset and evaluate the model with time-aware, diversity-aware, and user-centred measures.")

    add_heading(doc, "References", 1)
    add_para(doc, "[1] Supplied case study report, Music Recommendation Systems: A Case Study of Personalization Using Content-Based, Collaborative, and Hybrid Filtering, Manipal University Jaipur, 2026.")
    add_para(doc, "[2] Streamlit Documentation, Streamlit Community Cloud, https://docs.streamlit.io/deploy/streamlit-community-cloud")
    add_para(doc, "[3] Python Software Foundation, unittest documentation, https://docs.python.org/3/library/unittest.html")

    add_heading(doc, "Appendix A Local Execution", 1)
    add_para(doc, "1. Open the project folder.\n2. Double-click run_local.bat, or install dependencies with python -m pip install -r requirements.txt.\n3. Run python -m streamlit run app.py --server.port 8501.\n4. Open http://localhost:8501 in a browser.")
    add_para(doc, "The application starts with Aisha selected, but any listener in users.csv can be selected from the sidebar. The app does not require the user to upload data.")

    add_heading(doc, "Appendix B Repository Structure", 1)
    add_table(doc, ["Path", "Purpose"], [
        ("app.py", "Streamlit interface and session feedback workflow."),
        ("src/recommender.py", "Dataset loading, recommendation algorithms, and evaluation."),
        ("data/tracks.csv", "Built-in track catalogue and features."),
        ("data/users.csv", "Selectable demo listeners."),
        ("data/interactions.csv", "Listener interaction history."),
        ("tests/test_recommender.py", "Automated recommendation and evaluation tests."),
        ("run_local.bat", "One-click Windows local launcher."),
        ("presentation/", "Project presentation and deck builder."),
        ("docs/", "Source case study and this project report."),
    ], widths=[2.2, 4.3])

    # Keep document metadata neutral and professional.
    doc.core_properties.title = "Hybrid Music Recommendation Systems Project Report"
    doc.core_properties.subject = "Dataset-driven Streamlit recommender system implementation"
    doc.core_properties.author = "Shresth Srivastav and Tanishq Mehta"
    doc.core_properties.keywords = "music recommendation, Streamlit, hybrid filtering, recommender system"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build_report()
