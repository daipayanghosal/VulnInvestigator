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
- 300 DPI high-resolution figure embedding with captions (no duplicates, no overlapping text).
- Beautifully formatted mathematical typography (Cambria Math, centered display equations, piecewise cases).
- Styled tables with dark navy headers, alternating row shading, and padded cells.
- Consolas code blocks and styled callouts for supervisor certificate & prompt templates.
- Complete checklist with student declaration and supervisor endorsement signature blocks.
"""

import os
import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
_PARENT_DIR = _PROJECT_DIR.parent

# Documents dir is the parent directory
_DOCS_DIR = _PARENT_DIR
_FIGURES_DIR = _DOCS_DIR / "figures"
_INPUT_MD = _DOCS_DIR / "DISSERTATION_FINAL_THESIS.md"
_OUTPUT_DOCX_PARENT = _PARENT_DIR / "Daipayan_Ghosal_2022wa86002_Final_Dissertation.docx"
_OUTPUT_DOCX_PROJECT = _PROJECT_DIR / "docs" / "Daipayan_Ghosal_2022wa86002_Final_Dissertation.docx"

# Color Palette: Oxford Navy & Slate (Academic Professional)
COLOR_PRIMARY_NAVY = RGBColor(10, 37, 64)       # Deep Navy #0A2540
COLOR_DARK_SLATE   = RGBColor(30, 41, 59)       # Dark Slate #1E293B
COLOR_BODY_TEXT    = RGBColor(15, 23, 42)       # Text Charcoal #0F172A
COLOR_MUTED_GRAY   = RGBColor(100, 116, 139)    # Muted Gray #64748B
COLOR_ACCENT_BLUE  = RGBColor(37, 99, 235)      # Royal Accent #2563EB

HEX_HEADER_BLUE    = "0A2540"
HEX_ROW_ALT        = "F8FAFC"
HEX_BORDER         = "CBD5E1"
HEX_CODE_BG        = "F1F5F9"

def set_cell_shading(cell, color_hex: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
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

def clean_math_text(text: str) -> str:
    """Converts LaTeX math expressions into clean unicode typography."""
    replacements = [
        (r"\tau", "τ"),
        (r"\rho", "ρ"),
        (r"\sigma", "σ"),
        (r"\alpha", "α"),
        (r"\beta", "β"),
        (r"\gamma", "γ"),
        (r"\Delta", "Δ"),
        (r"\delta", "δ"),
        (r"\lambda", "λ"),
        (r"\ge", "≥"),
        (r"\geq", "≥"),
        (r"\le", "≤"),
        (r"\leq", "≤"),
        (r"\ne", "≠"),
        (r"\neq", "≠"),
        (r"\approx", "≈"),
        (r"\times", "×"),
        (r"\cdot", "·"),
        (r"\in", "∈"),
        (r"\notin", "∉"),
        (r"\sum", "Σ"),
        (r"\forall", "∀"),
        (r"\mathbb{I}", "𝕀"),
        (r"\rightarrow", "→"),
        (r"\leftarrow", "←"),
        (r"\to", "→"),
        (r"\%", "%"),
        (r"\_", "_"),
        (r"\quad", "   "),
        (r"\left(", "("),
        (r"\right)", ")"),
        (r"\left[", "["),
        (r"\right]", "]"),
        (r"\max", "max"),
        (r"\min", "min"),
        (r"S_{\text{cvss}}", "S_cvss"),
        (r"S_{\text{kev}}", "S_kev"),
        (r"S_{\text{asset}}", "S_asset"),
        (r"S_{\text{exp}}", "S_exp"),
        (r"w_{\text{cvss}}", "w_cvss"),
        (r"w_{\text{kev}}", "w_kev"),
        (r"w_{\text{asset}}", "w_asset"),
        (r"w_{\text{exp}}", "w_exp"),
        (r"R_{\text{final}}", "R_final"),
        (r"\text{Rank}_{\text{cvss}}", "Rank_cvss"),
        (r"\text{Rank}_{\text{ctx}}", "Rank_ctx"),
        (r"\text{Tier}", "Tier"),
        (r"\text{Exposure}", "Exposure"),
        (r"\text{Band}", "Band"),
        (r"\text{CitationRate}", "CitationRate"),
        (r"\text{ClaimSupportRate}", "ClaimSupportRate"),
        (r"\text{HallucinationRate}", "HallucinationRate"),
        (r"\text{ConfidenceScore}", "ConfidenceScore"),
        (r"\text{Citations}", "Citations"),
        (r"\text{HasUnsupported}", "HasUnsupported"),
        (r"\text{HasWarning}", "HasWarning"),
        (r"\text{CISA\_KEV}", "CISA_KEV"),
    ]
    for orig, rep in replacements:
        text = text.replace(orig, rep)
    
    # Strip \text{...} wrappers
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    # Strip \textbf{...} wrappers
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    # Format fractions \frac{A}{B} -> (A) / (B)
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1) / (\2)', text)
    # Strip dollar signs
    text = text.replace("$", "")
    return text

def format_inline_runs(paragraph, text: str, base_font="Times New Roman", base_size=Pt(12), base_color=COLOR_BODY_TEXT):
    text = clean_math_text(text)

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

def format_display_equation(doc, math_lines):
    full_math = "\n".join(math_lines)
    full_math = re.sub(r'^\$\$\s*', '', full_math)
    full_math = re.sub(r'\s*\$\$$', '', full_math)

    if r'\begin{cases}' in full_math:
        m = re.match(r'(.*?)\s*=\s*\\begin\{cases\}(.*?)\\end\{cases\}', full_math, re.DOTALL)
        if m:
            lhs = clean_math_text(m.group(1).strip())
            inner = m.group(2).strip()
            case_lines = []
            for cline in inner.split(r'\\'):
                cline = cline.strip()
                if not cline:
                    continue
                parts = [clean_math_text(p.strip()) for p in cline.split('&')]
                if len(parts) == 2:
                    case_lines.append(f"  {parts[0]:<14}  {parts[1]}")
                else:
                    case_lines.append("  " + "  ".join(parts))

            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.2

            r_lhs = p.add_run(f"{lhs} = {{\n")
            r_lhs.font.name = "Cambria Math"
            r_lhs.font.size = Pt(11.5)
            r_lhs.bold = True
            r_lhs.font.color.rgb = COLOR_PRIMARY_NAVY

            for idx, cl in enumerate(case_lines):
                r_case = p.add_run(cl + ("\n" if idx < len(case_lines) - 1 else ""))
                r_case.font.name = "Cambria Math"
                r_case.font.size = Pt(11)
                r_case.font.color.rgb = COLOR_BODY_TEXT
            return

    cleaned = clean_math_text(full_math)
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.2

    run = p.add_run(cleaned)
    run.font.name = "Cambria Math"
    run.font.size = Pt(12)
    run.bold = True
    run.font.color.rgb = COLOR_PRIMARY_NAVY

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
        clean_text = clean_math_text(cell_text.replace("**", ""))
        run = p.add_run(clean_text)
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

def add_code_block(doc, code_lines, caption: str = ""):
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

    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(8)
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = "Times New Roman"
        run_cap.font.size = Pt(10)
        run_cap.italic = True
        run_cap.font.color.rgb = COLOR_DARK_SLATE
    else:
        p_spacer = doc.add_paragraph()
        p_spacer.paragraph_format.space_before = Pt(0)
        p_spacer.paragraph_format.space_after = Pt(6)

def add_embedded_figure(doc, img_rel_path: str, caption_text: str = ""):
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
        run_cap = p_cap.add_run(caption_text)
        run_cap.font.name = "Times New Roman"
        run_cap.font.size = Pt(10)
        run_cap.italic = True
        run_cap.font.color.rgb = COLOR_DARK_SLATE

def build_dissertation_docx():
    print(f"Reading thesis markdown from: {_INPUT_MD}")
    if not _INPUT_MD.exists():
        raise FileNotFoundError(f"Input file not found: {_INPUT_MD}")

    with open(_INPUT_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = Document()

    # -------------------------------------------------------------
    # SECTION 1: Cover Page & Inner Title Page (No Headers/Footers)
    # -------------------------------------------------------------
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(1.5)
    sec1.right_margin = Inches(1.0)
    sec1.header.is_linked_to_previous = False
    sec1.footer.is_linked_to_previous = False

    # COVER PAGE
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(24)
    r = p.add_run("EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(36)
    r = p.add_run("CSIW ZG628T DISSERTATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.color.rgb = COLOR_DARK_SLATE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Daipayan Ghosal")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(48)
    r = p.add_run("BITS ID No.: 2022wa86002")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Dissertation Work Carried Out At:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(72)
    r = p.add_run("Wipro Limited")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(48)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Pilani (Rajasthan) India")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("November, 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    # PAGE BREAK FOR INNER TITLE
    doc.add_page_break()

    # INNER TITLE PAGE
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("CSIW ZG628T DISSERTATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = COLOR_DARK_SLATE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Submitted in partial fulfilment of the requirements of\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True
    r2 = p.add_run("M.Tech in Computing Systems & Infrastructure Degree Program\n(BITS - WIPRO Collaborative Programme - WIMS)\nby")
    r2.bold = True
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Daipayan Ghosal")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("ID No. 2022wa86002\n(Email: 2022wa86002@wilp.bits-pilani.ac.in)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Under the supervision of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("Ms. Nidhi Kashyap\n")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r2 = p.add_run("Analyst, Cybersecurity Practice\nWipro Limited, Pune (Email: nidhi.kashyap@wipro.com)")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(10)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Additional Examiner")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("Mr. Satish Banigole\n")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r2 = p.add_run("Project Manager, Wipro Limited, Pune (Email: satish.banigole@wipro.com)")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(10)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("Dissertation work carried out at\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r.font.italic = True
    r2 = p.add_run("Wipro Limited, Pune / Bangalore")
    r2.bold = True
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE\nPILANI (RAJASTHAN)")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_PRIMARY_NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("November, 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)

    # -------------------------------------------------------------
    # SECTION 2: Preliminary Pages (Roman Numerals i, ii, iii...)
    # -------------------------------------------------------------
    sec2 = doc.add_section()
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(1.0)
    sec2.left_margin = Inches(1.5)
    sec2.right_margin = Inches(1.0)
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False

    pgNumType2 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="1"/>')
    sec2._sectPr.append(pgNumType2)

    footer2 = sec2.footer
    f_p2 = footer2.paragraphs[0]
    f_p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number_field(f_p2.add_run())

    # Split markdown by sections
    pos_cert = md_text.find("## CERTIFICATE FROM THE SUPERVISOR")
    pos_chap1 = md_text.find("# CHAPTER 1: INTRODUCTION")

    prelim_text = md_text[pos_cert:pos_chap1]
    main_text = md_text[pos_chap1:]

    def process_markdown_content(target_doc, text_chunk):
        lines = text_chunk.splitlines()
        i = 0
        in_tbl = False
        tbl_buf = []
        in_code = False
        code_buf = []

        page_breaks = [
            "## ACKNOWLEDGEMENTS",
            "## ABSTRACT",
            "## TABLE OF CONTENTS",
            "## LIST OF FIGURES",
            "## LIST OF TABLES",
            "## LIST OF ABBREVIATIONS & SYMBOLS",
            "# CHAPTER 2: LITERATURE REVIEW AND RELATED WORK",
            "# CHAPTER 3: SYSTEM ARCHITECTURE AND MATHEMATICAL FORMULATION",
            "# CHAPTER 4: IMPLEMENTATION AND SYSTEM ENGINEERING",
            "# CHAPTER 5: EMPIRICAL RESULTS AND EVALUATION",
            "# CHAPTER 6: DISCUSSION AND OPERATIONAL IMPACT",
            "# CHAPTER 7: CONCLUSIONS AND FUTURE WORK",
            "# REFERENCES",
            "# APPENDICES",
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
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    fig_cap = ""
                    if j < len(lines) and (lines[j].strip().startswith("**Figure") or lines[j].strip().startswith("*Figure")):
                        fig_cap = re.sub(r'[\*]+', '', lines[j].strip())
                        i = j
                    add_code_block(target_doc, code_buf, caption=fig_cap)
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

            # Display Equations ($$ ... $$)
            if stripped.startswith("$$"):
                math_lines = []
                if stripped.endswith("$$") and len(stripped) > 2:
                    math_lines.append(stripped)
                    i += 1
                else:
                    math_lines.append(stripped)
                    i += 1
                    while i < len(lines) and not lines[i].strip().endswith("$$"):
                        math_lines.append(lines[i].strip())
                        i += 1
                    if i < len(lines):
                        math_lines.append(lines[i].strip())
                        i += 1
                format_display_equation(target_doc, math_lines)
                continue

            # Empty lines
            if not stripped:
                i += 1
                continue

            # Figures ![alt](figures/...)
            m_img = re.match(r'^!\[(.*?)\]\((.*?)\)', stripped)
            if m_img:
                raw_caption = m_img.group(1)
                img_path = m_img.group(2)
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                full_caption = raw_caption
                if j < len(lines) and (lines[j].strip().startswith("*Figure ") or lines[j].strip().startswith("**Figure ")):
                    full_caption = re.sub(r'[\*]+', '', lines[j].strip())
                    i = j
                add_embedded_figure(target_doc, img_path, full_caption)
                i += 1
                continue

            # Section page breaks
            if i > 5:
                for pb in page_breaks:
                    if stripped == pb or stripped.startswith(pb + " "):
                        target_doc.add_page_break()
                        break

            # Headings
            if stripped.startswith("# CHAPTER") or stripped.startswith("# REFERENCES") or stripped.startswith("# APPENDICES"):
                p = target_doc.add_paragraph(style='Heading 1')
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(8)
                p.paragraph_format.keep_with_next = True
                title_text = re.sub(r'^#\s+', '', stripped)
                r = p.add_run(clean_math_text(title_text))
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
                r = p.add_run(clean_math_text(title_text))
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
                r = p.add_run(clean_math_text(title_text))
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
                r = p.add_run(clean_math_text(title_text))
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

    print("Processing preliminary pages (Section 2)...")
    process_markdown_content(doc, prelim_text)

    # -------------------------------------------------------------
    # SECTION 3: Main Body (Arabic Numerals 1, 2, 3...)
    # -------------------------------------------------------------
    sec3 = doc.add_section()
    sec3.top_margin = Inches(1.0)
    sec3.bottom_margin = Inches(1.0)
    sec3.left_margin = Inches(1.5)
    sec3.right_margin = Inches(1.0)
    sec3.header.is_linked_to_previous = False
    sec3.footer.is_linked_to_previous = False

    pgNumType3 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>')
    sec3._sectPr.append(pgNumType3)

    # Add Running Header (Right aligned, Muted Gray, 9pt)
    header3 = sec3.header
    h_p = header3.paragraphs[0]
    h_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr = h_p.add_run("CSIW ZG628T Dissertation | BITS Pilani (WILP)")
    r_hdr.font.name = "Times New Roman"
    r_hdr.font.size = Pt(8.5)
    r_hdr.font.italic = True
    r_hdr.font.color.rgb = COLOR_MUTED_GRAY

    # Add Running Footer (Center aligned Page Number)
    footer3 = sec3.footer
    f_p3 = footer3.paragraphs[0]
    f_p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number_field(f_p3.add_run())

    print("Processing main body chapters, references, appendices, and checklist (Section 3)...")
    process_markdown_content(doc, main_text)

    # Save to both parent folder and project docs
    try:
        print(f"Saving primary dissertation to: {_OUTPUT_DOCX_PARENT}")
        doc.save(str(_OUTPUT_DOCX_PARENT))
        print(f"Primary dissertation successfully generated ({os.path.getsize(_OUTPUT_DOCX_PARENT):,} bytes)")
    except PermissionError:
        alt_path = _PARENT_DIR / "Daipayan_Ghosal_2022wa86002_Final_Dissertation_Updated.docx"
        print(f"Notice: Primary file is currently open in Word. Saving to alternate path: {alt_path}")
        doc.save(str(alt_path))
        print(f"Alternate dissertation successfully generated ({os.path.getsize(alt_path):,} bytes)")

    try:
        _OUTPUT_DOCX_PROJECT.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(_OUTPUT_DOCX_PROJECT))
        print(f"Project copy saved to: {_OUTPUT_DOCX_PROJECT}")
    except Exception as e:
        print(f"Note: Could not save to project docs copy: {e}")

if __name__ == "__main__":
    build_dissertation_docx()
