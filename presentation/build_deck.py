"""Build a small editable PowerPoint deck with standard Open XML.

The normal presentation runtime was unavailable in this Windows session, so this
uses only the Python standard library and keeps every slide element editable.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


OUT = Path(__file__).with_name("Music_Recommendation_Systems_Project.pptx")
EMU_PER_PX = 9525


def esc(value: object) -> str:
    return escape(str(value), quote=True)


def off(x: int, y: int) -> str:
    return f'<a:off x="{x * EMU_PER_PX}" y="{y * EMU_PER_PX}"/>'


def ext(w: int, h: int) -> str:
    return f'<a:ext cx="{w * EMU_PER_PX}" cy="{h * EMU_PER_PX}"/>'


def shape(shape_id: int, name: str, x: int, y: int, w: int, h: int, *, fill: str | None = None, line: str | None = None, text: str | None = None, size: int = 20, color: str = "1D2B27", bold: bool = False, align: str = "l") -> str:
    fill_xml = '<a:noFill/>' if fill is None else f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    line_xml = '<a:noFill/>' if line is None else f'<a:solidFill><a:srgbClr val="{line}"/></a:solidFill>'
    sppr = f'<p:spPr><a:xfrm>{off(x, y)}{ext(w, h)}</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill_xml}<a:ln>{line_xml}</a:ln></p:spPr>'
    tx = ""
    if text is not None:
        paragraphs = text.split("\n")
        p_xml = []
        for paragraph in paragraphs:
            p_xml.append(
                f'<a:p><a:pPr algn="{align}"/><a:r><a:rPr lang="en-US" sz="{size * 100}" b="{str(bold).lower()}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>{esc(paragraph)}</a:t></a:r><a:endParaRPr lang="en-US" sz="{size * 100}"/></a:p>'
            )
        tx = f'<p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{"".join(p_xml)}</p:txBody>'
    return f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>{sppr}{tx}</p:sp>'


def slide_xml(slide_shapes: list[str], background: str = "FAF9F6") -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>{off(0, 0)}{ext(1280, 720)}</a:xfrm></p:grpSpPr>{''.join(slide_shapes)}</p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def title(slide_id: int, heading: str, kicker: str) -> list[str]:
    return [
        shape(slide_id, "Kicker", 72, 40, 460, 28, text=kicker.upper(), size=13, color="1F6F5B", bold=True),
        shape(slide_id + 1, "Title", 72, 78, 1120, 68, text=heading, size=34, color="1D2B27", bold=True),
        shape(slide_id + 2, "Rule", 72, 160, 1136, 3, fill="1F6F5B", line="1F6F5B"),
    ]


def build_slides() -> list[str]:
    slides: list[str] = []

    slides.append(slide_xml([
        shape(2, "Accent", 0, 0, 1280, 720, fill="1F6F5B", line="1F6F5B"),
        shape(3, "Eyebrow", 80, 88, 720, 30, text="CASE STUDY PROJECT", size=16, color="D9F0E6", bold=True),
        shape(4, "Title", 80, 145, 970, 150, text="Hybrid Music\nRecommendation Systems", size=46, color="FFFFFF", bold=True),
        shape(5, "Subtitle", 84, 340, 820, 86, text="An interactive Streamlit demonstration of content-based, collaborative, and hybrid filtering", size=22, color="EAF6F0"),
        shape(6, "Meta", 84, 565, 900, 46, text="Based on the supplied case study report  •  2026", size=16, color="D9F0E6"),
        shape(7, "AccentLine", 84, 500, 170, 8, fill="F2C14E", line="F2C14E"),
    ]))

    s = title(10, "The recommendation problem", "01  Context")
    s += [
        shape(20, "Problem", 72, 208, 500, 155, fill="FFFFFF", line="D8E5DF", text="Millions of tracks\n\nA listener has limited time and incomplete knowledge of the catalogue.", size=23, color="1D2B27", bold=True),
        shape(21, "Goal", 72, 400, 500, 155, fill="EEF7F2", line="B9DCCB", text="The system must rank songs that are likely to satisfy the listener while preserving discovery and diversity.", size=23, color="1D2B27", bold=True),
        shape(22, "Arrow", 620, 318, 70, 70, fill="F2C14E", line="F2C14E", text="→", size=38, color="1D2B27", bold=True, align="c"),
        shape(23, "Question", 760, 228, 420, 240, fill="1D2B27", line="1D2B27", text="How can track characteristics and listening behaviour be combined to provide relevant, personalised, and diverse recommendations?", size=25, color="FFFFFF", bold=True),
        shape(24, "Scope", 760, 510, 420, 54, text="The report is conceptual; the scores are hypothetical.", size=16, color="1F6F5B", bold=True),
    ]
    slides.append(slide_xml(s))

    s = title(30, "Three complementary approaches", "02  Methods")
    s += [
        shape(40, "Content", 72, 215, 350, 320, fill="EAF6F0", line="B9DCCB", text="CONTENT-BASED\n\nRecommends tracks whose characteristics resemble items the listener already likes.\n\n+ explainable\n− can become repetitive", size=20, color="1D2B27", bold=True),
        shape(41, "Collaborative", 465, 215, 350, 320, fill="FFF7E1", line="F2D68C", text="COLLABORATIVE\n\nLearns from interactions by listeners with similar behaviour.\n\n+ unexpected discovery\n− cold start and sparsity", size=20, color="1D2B27", bold=True),
        shape(42, "Hybrid", 858, 215, 350, 320, fill="EAF0FF", line="B5C6F2", text="HYBRID\n\nCombines content signals with collaborative patterns, often adapting to data availability.\n\n+ balances weaknesses\n− more design choices", size=20, color="1D2B27", bold=True),
        shape(43, "Takeaway", 72, 585, 1136, 48, text="The case study uses hybrid filtering as the implementation direction for a transparent demonstration.", size=18, color="1F6F5B", bold=True),
    ]
    slides.append(slide_xml(s))

    s = title(50, "The hybrid score makes the trade-off visible", "03  Score fusion")
    s += [
        shape(60, "Equation", 110, 215, 1060, 90, fill="1D2B27", line="1D2B27", text="Hybrid Score = α × Content Score + (1 − α) × Collaborative Score", size=30, color="FFFFFF", bold=True, align="c"),
        shape(61, "Alpha", 120, 350, 265, 105, fill="F2C14E", line="F2C14E", text="α = 0.4\nContent 40%", size=24, color="1D2B27", bold=True, align="c"),
        shape(62, "Collab", 495, 350, 265, 105, fill="D9F0E6", line="B9DCCB", text="1 − α = 0.6\nCollaborative 60%", size=24, color="1D2B27", bold=True, align="c"),
        shape(63, "Result", 870, 350, 265, 105, fill="EAF0FF", line="B5C6F2", text="Track B\n0.81 → #1", size=24, color="1D2B27", bold=True, align="c"),
        shape(64, "TableHeader", 120, 510, 1015, 42, fill="1F6F5B", line="1F6F5B", text="CANDIDATE                         CONTENT                 COLLABORATIVE                 HYBRID", size=15, color="FFFFFF", bold=True),
        shape(65, "TableRows", 120, 552, 1015, 78, fill="FFFFFF", line="D8E5DF", text="Track B: indie folk                 0.75                         0.85                         0.81\nTrack A: acoustic pop             0.90                         0.60                         0.72\nTrack C: electronic dance       0.30                         0.70                         0.54", size=16, color="1D2B27"),
    ]
    slides.append(slide_xml(s))

    s = title(70, "What the Streamlit project delivers", "04  Product")
    s += [
        shape(80, "Flow1", 72, 230, 255, 126, fill="1F6F5B", line="1F6F5B", text="1\nChoose α and a genre", size=22, color="FFFFFF", bold=True, align="c"),
        shape(81, "Arrow1", 350, 265, 55, 55, fill="F2C14E", line="F2C14E", text="→", size=32, color="1D2B27", bold=True, align="c"),
        shape(82, "Flow2", 430, 230, 255, 126, fill="EAF6F0", line="B9DCCB", text="2\nRank candidate tracks", size=22, color="1D2B27", bold=True, align="c"),
        shape(83, "Arrow2", 708, 265, 55, 55, fill="F2C14E", line="F2C14E", text="→", size=32, color="1D2B27", bold=True, align="c"),
        shape(84, "Flow3", 788, 230, 255, 126, fill="EAF0FF", line="B5C6F2", text="3\nInspect why each appears", size=22, color="1D2B27", bold=True, align="c"),
        shape(85, "Controls", 72, 420, 520, 170, fill="FFFFFF", line="D8E5DF", text="Interactive controls\n\n• content weight α\n• genre filter\n• recommendation count", size=20, color="1D2B27", bold=True),
        shape(86, "Guardrails", 640, 420, 568, 170, fill="FFF7E1", line="F2D68C", text="Transparent scope\n\nIllustrative catalogue only. No Spotify scraping, private-algorithm claims, or API key required.", size=20, color="1D2B27", bold=True),
    ]
    slides.append(slide_xml(s))

    s = title(90, "Evaluation and responsible use", "05  Findings")
    s += [
        shape(100, "Metrics", 72, 220, 520, 270, fill="EAF6F0", line="B9DCCB", text="Precision@K\nRelevant recommendations in top K ÷ K\n\nRecall@K\nRelevant recommendations in top K ÷ all relevant test items", size=23, color="1D2B27", bold=True),
        shape(101, "Limits", 640, 220, 568, 270, fill="FFFFFF", line="D8E5DF", text="Metrics are not the whole product\n\n• offline splits do not equal live satisfaction\n• unplayed does not necessarily mean disliked\n• diversity, novelty, privacy, and control matter\n• changing preferences need recent signals", size=21, color="1D2B27", bold=True),
        shape(102, "Conclusion", 72, 560, 1136, 56, fill="1D2B27", line="1D2B27", text="A useful recommender balances relevance with discovery, diversity, timeliness, transparency, and user control.", size=21, color="FFFFFF", bold=True, align="c"),
    ]
    slides.append(slide_xml(s))

    return slides


CONTENT_TYPES = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{''.join(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, 7))}
</Types>'''


ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>'''


PRESENTATION_RELS = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
{''.join(f'<Relationship Id="rId{i+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1, 7))}
</Relationships>'''


PRESENTATION = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>{}</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle><a:defPPr/><a:lvl1pPr marL="0" algn="l"/><a:lvl2pPr marL="0" algn="l"/></p:defaultTextStyle></p:presentation>'''.format(''.join(f'<p:sldId id="{255+i}" r:id="rId{i+3}"/>' for i in range(6)))


MASTER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld name="Master"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm/></p:grpSpPr></p:spTree></p:cSld><p:clrMap accent1="1F6F5B" accent2="F2C14E" bg1="FFFFFF" bg2="FAF9F6" tx1="1D2B27" tx2="FFFFFF" hlink="0000FF" folHlink="800080"/></p:sldMaster>'''


LAYOUT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm/></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''


THEME = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Music Recommender"><a:themeElements><a:clrScheme name="Custom"><a:dk1><a:srgbClr val="1D2B27"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F6F5B"/></a:dk2><a:lt2><a:srgbClr val="FAF9F6"/></a:lt2><a:accent1><a:srgbClr val="1F6F5B"/></a:accent1><a:accent2><a:srgbClr val="F2C14E"/></a:accent2><a:accent3><a:srgbClr val="EAF0FF"/></a:accent3><a:accent4><a:srgbClr val="EEF7F2"/></a:accent4><a:accent5><a:srgbClr val="D8E5DF"/></a:accent5><a:accent6><a:srgbClr val="B9DCCB"/></a:accent6><a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink></a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Arial"/></a:minorFont></a:fontScheme><a:fmtScheme name="Plain"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>'''


def main() -> None:
    slides = build_slides()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("ppt/presentation.xml", PRESENTATION)
        z.writestr("ppt/_rels/presentation.xml.rels", PRESENTATION_RELS)
        z.writestr("ppt/slideMasters/slideMaster1.xml", MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>')
        z.writestr("ppt/slideLayouts/slideLayout1.xml", LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>')
        z.writestr("ppt/theme/theme1.xml", THEME)
        for index, slide in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{index}.xml", slide)
            z.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>')
    print(OUT)


if __name__ == "__main__":
    main()
