"""
scripts/generate_dissertation_docx.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Parses the master Markdown thesis (docs/DISSERTATION_FINAL_THESIS.md) and
generates a comprehensive, publication-grade Microsoft Word dissertation (.docx)
strictly conforming to BITS Pilani WILP specifications (S1-26_CSIWZG628T).

Features:
- Multi-section page numbering:
  * Section 1: Cover Page & Title Page (no numbers)
  * Section 2: Preliminary Matter (Certificate through Symbols) -> Roman numerals (i, ii, iii...)
  * Section 3: Core Chapters (1-7), References, Appendices, Checklist -> Arabic numerals (1, 2, 3...)
- Standard BITS margins (1.5" Left for binding, 1.0" Right/Top/Bottom).
- Native Word Heading 1, 2, 3, 4 styles for dynamic Navigation Pane & TOC generation.
- 300 DPI high-resolution figure embedding with captions.
- Styled tables with dark navy headers, alternating row shading, and padded cells.
- Consolas code blocks and styled callouts for supervisor certificate & prompt templates.
- Complete official BITS Pilani 15-point checklist with student/supervisor signatures.
"""

import os
import re
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

_PARENT_DIR = Path(r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents")
_PROJECT_DIR = _PARENT_DIR / "Project"
_DOCS_DIR = _PROJECT_DIR / "docs"
_FIGURES_DIR = _DOCS_DIR / "figures"
_INPUT_MD = _DOCS_DIR / "DISSERTATION_FINAL_THESIS.md"
_OUTPUT_DOCX_PARENT = _PARENT_DIR / "Daipayan_Ghosal_2022wa86002_Final_Dissertation.docx"
_OUTPUT_DOCX_PROJECT = _DOCS_DIR / "Daipayan_Ghosal_2022wa86002_Final_Dissertation.docx"

# Palette
COLOR_PRIMARY_NAVY = RGBColor(10, 37, 64)       # #0A2540
COLOR_DARK_SLATE = RGBColor(30, 41, 59)        # #1E293B
COLOR_MUTED_GRAY = RGBColor(100, 116, 139)     # #64748B
COLOR_BODY_TEXT = RGBColor(31, 41, 55)         # #1F2937
HEX_HEADER_BLUE = "1E3A8A"                     # Deep Navy
HEX_ROW_ALT = "F8FAFC"                         # Light Slate
HEX_CODE_BG = "F1F5F9"                         # Gray
HEX_BORDER = "CBD5E1"                          # Subtle line

def set_cell_shading(cell, color_hex: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_page_number_field(run):
    fld1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    instr = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    fld2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    fld3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    run._r.append(fld3)

def format_inline_runs(paragraph, text: str, base_font="Times New Roman", base_size=Pt(12), base_color=COLOR_BODY_TEXT):
    # LaTeX replacements
    replacements = [
        (r"\tau", "τ"),
        (r"\rho", "ρ"),
        (r"\sigma", "σ"),
        (r"\alpha", "α"),
        (r"\beta", "β"),
        (r"\gamma", "γ"),
        (r"\leq", "≤"),
        (r"\geq", "≥"),
        (r"\approx", "≈"),
        (r"\times", "×"),
        (r"\cdot", "·"),
        (r"\in", "∈"),
        (r"\sum", "Σ"),
        (r"\rightarrow", "→"),
        (r"\to", "→"),
        (r"S_{\text{context}}", "S_context"),
        (r"S_{\text{norm}}", "S_norm"),
        (r"S_{\text{CVSS}}", "S_CVSS"),
        (r"w_C", "w_C"),
        (r"w_E", "w_E"),
        (r"w_A", "w_A"),
        (r"w_T", "w_T"),
        (r"w_X", "w_X"),
    ]
    for orig, rep in replacements:
        text = text.replace(orig, rep)
    text = text.replace("$", "")

    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) >= 4:
            run = paragraph.add_run(tok[2:-2])
            run.bold = True
            run.font.name = base_font
            run.font.size = base_size
            run.font.color.rgb = base_color
        elif tok.startswith("*") and tok.endswith("*") and len(tok) >= 2:
            run = paragraph.add_run(tok[1:-1])
            run.italic = True
            run.font.name = base_font
            run.font.size = base_size
            run.font.color.rgb = base_color
        elif tok.startswith("`") and tok.endswith("`") and len(tok) >= 2:
            run = paragraph.add_run(tok[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(base_size.pt * 0.9)
            run.font.color.rgb = COLOR_PRIMARY_NAVY
        else:
            run = paragraph.add_run(tok)
            run.font.name = base_font
            run.font.size = base_size
            run.font.color.rgb = base_color

def parse_markdown_table(table_lines):
    rows = []
    for line in table_lines:
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if all(re.match(r'^:?-+:?$', c) for c in cells if c):
            continue
        rows.append(cells)
    return rows

def add_table_to_doc(doc, table_data):
    if not table_data or len(table_data) < 1:
        return
    num_rows = len(table_data)
    num_cols = max(len(r) for r in table_data)

    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color=HEX_BORDER)

    # Header Row
    header_row = table.rows[0]
    trPr = header_row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for col_idx, cell_text in enumerate(table_data[0]):
        cell = header_row.cells[col_idx]
        set_cell_shading(cell, HEX_HEADER_BLUE)
        set_cell_margins(cell, top=130, bottom=130, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(cell_text.replace("**", ""))
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for row_idx in range(1, num_rows):
        row = table.rows[row_idx]
        trPr_row = row._tr.get_or_add_trPr()
        trPr_row.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        bg_color = HEX_ROW_ALT if row_idx % 2 == 1 else "FFFFFF"
        for col_idx in range(num_cols):
            cell = row.cells[col_idx]
            set_cell_shading(cell, bg_color)
            set_cell_margins(cell, top=90, bottom=90, left=130, right=130)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            cell_text = table_data[row_idx][col_idx] if col_idx < len(table_data[row_idx]) else ""
            format_inline_runs(p, cell_text, base_font="Times New Roman", base_size=Pt(9.5))

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)

def add_callout_box(doc, text: str):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_shading(cell, HEX_ROW_ALT)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_HEADER_BLUE}"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.3
    format_inline_runs(p, text, base_font="Times New Roman", base_size=Pt(11))

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)

def add_code_block(doc, code_lines):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_shading(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=100, bottom=100, left=160, right=160)
    set_table_borders(table, color=HEX_BORDER, sz="4")

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    for idx, line in enumerate(code_lines):
        run = p.add_run(line + ("\n" if idx < len(code_lines) - 1 else ""))
        run.font.name = "Consolas"
        run.font.size = Pt(8.8)
        run.font.color.rgb = COLOR_PRIMARY_NAVY

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)

def add_embedded_figure(doc, img_rel_path: str, caption_text: str = ""):
    """Embeds an image from docs/figures/ centered with caption."""
    filename = Path(img_rel_path).name
    img_file = _FIGURES_DIR / filename
    if not img_file.exists():
        print(f"Warning: Figure file not found at {img_file}")
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(12)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(str(img_file), width=Inches(5.8))

    if caption_text:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption_text.replace("*", ""))
        r_cap.bold = True
        r_cap.italic = True
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(10)
        r_cap.font.color.rgb = COLOR_DARK_SLATE

def build_cover_page(doc):
    """Section 1: Outer Cover Page."""
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(72)
    p_title.paragraph_format.space_after = Pt(24)
    p_title.paragraph_format.line_spacing = 1.3
    r = p_title.add_run("EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(18)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_after = Pt(48)
    r = p_course.add_run("CSIW ZG628T DISSERTATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.color.rgb = COLOR_DARK_SLATE

    p_student = doc.add_paragraph()
    p_student.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_student.paragraph_format.space_after = Pt(6)
    r = p_student.add_run("Daipayan Ghosal")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)

    p_id = doc.add_paragraph()
    p_id.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_id.paragraph_format.space_after = Pt(48)
    r = p_id.add_run("BITS ID No.: 2022wa86002")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p_loc_label = doc.add_paragraph()
    p_loc_label.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc_label.paragraph_format.space_after = Pt(4)
    r = p_loc_label.add_run("Dissertation Work Carried Out At:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_after = Pt(60)
    r = p_loc.add_run("Wipro Limited")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(4)
    r = p_inst.add_run("BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p_place = doc.add_paragraph()
    p_place.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_place.paragraph_format.space_after = Pt(4)
    r = p_place.add_run("Pilani (Rajasthan) India")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_after = Pt(0)
    r = p_date.add_run("November, 2026")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    doc.add_page_break()

def build_title_page(doc):
    """Section 1: Title Page (Inner Cover Page)."""
    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_before = Pt(36)
    p_course.paragraph_format.space_after = Pt(18)
    r = p_course.add_run("CSIW ZG628T DISSERTATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.color.rgb = COLOR_DARK_SLATE

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(18)
    p_title.paragraph_format.line_spacing = 1.3
    r = p_title.add_run("EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(4)
    r = p_sub.add_run("Submitted in partial fulfilment of the requirements of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_after = Pt(24)
    r = p_deg.add_run("M.Tech in Computing Systems & Infrastructure Degree Program\n(BITS - WIPRO Collaborative Programme - WIMS)")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_after = Pt(2)
    r = p_by.add_run("by")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    p_stu = doc.add_paragraph()
    p_stu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_stu.paragraph_format.space_after = Pt(2)
    r = p_stu.add_run("Daipayan Ghosal")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)

    p_id = doc.add_paragraph()
    p_id.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_id.paragraph_format.space_after = Pt(24)
    r = p_id.add_run("ID No. 2022wa86002\n(Email: 2022wa86002@wilp.bits-pilani.ac.in)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    p_sup_lbl = doc.add_paragraph()
    p_sup_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sup_lbl.paragraph_format.space_after = Pt(2)
    r = p_sup_lbl.add_run("Under the supervision of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sup.paragraph_format.space_after = Pt(12)
    r = p_sup.add_run("Ms. Nidhi Kashyap\nAnalyst, Cybersecurity Practice\nWipro Limited, Pune (Email: nidhi.kashyap@wipro.com)")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    p_exm_lbl = doc.add_paragraph()
    p_exm_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_exm_lbl.paragraph_format.space_after = Pt(2)
    r = p_exm_lbl.add_run("Additional Examiner")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p_exm = doc.add_paragraph()
    p_exm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_exm.paragraph_format.space_after = Pt(24)
    r = p_exm.add_run("Mr. Satish Banigole\nProject Manager, Wipro Limited, Pune (Email: satish.banigole@wipro.com)")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_after = Pt(16)
    r = p_loc.add_run("Dissertation work carried out at\nWipro Limited, Pune / Bangalore")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(4)
    r = p_inst.add_run("BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE\nPILANI (RAJASTHAN)")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_after = Pt(0)
    r = p_date.add_run("November, 2026")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

def build_dissertation_docx():
    print("Reading master markdown thesis from:", _INPUT_MD)
    with open(_INPUT_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = docx.Document()

    # Configure Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = COLOR_BODY_TEXT
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Configure Heading Styles
    h1_style = doc.styles['Heading 1']
    h1_style.font.name = 'Times New Roman'
    h1_style.font.size = Pt(16)
    h1_style.font.bold = True
    h1_style.font.color.rgb = COLOR_PRIMARY_NAVY

    h2_style = doc.styles['Heading 2']
    h2_style.font.name = 'Times New Roman'
    h2_style.font.size = Pt(14)
    h2_style.font.bold = True
    h2_style.font.color.rgb = COLOR_DARK_SLATE

    h3_style = doc.styles['Heading 3']
    h3_style.font.name = 'Times New Roman'
    h3_style.font.size = Pt(12)
    h3_style.font.bold = True
    h3_style.font.color.rgb = COLOR_DARK_SLATE

    h4_style = doc.styles['Heading 4']
    h4_style.font.name = 'Times New Roman'
    h4_style.font.size = Pt(12)
    h4_style.font.bold = True
    h4_style.font.italic = True
    h4_style.font.color.rgb = COLOR_DARK_SLATE

    # =========================================================================
    # SECTION 1: COVER PAGE & TITLE PAGE (INNER COVER)
    # =========================================================================
    s1 = doc.sections[0]
    s1.top_margin = Inches(1.0)
    s1.bottom_margin = Inches(1.0)
    s1.left_margin = Inches(1.5)
    s1.right_margin = Inches(1.0)
    s1.page_width = Inches(8.27)
    s1.page_height = Inches(11.69)
    s1.different_first_page_header_footer = True

    build_cover_page(doc)
    build_title_page(doc)

    # =========================================================================
    # SECTION 2: PRELIMINARY PAGES (ROMAN NUMERALS i, ii, iii...)
    # =========================================================================
    s2 = doc.add_section()
    s2.top_margin = Inches(1.0)
    s2.bottom_margin = Inches(1.0)
    s2.left_margin = Inches(1.5)
    s2.right_margin = Inches(1.0)
    s2.page_width = Inches(8.27)
    s2.page_height = Inches(11.69)
    s2.header.is_linked_to_previous = False
    s2.footer.is_linked_to_previous = False

    # Set roman page numbering starting at i
    sectPr2 = s2._sectPr
    pgNum2 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="roman" w:start="1"/>')
    sectPr2.append(pgNum2)

    # Preliminary Header
    h2_p = s2.header.paragraphs[0]
    h2_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr2 = h2_p.add_run("M.Tech Dissertation | BITS Pilani (WILP) — S1-26_CSIWZG628T")
    r_hdr2.font.name = "Times New Roman"
    r_hdr2.font.size = Pt(8.5)
    r_hdr2.font.italic = True
    r_hdr2.font.color.rgb = COLOR_MUTED_GRAY

    # Preliminary Footer
    f2_p = s2.footer.paragraphs[0]
    f2_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f2 = f2_p.add_run()
    r_f2.font.name = "Times New Roman"
    r_f2.font.size = Pt(10)
    r_f2.font.color.rgb = COLOR_DARK_SLATE
    add_page_number_field(r_f2)

    # Find where preliminary matter starts
    cert_idx = md_text.find("## CERTIFICATE FROM THE SUPERVISOR")
    ch1_idx = md_text.find("# CHAPTER 1: INTRODUCTION")

    prelim_text = md_text[cert_idx:ch1_idx]
    main_text = md_text[ch1_idx:]

    def process_markdown_block(block_text, target_doc):
        lines = block_text.splitlines()
        i = 0
        in_code = False
        code_buf = []
        in_tbl = False
        tbl_buf = []

        page_breaks = [
            "## CERTIFICATE FROM THE SUPERVISOR",
            "## ACKNOWLEDGEMENTS",
            "## ABSTRACT",
            "## TABLE OF CONTENTS",
            "## LIST OF FIGURES",
            "## LIST OF TABLES",
            "## LIST OF ABBREVIATIONS & SYMBOLS",
            "# CHAPTER 1: INTRODUCTION",
            "# CHAPTER 2: LITERATURE REVIEW AND RELATED WORK",
            "# CHAPTER 3: SYSTEM ARCHITECTURE AND MATHEMATICAL FORMULATION",
            "# CHAPTER 4: IMPLEMENTATION AND SYSTEM ENGINEERING",
            "# CHAPTER 5: EMPIRICAL RESULTS AND EVALUATION",
            "# CHAPTER 6: DISCUSSION AND OPERATIONAL IMPACT",
            "# CHAPTER 7: CONCLUSIONS AND FUTURE WORK",
            "# REFERENCES",
            "## APPENDIX A: COMPLETE DATA DICTIONARY & SCHEMA DEFINITIONS",
            "## APPENDIX B: ENTERPRISE ASSET INVENTORY SPECIFICATIONS",
            "## APPENDIX C: PROMPT TEMPLATES & SYSTEM INSTRUCTIONS",
            "## APPENDIX D: AUTOMATED UNIT TEST SUITE SUMMARY",
            "## LIST OF PUBLICATIONS / CONFERENCE PRESENTATIONS",
            "## CHECK LIST OF ITEMS FOR FINAL REPORT",
        ]

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if '<div style="page-break-after: always;"></div>' in stripped:
                i += 1
                continue
            if stripped == "---":
                i += 1
                continue

            # Code blocks
            if stripped.startswith("```"):
                if in_code:
                    add_code_block(target_doc, code_buf)
                    code_buf = []
                    in_code = False
                else:
                    in_code = True
                i += 1
                continue

            if in_code:
                code_buf.append(line)
                i += 1
                continue

            # Tables
            if stripped.startswith("|") and stripped.endswith("|"):
                if not in_tbl:
                    in_tbl = True
                    tbl_buf = []
                tbl_buf.append(stripped)
                i += 1
                continue
            elif in_tbl:
                tbl_data = parse_markdown_table(tbl_buf)
                add_table_to_doc(target_doc, tbl_data)
                tbl_buf = []
                in_tbl = False

            # Empty lines
            if not stripped:
                i += 1
                continue

            # Figures ![alt](figures/...)
            m_img = re.match(r'^!\[(.*?)\]\((.*?)\)', stripped)
            if m_img:
                img_caption = m_img.group(1)
                img_path = m_img.group(2)
                # Next line might be caption
                next_caption = ""
                if i + 1 < len(lines) and lines[i+1].strip().startswith("*Figure "):
                    next_caption = lines[i+1].strip()
                    i += 1
                add_embedded_figure(target_doc, img_path, next_caption or img_caption)
                i += 1
                continue

            # Section page breaks (skip if at very start of block)
            if i > 5:
                for pb in page_breaks:
                    if stripped == pb or stripped.startswith(pb + " "):
                        target_doc.add_page_break()
                        break

            # Headings
            if stripped.startswith("# CHAPTER") or stripped.startswith("# REFERENCES"):
                p = target_doc.add_paragraph(style='Heading 1')
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(8)
                p.paragraph_format.keep_with_next = True
                title_text = re.sub(r'^#\s+', '', stripped)
                r = p.add_run(title_text)
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(16)
                r.font.color.rgb = COLOR_PRIMARY_NAVY
                i += 1
                continue

            if stripped.startswith("## "):
                p = target_doc.add_paragraph(style='Heading 2')
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                title_text = re.sub(r'^##\s+', '', stripped)
                r = p.add_run(title_text)
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(14)
                r.font.color.rgb = COLOR_DARK_SLATE
                i += 1
                continue

            if stripped.startswith("### "):
                p = target_doc.add_paragraph(style='Heading 3')
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.keep_with_next = True
                title_text = re.sub(r'^###\s+', '', stripped).replace("**", "")
                r = p.add_run(title_text)
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.font.color.rgb = COLOR_DARK_SLATE
                i += 1
                continue

            if stripped.startswith("#### "):
                p = target_doc.add_paragraph(style='Heading 4')
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.keep_with_next = True
                title_text = re.sub(r'^####\s+', '', stripped).replace("**", "")
                r = p.add_run(title_text)
                r.bold = True
                r.font.italic = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.font.color.rgb = COLOR_DARK_SLATE
                i += 1
                continue

            # Blockquotes (> ...)
            if stripped.startswith(">"):
                quote_text = re.sub(r'^>\s*', '', stripped)
                add_callout_box(target_doc, quote_text)
                i += 1
                continue

            # Bullet List Items (- or *)
            if (stripped.startswith("- ") or stripped.startswith("* ")) and not stripped.startswith("**"):
                p = target_doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.35)
                p.paragraph_format.first_line_indent = Inches(-0.2)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.3
                r_bullet = p.add_run("▪  ")
                r_bullet.font.name = "Times New Roman"
                r_bullet.font.size = Pt(10)
                r_bullet.font.color.rgb = COLOR_PRIMARY_NAVY
                item_text = stripped[2:].strip()
                format_inline_runs(p, item_text)
                i += 1
                continue

            # Numbered List Items
            m_num = re.match(r'^(\d+\.|\(\d+\)|\[\d+\])\s+(.*)', stripped)
            if m_num:
                prefix = m_num.group(1)
                content_text = m_num.group(2)
                p = target_doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                p.paragraph_format.first_line_indent = Inches(-0.3)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.3
                r_num = p.add_run(prefix + " ")
                r_num.bold = True
                r_num.font.name = "Times New Roman"
                r_num.font.size = Pt(11)
                r_num.font.color.rgb = COLOR_PRIMARY_NAVY
                format_inline_runs(p, content_text)
                i += 1
                continue

            # Regular Paragraph
            p = target_doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            format_inline_runs(p, stripped)
            i += 1

        if in_tbl and tbl_buf:
            tbl_data = parse_markdown_table(tbl_buf)
            add_table_to_doc(target_doc, tbl_data)

    # Process Preliminary Matter
    print("Processing preliminary pages (Section 2)...")
    process_markdown_block(prelim_text, doc)

    # =========================================================================
    # SECTION 3: CORE CHAPTERS & END MATTER (DECIMAL NUMERALS 1, 2, 3...)
    # =========================================================================
    print("Processing core chapters and end matter (Section 3)...")
    s3 = doc.add_section()
    s3.top_margin = Inches(1.0)
    s3.bottom_margin = Inches(1.0)
    s3.left_margin = Inches(1.5)
    s3.right_margin = Inches(1.0)
    s3.page_width = Inches(8.27)
    s3.page_height = Inches(11.69)
    s3.header.is_linked_to_previous = False
    s3.footer.is_linked_to_previous = False

    # Set decimal page numbering starting at 1
    sectPr3 = s3._sectPr
    pgNum3 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>')
    sectPr3.append(pgNum3)

    # Core Header
    h3_p = s3.header.paragraphs[0]
    h3_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr3 = h3_p.add_run("M.Tech Dissertation | BITS Pilani (WILP) — S1-26_CSIWZG628T")
    r_hdr3.font.name = "Times New Roman"
    r_hdr3.font.size = Pt(8.5)
    r_hdr3.font.italic = True
    r_hdr3.font.color.rgb = COLOR_MUTED_GRAY

    # Core Footer
    f3_p = s3.footer.paragraphs[0]
    f3_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f3 = f3_p.add_run()
    r_f3.font.name = "Times New Roman"
    r_f3.font.size = Pt(10)
    r_f3.font.color.rgb = COLOR_DARK_SLATE
    add_page_number_field(r_f3)

    process_markdown_block(main_text, doc)

    # Save to both target locations
    print("Saving formal dissertation Word document to:", _OUTPUT_DOCX_PARENT)
    doc.save(_OUTPUT_DOCX_PARENT)
    print("Saving copy of formal dissertation Word document to:", _OUTPUT_DOCX_PROJECT)
    doc.save(_OUTPUT_DOCX_PROJECT)
    print("Thesis docx build completed successfully!")

if __name__ == "__main__":
    build_dissertation_docx()
