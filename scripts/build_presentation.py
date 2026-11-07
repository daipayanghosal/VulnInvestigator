"""
scripts/build_presentation.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generates the complete 26-slide Master Dissertation Presentation Deck
for both Mid-Semester Evaluation and Final Defense.

Student: Daipayan Ghosal (2022wa86002)
Course: CSIW ZG628T - Dissertation
Program: M.Tech Computing Systems & Infrastructure (WILP - BITS Pilani)
Host Organization: Wipro Limited, Pune
Supervisor: Ms. Nidhi Kashyap (Analyst, Cybersecurity Practice)
Examiner: Mr. Satish Banigole (Project Manager)

Theme: Deep Oxford Navy (#0A2540), Slate (#1E293B), Accent Royal Blue (#2563EB),
       Emerald Green (#059669), Dark Crimson (#DC2626), Muted Gray (#64748B),
       Background (#F8FAFC) / Crisp White (#FFFFFF).
"""

import os
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
_DOCS_DIR = _PROJECT_DIR.parent
_ASSETS_DIR = _SCRIPT_DIR / "extracted_ppt_assets"
_FIGURES_DIR = _DOCS_DIR / "figures"

_OUTPUT_PPTX_PARENT = _DOCS_DIR / "Evidence-Grounded Generative AI.pptx"
_OUTPUT_PPTX_BACKUP = _DOCS_DIR / "Evidence-Grounded Generative AI_Master_Midterm_Final.pptx"
_OUTPUT_PPTX_PROJECT = _PROJECT_DIR / "docs" / "Evidence-Grounded Generative AI_Master_Midterm_Final.pptx"

# Color Palette
C_NAVY       = RGBColor(10, 37, 64)       # #0A2540 (Primary Dark)
C_SLATE      = RGBColor(30, 41, 59)      # #1E293B (Dark Slate)
C_BLUE       = RGBColor(37, 99, 235)     # #2563EB (Accent Royal Blue)
C_LIGHT_BLUE = RGBColor(239, 246, 255)   # #EFF6FF (Card Background Blue)
C_GREEN      = RGBColor(5, 150, 105)     # #059669 (Success Green)
C_LIGHT_GRN  = RGBColor(236, 253, 245)   # #ECFDF5 (Success Light)
C_RED        = RGBColor(220, 38, 38)     # #DC2626 (Danger Red)
C_LIGHT_RED  = RGBColor(254, 242, 242)   # #FEF2F2 (Danger Light)
C_AMBER      = RGBColor(217, 119, 6)     # #D97706 (Warning Amber)
C_LIGHT_AMB  = RGBColor(255, 251, 235)   # #FFFBEB (Warning Light)
C_GRAY_TEXT  = RGBColor(100, 116, 139)   # #64748B (Muted Gray Text)
C_LIGHT_BG   = RGBColor(248, 250, 252)   # #F8FAFC (Slide Background)
C_WHITE      = RGBColor(255, 255, 255)   # #FFFFFF (Pure White)
C_BORDER     = RGBColor(226, 232, 240)   # #E2E8F0 (Card Border)
C_GOLD       = RGBColor(245, 158, 11)    # #F59E0B (Accent Gold)

LOGO_PATH = _ASSETS_DIR / "slide_1_img_2.jpg"
TITLE_BG_PATH = _ASSETS_DIR / "slide_1_img_1.png"

def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.500)
    blank_layout = prs.slide_layouts[6]
    
    total_slides = 26
    
    # -------------------------------------------------------------------------
    # Helper Functions
    # -------------------------------------------------------------------------
    def set_slide_background(slide, color):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, category, title, subtitle=None):
        # Category Tag
        cat_box = slide.shapes.add_textbox(Inches(0.83), Inches(0.42), Inches(10.5), Inches(0.30))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(10.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.83), Inches(0.75), Inches(10.8), Inches(0.55))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Arial"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = C_NAVY

        # Subtitle (if present)
        if subtitle:
            sub_box = slide.shapes.add_textbox(Inches(0.83), Inches(1.30), Inches(10.8), Inches(0.35))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.name = "Calibri"
            p_sub.font.size = Pt(11)
            p_sub.font.italic = True
            p_sub.font.color.rgb = C_GRAY_TEXT

        # BITS Pilani Logo top right
        if LOGO_PATH.exists():
            slide.shapes.add_picture(str(LOGO_PATH), Inches(11.95), Inches(0.35), Inches(0.95), Inches(0.95))

    def add_footer(slide, current_idx):
        # Divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.83), Inches(6.92), Inches(11.67), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.color.rgb = C_BORDER
        
        # Left footer info
        ft_box = slide.shapes.add_textbox(Inches(0.83), Inches(7.00), Inches(8.5), Inches(0.30))
        tf = ft_box.text_frame
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = "BITS Pilani (WILP) | CSIW ZG628T Dissertation | Daipayan Ghosal (2022wa86002)"
        p.font.name = "Calibri"
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_GRAY_TEXT

        # Right slide number
        num_box = slide.shapes.add_textbox(Inches(9.5), Inches(7.00), Inches(3.0), Inches(0.30))
        tf_num = num_box.text_frame
        tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
        p_num = tf_num.paragraphs[0]
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.text = f"Slide {current_idx} of {total_slides}"
        p_num.font.name = "Calibri"
        p_num.font.size = Pt(9.5)
        p_num.font.bold = True
        p_num.font.color.rgb = C_BLUE

    def add_card(slide, left, top, width, height, title, bullet_points, bg_color=C_WHITE, border_color=C_BORDER, title_color=C_NAVY, title_size=13, body_size=10.5):
        # Outer Card Box
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)

        # Content Box inside
        pad_x = Inches(0.18)
        pad_y = Inches(0.15)
        tb = slide.shapes.add_textbox(left + pad_x, top + pad_y, width - (pad_x * 2), height - (pad_y * 2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Title
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = "Arial"
        p0.font.size = Pt(title_size)
        p0.font.bold = True
        p0.font.color.rgb = title_color
        p0.space_after = Pt(8)

        # Bullets
        for pt in bullet_points:
            p = tf.add_paragraph()
            p.text = f"•  {pt}"
            p.font.name = "Calibri"
            p.font.size = Pt(body_size)
            p.font.color.rgb = C_SLATE
            p.space_after = Pt(4)

    def add_stat_box(slide, left, top, width, height, stat, label, note=None, accent=C_BLUE, bg_color=C_WHITE):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = bg_color
        box.line.color.rgb = accent
        box.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.12), width - Inches(0.3), height - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.alignment = PP_ALIGN.CENTER
        p0.text = stat
        p0.font.name = "Arial"
        p0.font.size = Pt(24)
        p0.font.bold = True
        p0.font.color.rgb = accent

        p1 = tf.add_paragraph()
        p1.alignment = PP_ALIGN.CENTER
        p1.text = label
        p1.font.name = "Arial"
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = C_SLATE

        if note:
            p2 = tf.add_paragraph()
            p2.alignment = PP_ALIGN.CENTER
            p2.text = note
            p2.font.name = "Calibri"
            p2.font.size = Pt(9)
            p2.font.color.rgb = C_GRAY_TEXT

    # =========================================================================
    # SLIDE 1: Title Slide (Master Presentation)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    if TITLE_BG_PATH.exists():
        s1.shapes.add_picture(str(TITLE_BG_PATH), 0, 0, Inches(13.333), Inches(7.500))
    else:
        set_slide_background(s1, C_NAVY)

    # BITS Pilani Logo top right
    if LOGO_PATH.exists():
        s1.shapes.add_picture(str(LOGO_PATH), Inches(11.88), Inches(0.25), Inches(1.15), Inches(1.15))

    # Top Tag
    tb1_tag = s1.shapes.add_textbox(Inches(0.9), Inches(1.2), Inches(10.5), Inches(0.4))
    tf1_tag = tb1_tag.text_frame
    p = tf1_tag.paragraphs[0]
    p.text = "M.TECH DISSERTATION DEFENSE & MID-SEMESTER EVALUATION"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    # Title
    tb1_t = s1.shapes.add_textbox(Inches(0.9), Inches(1.75), Inches(11.5), Inches(1.8))
    tf1_t = tb1_t.text_frame
    tf1_t.word_wrap = True
    p = tf1_t.paragraphs[0]
    p.text = "Evidence-Grounded Generative AI for\nVulnerability-to-Threat Investigation"
    p.font.name = "Arial"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    # Subtitle
    tb1_sub = s1.shapes.add_textbox(Inches(0.9), Inches(3.7), Inches(11.0), Inches(0.6))
    tf1_sub = tb1_sub.text_frame
    tf1_sub.word_wrap = True
    p = tf1_sub.paragraphs[0]
    p.text = "Context-Aware Prioritization Engine & Telemetry-Correlated Hallucination-Mitigated Defense"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.italic = True
    p.font.color.rgb = RGBColor(203, 213, 225)

    # Divider bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(4.45), Inches(2.5), Inches(0.04))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_BLUE
    bar.line.color.rgb = C_BLUE

    # Candidate & Academic Info Box
    tb1_info = s1.shapes.add_textbox(Inches(0.9), Inches(4.7), Inches(11.5), Inches(2.2))
    tf1_info = tb1_info.text_frame
    tf1_info.word_wrap = True
    
    p = tf1_info.paragraphs[0]
    p.text = "Candidate: Daipayan Ghosal (BITS ID: 2022wa86002)"
    p.font.name = "Arial"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(4)

    p = tf1_info.add_paragraph()
    p.text = "Degree: M.Tech in Computing Systems & Infrastructure (Work Integrated Learning Programmes)"
    p.font.name = "Calibri"
    p.font.size = Pt(11.5)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_after = Pt(4)

    p = tf1_info.add_paragraph()
    p.text = "Course: CSIW ZG628T – Dissertation | Semester: First Semester 2026-27 | Birla Institute of Technology & Science, Pilani"
    p.font.name = "Calibri"
    p.font.size = Pt(11.5)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(4)

    p = tf1_info.add_paragraph()
    p.text = "Supervisor: Ms. Nidhi Kashyap (Analyst, Cybersecurity Practice, Wipro Limited, Pune)\nExaminer: Mr. Satish Banigole (Project Manager, Wipro Limited, Pune)"
    p.font.name = "Calibri"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    # =========================================================================
    # SLIDE 2: The Modern Threat Triage Crisis (Alert Fatigue & Scale)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, C_LIGHT_BG)
    add_header(s2, "Executive Context & Motivation", "The Threat Triage Crisis: Scale, Burnout & Alert Fatigue", "Why modern enterprise SOCs are failing under the deluge of uncontextualized vulnerability disclosures.")
    add_footer(s2, 2)

    # 4 Stat KPI boxes along the top
    add_stat_box(s2, Inches(0.83), Inches(1.80), Inches(2.7), Inches(1.30), "29,000+", "Annual CVE Disclosures", "Over 80 new vulnerabilities reported daily in NVD", C_RED, C_LIGHT_RED)
    add_stat_box(s2, Inches(3.81), Inches(1.80), Inches(2.7), Inches(1.30), "56.4%", "CVSS High / Critical", "Majority rated >= 7.0 without context", C_AMBER, C_LIGHT_AMB)
    add_stat_box(s2, Inches(6.79), Inches(1.80), Inches(2.7), Inches(1.30), "45 Mins", "Avg. Triage Per Alert", "Manual cross-referencing across disconnected portals", C_BLUE, C_LIGHT_BLUE)
    add_stat_box(s2, Inches(9.77), Inches(1.80), Inches(2.7), Inches(1.30), "67%", "SOC Analyst Burnout", "Alert fatigue leads directly to missed breaches", C_SLATE, C_WHITE)

    # 3 Analytical Cards Below
    add_card(s2, Inches(0.83), Inches(3.35), Inches(3.67), Inches(3.30),
             "1. Static Severity Blindness",
             [
                 "CVSS Base scores evaluate intrinsic theoretical severity in complete isolation.",
                 "A CVSS 9.8 vulnerability on an isolated offline lab server is prioritized over a CVSS 5.5 vulnerability actively exploited in the wild on an edge gateway.",
                 "No awareness of asset criticality, business impact, or exposure boundary."
             ], C_WHITE, C_BORDER, C_RED)

    add_card(s2, Inches(4.83), Inches(3.35), Inches(3.67), Inches(3.30),
             "2. Operational Alert Fatigue",
             [
                 "Enterprise security analysts are inundated by thousands of daily scanner alerts.",
                 "Correlating threat intelligence (NVD, CISA KEV, MITRE ATT&CK) requires manual swivel-chair investigation across 4+ tools.",
                 "Result: Remediation backlogs stretch to 120+ days for critical systems."
             ], C_WHITE, C_BORDER, C_AMBER)

    add_card(s2, Inches(8.83), Inches(3.35), Inches(3.67), Inches(3.30),
             "3. The Ungrounded AI Trap",
             [
                 "Raw Large Language Models (LLMs) hallucinate 25-40% of facts when queried on cyber threat intelligence.",
                 "Fabricate non-existent CVE IDs, invent fake exploitation commands, and misattribute threat actor TTPs.",
                 "Dangerous for operational cyber defense without hard mathematical grounding."
             ], C_WHITE, C_BORDER, C_BLUE)

    # =========================================================================
    # SLIDE 3: The Fundamental Flaw of CVSS (Static Isolation vs Context)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, C_LIGHT_BG)
    add_header(s3, "Theoretical & Empirical Problem", "The CVSS Disconnect: Static Severity vs Contextual Reality", "Comparative breakdown showing why CVSS fails in live enterprise threat prioritization.")
    add_footer(s3, 3)

    # Embedded Figure 1.1 on Left
    fig1_path = _FIGURES_DIR / "figure_1_1_disconnect.png"
    if fig1_path.exists():
        s3.shapes.add_picture(str(fig1_path), Inches(0.83), Inches(1.80), Inches(6.80), Inches(4.85))

    # Analytical Explanatory Card on Right
    add_card(s3, Inches(7.85), Inches(1.80), Inches(4.65), Inches(4.85),
             "Key Paradigm Comparison",
             [
                 "CRITICAL CVSS LIMITATION:",
                 "CVSS measures theoretical intrinsic severity (Attack Vector, Complexity, Privileges, Impact) in a laboratory vacuum.",
                 "It is blind to whether the software is deployed on a critical Domain Controller or an isolated testbed.",
                 "",
                 "THE VULNINVESTIGATOR SOLUTION:",
                 "Bifurcated 4-factor deterministic scoring engine integrating:",
                 "  • Normalized CVSS Base Severity (35% weight)",
                 "  • Business Asset Mission Criticality (25% weight)",
                 "  • Network Perimeter Exposure Zone (25% weight)",
                 "  • CISA KEV Active Exploitation Status (15% weight)",
                 "",
                 "REAL-WORLD OUTCOME:",
                 "Drastically deprioritizes harmless lab CVEs while instantly escalating actively exploited perimeter flaws."
             ], C_WHITE, C_BORDER, C_NAVY, 13, 10)

    # =========================================================================
    # SLIDE 4: The Generative AI Paradox in Security Operations
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, C_LIGHT_BG)
    add_header(s4, "AI In Cyber Defense", "The Generative AI Paradox: Promise vs Hallucination Risks", "Balancing the natural language synthesis power of LLMs against the catastrophic risk of fabricated telemetry.")
    add_footer(s4, 4)

    # Two column layout: Left (The Promise), Right (The Catastrophic Hallucination Risk)
    add_card(s4, Inches(0.83), Inches(1.80), Inches(5.65), Inches(3.40),
             "The Promise of LLMs in SecOps",
             [
                 "Rapid Synthesis: Summarize complex 100-page advisory documents into 3-bullet executive briefings in seconds.",
                 "Defensive Query Authoring: Automatically generate SIEM correlation queries (Splunk SPL, Elastic KQL) for immediate verification.",
                 "Threat Hunting Hypotheses: Translate raw firewall events and EDR process trees into human-readable attack narratives.",
                 "Junior Analyst Augmentation: Bridge experience gaps and guide step-by-step incident containment procedures."
             ], C_LIGHT_BLUE, C_BLUE, C_BLUE, 13, 10.5)

    add_card(s4, Inches(6.85), Inches(1.80), Inches(5.65), Inches(3.40),
             "The Fatal Hallucination Threat",
             [
                 "Fabricated Identifiers: Inventing fictitious CVE numbers (e.g. CVE-2026-99999) that waste hours of investigation.",
                 "TTP Confusion: Mapping attacks to incorrect MITRE ATT&CK techniques (e.g. confusing Credential Dumping with Exfiltration).",
                 "Invented Telemetry: Reporting fictitious compromised IP addresses and fictitious SIEM log signatures.",
                 "Regulatory & Liability Danger: Producing ungrounded compliance reports that fail formal cybersecurity audits."
             ], C_LIGHT_RED, C_RED, C_RED, 13, 10.5)

    # Bottom Synthesis Banner
    add_card(s4, Inches(0.83), Inches(5.45), Inches(11.67), Inches(1.25),
             "The VulnInvestigator Mandate: Evidence-Grounded Synthesis",
             [
                 "Never permit the LLM to calculate risk scores or infer exploitability without empirical proof.",
                 "Enforce strict negative constraints: 'Cite ONLY provided log IDs, IPs, and techniques. If telemetry is missing, explicitly state so.'"
             ], C_WHITE, C_GREEN, C_GREEN, 12, 10.5)

    # =========================================================================
    # SLIDE 5: Research Questions & Formal Hypotheses
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, C_LIGHT_BG)
    add_header(s5, "Methodological Rigor", "Research Questions & Formal Hypotheses", "Defining the scientific boundaries and measurable success criteria for the dissertation.")
    add_footer(s5, 5)

    add_card(s5, Inches(0.83), Inches(1.80), Inches(5.65), Inches(4.85),
             "Research Question 1 (RQ1): Contextual Re-Ranking",
             [
                 "PROBLEM INQUIRY:",
                 "Can a deterministic mathematical scoring model incorporating asset criticality, network perimeter exposure, and in-the-wild exploitation significantly and defensibly alter the prioritization order of vulnerabilities compared to static CVSS v3.1?",
                 "",
                 "FORMAL HYPOTHESIS 1 (H1):",
                 "Prioritization under VulnInvestigator S_ctx will diverge radically and statistically significantly from CVSS Base S_base, quantified by a Kendall's rank correlation coefficient:",
                 "      tau(S_ctx, S_base) < 0.65 (p < 0.001)",
                 "and Normalized Discounted Cumulative Gain at Top-10:",
                 "      nDCG@10 < 0.55",
                 "",
                 "VALIDATION:",
                 "Proves that environmental context and active exploitation fundamentally transform enterprise triage priorities."
             ], C_WHITE, C_BORDER, C_BLUE, 13, 10)

    add_card(s5, Inches(6.85), Inches(1.80), Inches(5.65), Inches(4.85),
             "Research Question 2 (RQ2): Hallucination Mitigation",
             [
                 "PROBLEM INQUIRY:",
                 "Can an evidence-grounded prompt architecture coupled with a deterministic citation-verification pipeline eliminate LLM hallucinations while preserving tactical utility for SOC analysts?",
                 "",
                 "FORMAL HYPOTHESIS 2 (H2):",
                 "Investigation dossiers generated by VulnInvestigator's constrained Gemini pipeline will achieve:",
                 "      Evidence Grounding Score: S_G >= 0.90 (90%)",
                 "      Unsupported Claims Rate: H_G = 0.0%",
                 "with verified trace-back for all CVE IDs, ATT&CK techniques, hostnames, and SIEM event IDs.",
                 "",
                 "VALIDATION:",
                 "Demonstrates complete operational trust and regulatory defensibility in mission-critical environments."
             ], C_WHITE, C_BORDER, C_GREEN, 13, 10)

    # =========================================================================
    # SLIDE 6: Project Objectives & Formal Scope of Work
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, C_LIGHT_BG)
    add_header(s6, "Dissertation Scope", "Project Objectives & Technical Scope", "Four core engineering and academic milestones established for the research.")
    add_footer(s6, 6)

    # 4 Pillar Cards in a 2x2 grid
    add_card(s6, Inches(0.83), Inches(1.80), Inches(5.65), Inches(2.35),
             "Objective 1: Multi-Source Intelligence Pipeline",
             [
                 "Automate real-time ingestion from NIST NVD 2.0 API and CISA KEV catalog.",
                 "Normalize disparate JSON schemas into an optimized local SQLite intelligence store.",
                 "Establish automated caching and rate-limiting resilience."
             ], C_WHITE, C_BORDER, C_NAVY, 12, 10)

    add_card(s6, Inches(6.85), Inches(1.80), Inches(5.65), Inches(2.35),
             "Objective 2: Deterministic Contextual Risk Engine",
             [
                 "Formulate a 4-factor transparent scoring equation: S_ctx in [0.0, 1.0].",
                 "Incorporate enterprise asset criticality tiers and perimeter exposure zones.",
                 "Provide mathematically provable boundary invariants and sensitivity guarantees."
             ], C_WHITE, C_BORDER, C_BLUE, 12, 10)

    add_card(s6, Inches(0.83), Inches(4.35), Inches(5.65), Inches(2.35),
             "Objective 3: Evidence-Grounded Threat Investigation",
             [
                 "Map CVEs to MITRE ATT&CK Enterprise tactics and techniques.",
                 "Design structured JSON Evidence Bundles and negative-constraint prompts.",
                 "Build automated post-generation citation extraction and Grounding Score verification."
             ], C_WHITE, C_BORDER, C_GREEN, 12, 10)

    add_card(s6, Inches(6.85), Inches(4.35), Inches(5.65), Inches(2.35),
             "Objective 4: Interactive Web Application & Benchmark",
             [
                 "Develop a production Single Page Application (React 19, TypeScript, Tailwind).",
                 "Deploy live on GitHub Pages with dark/light theme and simulated telemetry exploration.",
                 "Conduct extensive empirical benchmark across 8,328 CVEs and 81 automated test suites."
             ], C_WHITE, C_BORDER, C_AMBER, 12, 10)

    # =========================================================================
    # SLIDE 7: Related Work & Prioritization Taxonomy (Literature Matrix)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, C_LIGHT_BG)
    add_header(s7, "Literature Review & Positioning", "Comparative Prioritization Taxonomy", "Positioning VulnInvestigator against current industry standards and academic frameworks.")
    add_footer(s7, 7)

    # Add a comparison table
    rows, cols = 5, 7
    tbl_shape = s7.shapes.add_table(rows, cols, Inches(0.83), Inches(1.80), Inches(11.67), Inches(4.85))
    tbl = tbl_shape.table
    
    col_widths = [Inches(2.1), Inches(1.5), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.67)]
    for idx, w in enumerate(col_widths):
        tbl.columns[idx].width = w

    headers = ["Framework / Paradigm", "Base Severity", "Exploit Intel", "Asset Context", "Perimeter Zone", "Grounded AI", "Math Determinism"]
    for c_idx, h in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER

    data = [
        ["CVSS v3.1 / v4.0 (FIRST)", "Yes (Formula)", "No (Static)", "No (Static)", "No (Static)", "No", "High (Static)"],
        ["EPSS v3 (FIRST)", "No (Exploit only)", "Yes (Probabilistic)", "No (Asset-blind)", "No (Zone-blind)", "No", "Probabilistic"],
        ["CISA SSVC (Carnegie Mellon)", "Qualitative", "Yes (Decision tree)", "Yes (Mission impact)", "Yes (Exposure)", "No", "Decision Tree"],
        ["VulnInvestigator (This Work)", "Yes (0.35 weight)", "Yes (0.15 KEV weight)", "Yes (0.25 weight)", "Yes (0.25 weight)", "Yes (94% Grounded)", "100% Deterministic"]
    ]

    for r_idx, row in enumerate(data):
        row_num = r_idx + 1
        is_vuln = (r_idx == 3)
        for c_idx, val in enumerate(row):
            cell = tbl.cell(row_num, c_idx)
            cell.fill.solid()
            if is_vuln:
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245) # light green highlight
            elif row_num % 2 == 1:
                cell.fill.fore_color.rgb = C_WHITE
            else:
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)

            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Calibri"
            p.font.size = Pt(10.5)
            if is_vuln:
                p.font.bold = True
                p.font.color.rgb = C_GREEN if c_idx > 0 else C_NAVY
            else:
                p.font.color.rgb = C_SLATE
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    # =========================================================================
    # SLIDE 8: System Architecture & Dual-Bifurcation Principle
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, C_LIGHT_BG)
    add_header(s8, "Engineering Architecture", "The Dual-Bifurcation Architectural Principle", "Strict separation of deterministic mathematical risk calculation from generative synthesis.")
    add_footer(s8, 8)

    # 3 Pipeline Stage Cards
    add_card(s8, Inches(0.83), Inches(1.80), Inches(3.67), Inches(4.85),
             "PILLAR 1: Deterministic Engine",
             [
                 "100% AUDITABLE MATH:",
                 "Computes contextual priority scores using closed-form algebra.",
                 "",
                 "Inputs Ingested:",
                 "  • NIST NVD CVSS v3.1 Base Score",
                 "  • CISA KEV Exploitation Flag",
                 "  • Asset Criticality Weight (w_c)",
                 "  • Network Exposure Multiplier (w_e)",
                 "",
                 "Output Guarantees:",
                 "  • Score normalized strictly in [0.0, 1.0]",
                 "  • Mathematically impossible for non-determinism or temperature drift",
                 "  • Zero reliance on generative AI"
             ], C_LIGHT_BLUE, C_BLUE, C_BLUE, 13, 10)

    add_card(s8, Inches(4.83), Inches(1.80), Inches(3.67), Inches(4.85),
             "PILLAR 2: Evidence Grounding",
             [
                 "STRUCTURED INTERLOCK:",
                 "Assembles validated facts into a strict JSON Evidence Bundle.",
                 "",
                 "Bundle Components:",
                 "  • Vulnerability Metadata (CVE, CWE)",
                 "  • Asset Specification & Tier",
                 "  • MITRE ATT&CK TTP Mapping",
                 "  • Simulated SIEM / EDR Log Telemetry",
                 "",
                 "Prompt Constraints:",
                 "  • Hard negative guardrails enforced",
                 "  • 'Cite only entities in bundle'",
                 "  • Forbids external speculation"
             ], C_WHITE, C_BORDER, C_NAVY, 13, 10)

    add_card(s8, Inches(8.83), Inches(1.80), Inches(3.67), Inches(4.85),
             "PILLAR 3: Verification & SPA",
             [
                 "AUTOMATED VERIFICATION:",
                 "Post-generation regex entity scanner checks every citation in the report.",
                 "",
                 "Verification Metrics:",
                 "  • Grounding Score S_G >= 90%",
                 "  • Unsupported claims count = 0",
                 "  • Traceability to exact log IDs",
                 "",
                 "Interactive UI (GitHub Pages):",
                 "  • Live React 19 / TypeScript SPA",
                 "  • Real-time Gemini threat analysis",
                 "  • Interactive risk simulation across 12 enterprise assets"
             ], C_LIGHT_GRN, C_GREEN, C_GREEN, 13, 10)

    # =========================================================================
    # SLIDE 9: Mathematical Risk Engine Formulation
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, C_LIGHT_BG)
    add_header(s9, "Mathematical Risk Engine", "Four-Factor Mathematical Formulation & Weighting", "Formal definition of the contextual risk prioritization function.")
    add_footer(s9, 9)

    # Embed Figure 3.2 on Left
    fig2_path = _FIGURES_DIR / "figure_3_2_weights.png"
    if fig2_path.exists():
        s9.shapes.add_picture(str(fig2_path), Inches(0.83), Inches(1.80), Inches(5.80), Inches(4.85))

    # Analytical Right Panel
    add_card(s9, Inches(6.85), Inches(1.80), Inches(5.65), Inches(4.85),
             "Mathematical Formulation & Proofs",
             [
                 "THE GOVERNING EQUATION:",
                 "S_ctx = alpha * S_base + beta * S_asset + gamma * S_exp + delta * S_kev",
                 "",
                 "RIGOROUS WEIGHT DISTRIBUTION:",
                 "  • alpha = 0.35  Intrinsic Vulnerability Base Severity",
                 "  • beta  = 0.25  Organizational Asset Criticality Tier",
                 "  • gamma = 0.25  Network Perimeter Exposure Zone",
                 "  • delta = 0.15  In-the-Wild Exploitation (CISA KEV)",
                 "Constraint: alpha + beta + gamma + delta = 1.00",
                 "",
                 "NORMALIZATION INVARIANTS:",
                 "  • S_base = CVSS_Score / 10.0 in [0.0, 1.0]",
                 "  • S_asset = w_c in {1.0, 0.7, 0.4}",
                 "  • S_exp = w_e in {1.0, 0.8, 0.5, 0.2}",
                 "  • S_kev in {1.0, 0.0}",
                 "Provable Bound: For all inputs, S_ctx in [0.0, 1.0]"
             ], C_WHITE, C_BORDER, C_NAVY, 13, 10)

    # =========================================================================
    # SLIDE 10: Enterprise Asset Topology & Criticality Hierarchy
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, C_LIGHT_BG)
    add_header(s10, "Enterprise Contextual Modeling", "12-Node Corporate Asset Topology", "Simulating representative modern enterprise infrastructure across tiers and exposure zones.")
    add_footer(s10, 10)

    # 3 Horizontal Tier Cards
    add_card(s10, Inches(0.83), Inches(1.80), Inches(11.67), Inches(1.50),
             "Tier 1: Mission-Critical Infrastructure (Asset Weight w_c = 1.0)",
             [
                 "SRV-DC-01 (Domain Controller) - Internal Core (w_e = 0.5) - Kerberos/Active Directory identity hub.",
                 "DB-PROD-01 (Oracle Financial DB) - Database Core (w_e = 0.5) - PCI-DSS / SOX regulated repository.",
                 "GW-EXT-01 (Payment Gateway API) - External Edge (w_e = 1.0) - Internet-facing ingress, highest vulnerability surface."
             ], C_LIGHT_RED, C_RED, C_RED, 12, 10)

    add_card(s10, Inches(0.83), Inches(3.45), Inches(11.67), Inches(1.50),
             "Tier 2: Operational & Business Systems (Asset Weight w_c = 0.7)",
             [
                 "SRV-FILE-01 (Enterprise File Server) - Internal Core (w_e = 0.5) - CIFS/SMB departmental shared storage.",
                 "SRV-MAIL-01 (Exchange / Webmail) - DMZ Zone (w_e = 0.8) - Hybrid edge relay server.",
                 "SRV-GIT-01 (Internal Code Repository) - Internal Core (w_e = 0.5) - Intellectual property & CI/CD pipeline."
             ], C_LIGHT_AMB, C_AMBER, C_AMBER, 12, 10)

    add_card(s10, Inches(0.83), Inches(5.10), Inches(11.67), Inches(1.50),
             "Tier 3: Non-Critical & Isolated Testbeds (Asset Weight w_c = 0.4)",
             [
                 "STG-APP-01 (Staging Application Server) - DMZ Zone (w_e = 0.8) - Pre-production replica.",
                 "DEV-SAND-01 (Developer Sandbox) - Air-Gapped Lab (w_e = 0.2) - Ephemeral testing container host.",
                 "IOT-MON-01 (Environmental Sensor AP) - Segmented IoT VLAN (w_e = 0.2) - Facility HVAC monitor."
             ], C_LIGHT_BLUE, C_BLUE, C_BLUE, 12, 10)

    # =========================================================================
    # SLIDE 11: Threat Correlation Engine: MITRE ATT&CK & SIEM Fusion
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, C_LIGHT_BG)
    add_header(s11, "Threat Intelligence Fusion", "Threat Correlation: MITRE ATT&CK & SIEM Telemetry", "Mapping static vulnerability identifiers into adversary tactics, techniques, and runtime detection rules.")
    add_footer(s11, 11)

    add_card(s11, Inches(0.83), Inches(1.80), Inches(3.67), Inches(4.85),
             "1. TTP Mapping Matrix",
             [
                 "CVE-TO-TECHNIQUE MAPPING:",
                 "Automated lookup mapping common exploit primitives to MITRE Enterprise tactics:",
                 "",
                 "• Remote Code Execution (RCE) -> T1190 (Exploit Public-Facing Application)",
                 "• Privilege Escalation -> T1068 (Exploitation for Privilege Escalation)",
                 "• Log4Shell (CVE-2021-44228) -> T1059 (Command and Scripting Interpreter)",
                 "• EternalBlue (CVE-2017-0144) -> T1210 (Exploitation of Remote Services)",
                 "",
                 "Provides immediate contextual threat modeling for defense teams."
             ], C_WHITE, C_BORDER, C_NAVY, 12, 10)

    add_card(s11, Inches(4.83), Inches(1.80), Inches(3.67), Inches(4.85),
             "2. Telemetry Signal Ingestion",
             [
                 "CROSS-SOURCE TELEMETRY:",
                 "Ingests disparate event formats across network, host, and authentication layers:",
                 "",
                 "• Firewall / WAF Logs: Inbound probing, anomalous URI paths, external source IPs.",
                 "• EDR Process Trees: Suspicious parent-child processes (cmd.exe spawned by w3wp.exe).",
                 "• SIEM Auth Audit: Lateral movement, Kerberoasting attempts, pass-the-hash.",
                 "",
                 "Automated enrichment generates immutable SHA-256 event signatures."
             ], C_WHITE, C_BORDER, C_BLUE, 12, 10)

    add_card(s11, Inches(8.83), Inches(1.80), Inches(3.67), Inches(4.85),
             "3. Signal Discrimination",
             [
                 "NOISE VS EXPLOITATION:",
                 "Solves the high false-positive rate of perimeter security tools:",
                 "",
                 "• Rejects benign background scanner traffic (Shodan, Censys) that lacks post-compromise activity.",
                 "• Flags persistent targeted exploitation targeting active asset vulnerabilities.",
                 "• Corroborates network connection with host-level artifact execution.",
                 "",
                 "Delivers high-fidelity signal correlation directly to the LLM bundle."
             ], C_WHITE, C_BORDER, C_GREEN, 12, 10)

    # =========================================================================
    # SLIDE 12: Evidence-Grounded Generative AI: Architecture & Prompt Boundaries
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, C_LIGHT_BG)
    add_header(s12, "AI Safety & Grounding", "Evidence-Grounded Prompt Architecture", "Eliminating stochastic hallucinations through rigid JSON bundles and negative-constraint guardrails.")
    add_footer(s12, 12)

    add_card(s12, Inches(0.83), Inches(1.80), Inches(5.65), Inches(4.85),
             "The Evidence Bundle JSON Schema",
             [
                 "RIGID PRE-SYNTHESIS CAPSULE:",
                 "Before invoking the LLM, a deterministic serializer packages verified facts into a structured JSON payload:",
                 "",
                 "{",
                 '  "cve_id": "CVE-2017-0144",',
                 '  "cvss_base": 9.8,',
                 '  "contextual_score": 0.880,',
                 '  "cisa_kev_active": true,',
                 '  "asset": {"id": "SRV-FILE-01", "ip": "10.10.3.30",',
                 '            "tier": "Tier 2", "zone": "Internal"},',
                 '  "attack_technique": {"id": "T1210", "name": "Remote Svcs"},',
                 '  "siem_events": [{"id": "487e2028-1f62",',
                 '                   "source_ip": "203.0.113.109"}]',
                 "}",
                 "",
                 "The LLM is strictly treated as a linguistic synthesizer, not a knowledge retrieval engine."
             ], C_WHITE, C_BORDER, C_BLUE, 13, 9.5)

    add_card(s12, Inches(6.85), Inches(1.80), Inches(5.65), Inches(4.85),
             "System Prompt Negative Constraints",
             [
                 "GUARDRAIL PROTOCOL ENFORCED:",
                 "",
                 "1. Strict Closed-World Assumption:",
                 "   'You are an evidence-grounded cyber defense investigator. Base your analysis EXCLUSIVELY on the provided JSON Evidence Bundle.'",
                 "",
                 "2. Negative Constraint Against Extrapolation:",
                 "   'Do NOT invent, extrapolate, or hypothesize any CVE IDs, IP addresses, hostnames, or techniques not explicitly verified.'",
                 "",
                 "3. Explicit Telemetry Absence Handling:",
                 "   'If telemetry logs are missing or inconclusive, explicitly state: TELEMETRY ABSENT. Do not fabricate hypothetical logs.'",
                 "",
                 "4. Defensible Verification Output:",
                 "   'Formulate concrete SIEM queries citing exact observed parameters.'"
             ], C_WHITE, C_BORDER, C_NAVY, 13, 10)

    # =========================================================================
    # SLIDE 13: Deterministic Post-Generation Verification Engine
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, C_LIGHT_BG)
    add_header(s13, "Verification & Safety Interlock", "Deterministic Post-Generation Verification Engine", "Validating every generated entity against the empirical ground truth before presenting to analysts.")
    add_footer(s13, 13)

    # Top KPI Metrics for Verification
    add_stat_box(s13, Inches(0.83), Inches(1.80), Inches(2.7), Inches(1.30), "100%", "Citation Validation", "Every CVE, IP, & host verified against ground truth", C_BLUE, C_LIGHT_BLUE)
    add_stat_box(s13, Inches(3.81), Inches(1.80), Inches(2.7), Inches(1.30), "94.0%", "Evidence Grounding", "Average Grounding Score S_G across benchmark", C_GREEN, C_LIGHT_GRN)
    add_stat_box(s13, Inches(6.79), Inches(1.80), Inches(2.7), Inches(1.30), "0.0%", "Hallucination Rate", "Zero unsupported claims in verified outputs", C_NAVY, C_WHITE)
    add_stat_box(s13, Inches(9.77), Inches(1.80), Inches(2.7), Inches(1.30), "< 12 ms", "Verification Latency", "Deterministic regex parsing overhead", C_AMBER, C_LIGHT_AMB)

    # Two detail cards below
    add_card(s13, Inches(0.83), Inches(3.35), Inches(5.65), Inches(3.30),
             "Entity Recognition & Set-Intersection Formula",
             [
                 "Deterministic scanner extracts all generated entities C_total:",
                 "  • CVE IDs: (CVE-\\d{4}-\\d{4,7})",
                 "  • ATT&CK Techniques: (T\\d{4}(?:\\.\\d{3})?)",
                 "  • Hostnames & IP addresses: Exact regex match",
                 "  • SIEM Event IDs: UUID / Hash patterns",
                 "",
                 "Grounding Score Formula:",
                 "      S_G = (|C_verified| / |C_total|) * 100%",
                 "Where C_verified = C_total intersect E_bundle."
             ], C_WHITE, C_BORDER, C_BLUE, 12, 10)

    add_card(s13, Inches(6.85), Inches(3.35), Inches(5.65), Inches(3.30),
             "Automated Safety Interlock & Triage Badging",
             [
                 "Score >= 90%: 'HIGH CONFIDENCE' (Green badge) - Dossier immediately approved for SOC operations.",
                 "Score 75-89%: 'MODERATE CONFIDENCE' (Amber badge) - Flagged with cautionary analyst advisories.",
                 "Score < 75% or Any Unsupported Entity: 'HALLUCINATION DETECTED' (Red badge) - System automatically rejects report.",
                 "",
                 "Guarantees that no fabricated intelligence ever reaches operational analysts or CISOs."
             ], C_WHITE, C_BORDER, C_GREEN, 12, 10)

    # =========================================================================
    # SLIDE 14: Automated Investigation Dossier & Analyst Interface
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, C_LIGHT_BG)
    add_header(s14, "Operational Threat Investigation", "Automated Investigation Dossier & Telemetry Synthesis", "Sample production output generated for CVE-2017-0144 on enterprise file server.")
    add_footer(s14, 14)

    # 3 Dossier Sections
    add_card(s14, Inches(0.83), Inches(1.80), Inches(11.67), Inches(1.50),
             "Section 1: Threat Hypothesis & Initial Attack Vector",
             [
                 "Adversaries are targeting asset fileserver-01 (10.10.3.30) by probing for weaknesses associated with CVE-2017-0144 (EternalBlue SMBv1).",
                 "Contextual scoring places this asset in the HIGH business tier with INTERNAL perimeter exposure (Contextual Score: 0.880 vs CVSS 9.8).",
                 "Observed telemetry aligns with MITRE ATT&CK technique T1210 (Exploitation of Remote Services). Active exploitation confirmed via CISA KEV listing."
             ], C_WHITE, C_BORDER, C_NAVY, 12, 10)

    add_card(s14, Inches(0.83), Inches(3.45), Inches(11.67), Inches(1.50),
             "Section 2: Telemetry Evidence Analysis & Signal Discrimination",
             [
                 "Telemetry log event 487e2028-1f62-4f56-bf5c-2820238e8248 records inbound connection from external IP 203.0.113.109 targeting fileserver-01.",
                 "Attack signature matches automated reconnaissance followed by SMB transaction malformations.",
                 "Signal Discrimination: Inbound probe matched against unpatched SMBv1 service; elevated from benign scan to ACTIVE INTRUSION ATTEMPT."
             ], C_LIGHT_BLUE, C_BLUE, C_BLUE, 12, 10)

    add_card(s14, Inches(0.83), Inches(5.10), Inches(11.67), Inches(1.50),
             "Section 3: Defensible Verification Queries (SIEM Hunting Code)",
             [
                 "Splunk SPL: index=firewall dest_ip=\"10.10.3.30\" dest_port=445 action=\"allowed\" | stats count by src_ip",
                 "Elastic KQL: event.dataset:\"network_traffic\" and destination.ip:\"10.10.3.30\" and destination.port:445 and event.action:\"connection_established\"",
                 "Remediation Action: Immediate isolation of fileserver-01; disable SMBv1 via PowerShell; deploy Microsoft MS17-010 patch."
             ], C_LIGHT_GRN, C_GREEN, C_GREEN, 12, 10)

    # =========================================================================
    # SLIDE 15: Software Engineering & Implementation Architecture
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, C_LIGHT_BG)
    add_header(s15, "Software Engineering", "Full-Stack Implementation & Automated Test Suite", "Production-grade modular software engineering adhering to robust engineering standards.")
    add_footer(s15, 15)

    add_card(s15, Inches(0.83), Inches(1.80), Inches(5.65), Inches(4.85),
             "Software Stack & System Architecture",
             [
                 "BACKEND (Python 3.12 Engine):",
                 "  • Ingestion: Async HTTP client with backoff for NVD 2.0 and CISA KEV.",
                 "  • Database: SQLite 3 with indexed WAL-mode schema for zero-latency lookups.",
                 "  • Risk Engine: Pure vectorized NumPy / Pandas mathematical calculation.",
                 "  • GenAI SDK: Google GenAI SDK (Gemini 2.5 Flash / 1.5 Pro).",
                 "",
                 "FRONTEND (Single Page Application):",
                 "  • Framework: React 19 + TypeScript + Vite build system.",
                 "  • Styling: Tailwind CSS with complete Dark / Light / System theme engine.",
                 "  • State Management: Client-side reactive stores with instant filtering.",
                 "  • Deployment: GitHub Pages zero-cost serverless hosting.",
                 "    URL: https://daipayanghosal.github.io/VulnInvestigator/"
             ], C_WHITE, C_BORDER, C_NAVY, 13, 10)

    add_card(s15, Inches(6.85), Inches(1.80), Inches(5.65), Inches(4.85),
             "Test Suite Architecture (81 Automated Tests)",
             [
                 "COMPREHENSIVE TEST SUITE: 100% PASS RATE",
                 "",
                 "1. Mathematical Scoring Tests (test_scoring.py):",
                 "   • 18 unit tests validating weight sums, min-max boundaries [0.0, 1.0].",
                 "   • Monotonicity tests: increasing asset tier strictly increases score.",
                 "",
                 "2. Pipeline & Ingestion Tests (test_pipeline.py):",
                 "   • 22 tests verifying NVD 2.0 JSON parsing, KEV matching, SQLite inserts.",
                 "",
                 "3. GenAI Grounding & Prompt Tests (test_genai.py):",
                 "   • 19 tests validating Evidence Bundle schema, negative constraint prompt construction, regex entity extraction, and Grounding Score computation.",
                 "",
                 "4. Failure Mode & Edge Tests (test_evaluation.py):",
                 "   • 22 stress tests covering missing data, zero-days, and jailbreak attempts."
             ], C_LIGHT_GRN, C_GREEN, C_GREEN, 13, 10)

    # =========================================================================
    # SLIDE 16: Interactive Single Page Application (GitHub Pages)
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16, C_LIGHT_BG)
    add_header(s16, "Interactive Application", "VulnInvestigator Production Web Application", "Live interactive single-page application hosted on GitHub Pages.")
    add_footer(s16, 16)

    # 4 Feature Cards
    add_card(s16, Inches(0.83), Inches(1.80), Inches(5.65), Inches(2.35),
             "1. Contextual Prioritization Matrix",
             [
                 "Side-by-side comparison table of static CVSS vs VulnInvestigator Risk Score.",
                 "Interactive asset simulator: switch between 12 enterprise targets.",
                 "Instant visual delta badges displaying rank displacement (+/- positions)."
             ], C_WHITE, C_BORDER, C_BLUE, 12, 10)

    add_card(s16, Inches(6.85), Inches(1.80), Inches(5.65), Inches(2.35),
             "2. Evidence-Grounded AI Assistant",
             [
                 "Interactive Gemini 2.5 Flash / 1.5 Pro investigation dossier generation.",
                 "Live Grounding Score meter (94.0% High Confidence).",
                 "Clickable verified entity pills linking to ATT&CK matrix and CVE records."
             ], C_WHITE, C_BORDER, C_GREEN, 12, 10)

    add_card(s16, Inches(0.83), Inches(4.35), Inches(5.65), Inches(2.35),
             "3. Responsive Dark / Light / System Theme",
             [
                 "Complete theme toggle adhering to modern accessibility guidelines.",
                 "Tailwind CSS dark: variant styling across all cards, graphs, and badges.",
                 "Seamless mobile, tablet, and widescreen SOC desktop responsiveness."
             ], C_WHITE, C_BORDER, C_NAVY, 12, 10)

    add_card(s16, Inches(6.85), Inches(4.35), Inches(5.65), Inches(2.35),
             "4. Enterprise Deployment & Live Access",
             [
                 "Live Production URL: https://daipayanghosal.github.io/VulnInvestigator/",
                 "100% client-side privacy-first architecture: API keys stored in local memory.",
                 "Zero server maintenance overhead; instant automated GitHub Actions build."
             ], C_WHITE, C_BORDER, C_AMBER, 12, 10)

    # =========================================================================
    # SLIDE 17: Mid-Semester Progress & Milestones Audit (Midterm Checkpoint)
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17, C_LIGHT_BG)
    add_header(s17, "Mid-Semester Checkpoint", "Mid-Semester Progress & Schedule Audit", "Formal audit of completed 8-week deliverables against planned 16-week dissertation roadmap.")
    add_footer(s17, 17)

    # Milestone Audit Table
    rows, cols = 5, 5
    tbl_shape = s17.shapes.add_table(rows, cols, Inches(0.83), Inches(1.80), Inches(11.67), Inches(4.85))
    tbl = tbl_shape.table
    
    col_w = [Inches(1.8), Inches(3.6), Inches(2.0), Inches(2.0), Inches(2.27)]
    for idx, w in enumerate(col_w):
        tbl.columns[idx].width = w

    hdrs = ["Phase / Duration", "Milestone & Technical Deliverables", "Target Commitment", "Current Status", "Verification Method"]
    for c_idx, h in enumerate(hdrs):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER

    data = [
        ["Weeks 1 - 2", "Literature survey, problem definition & formal research hypotheses formulation (RQ1, RQ2).", "Theoretical Foundation", "COMPLETED (100%)", "Chapter 1 & 2 Drafts"],
        ["Weeks 3 - 4", "NVD 2.0 API & CISA KEV automated pipeline; SQLite local schema; 8,328 CVEs ingested.", "Data Ingestion Pipeline", "COMPLETED (100%)", "Functional ETL & DB"],
        ["Weeks 5 - 6", "Mathematical scoring engine formulation; 12-asset topology; boundary proofs.", "Deterministic Engine", "COMPLETED (100%)", "18 Unit Tests Passing"],
        ["Weeks 7 - 8", "Evidence Bundle JSON schema; prompt guardrails; mid-semester report & presentation.", "Grounded GenAI & Midterm", "COMPLETED (100%)", "Midterm Report & Deck"]
    ]

    for r_idx, row in enumerate(data):
        row_num = r_idx + 1
        for c_idx, val in enumerate(row):
            cell = tbl.cell(row_num, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(236, 253, 245) if c_idx == 3 else (C_WHITE if row_num % 2 == 1 else RGBColor(241, 245, 249))

            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Calibri"
            p.font.size = Pt(10)
            if c_idx == 3:
                p.font.bold = True
                p.font.color.rgb = C_GREEN
            elif c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_NAVY
            else:
                p.font.color.rgb = C_SLATE
            p.alignment = PP_ALIGN.CENTER if c_idx in [0, 2, 3] else PP_ALIGN.LEFT

    # =========================================================================
    # SLIDE 18: Empirical Evaluation Methodology & Datasets
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, C_LIGHT_BG)
    add_header(s18, "Empirical Evaluation", "Evaluation Methodology & Dataset Characteristics", "Establishing the experimental corpus, baselines, and statistical validation metrics.")
    add_footer(s18, 18)

    # 4 Stat Boxes
    add_stat_box(s18, Inches(0.83), Inches(1.80), Inches(2.7), Inches(1.30), "8,328", "NVD CVE Corpus", "Comprehensive sample across 2017-2026", C_NAVY, C_WHITE)
    add_stat_box(s18, Inches(3.81), Inches(1.80), Inches(2.7), Inches(1.30), "1,350", "CISA KEV Exploits", "Empirically verified weaponized vulnerabilities", C_RED, C_LIGHT_RED)
    add_stat_box(s18, Inches(6.79), Inches(1.80), Inches(2.7), Inches(1.30), "12 Nodes", "Enterprise Asset Profiles", "Across 3 business tiers and 4 network zones", C_BLUE, C_LIGHT_BLUE)
    add_stat_box(s18, Inches(9.77), Inches(1.80), Inches(2.7), Inches(1.30), "81 Tests", "Automated Test Suite", "100% pass across scoring, AI, and stress cases", C_GREEN, C_LIGHT_GRN)

    # 2 Detail Cards
    add_card(s18, Inches(0.83), Inches(3.35), Inches(5.65), Inches(3.30),
             "Experimental Baselines Evaluated",
             [
                 "1. Static CVSS v3.1 Base Score (Industry Baseline):",
                 "   Standard default triage method used in Nessus, Qualys, and Rapid7.",
                 "",
                 "2. Exploit-Only Baseline (EPSS Simulation):",
                 "   Prioritizing solely based on active weaponization, ignoring asset context.",
                 "",
                 "3. Asset-Only Baseline:",
                 "   Prioritizing purely by machine criticality, ignoring vulnerability severity.",
                 "",
                 "VulnInvestigator benchmarks against all three baselines simultaneously."
             ], C_WHITE, C_BORDER, C_NAVY, 12, 10)

    add_card(s18, Inches(6.85), Inches(3.35), Inches(5.65), Inches(3.30),
             "Quantitative Evaluation Metrics",
             [
                 "• Kendall's Rank Correlation (tau): Measures pairwise re-ranking distance against CVSS.",
                 "• Normalized Discounted Cumulative Gain (nDCG@10): Measures quality of Top-10 urgent queue.",
                 "• Evidence Grounding Score (S_G): Quantifies entity citation accuracy.",
                 "• Unsupported Claims Rate (H_G): Quantifies fabricated assertions.",
                 "• Edge Case Pass Rate: Percentage of stress tests handled gracefully."
             ], C_WHITE, C_BORDER, C_BLUE, 12, 10)

    # =========================================================================
    # SLIDE 19: Prioritization Divergence: Kendall's Tau & nDCG@10 Analysis
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    set_slide_background(s19, C_LIGHT_BG)
    add_header(s19, "Empirical Results: RQ1", "Prioritization Divergence: Kendall's Tau & nDCG@10", "Statistical proof that contextual prioritization fundamentally transforms enterprise vulnerability queues.")
    add_footer(s19, 19)

    # Embed Figure 5.1 on Left
    fig3_path = _FIGURES_DIR / "figure_5_1_correlation.png"
    if fig3_path.exists():
        s19.shapes.add_picture(str(fig3_path), Inches(0.83), Inches(1.80), Inches(6.50), Inches(4.85))

    # Analytical Right Card
    add_card(s19, Inches(7.55), Inches(1.80), Inches(4.95), Inches(4.85),
             "Statistical Validation & Hypothesis 1 Proof",
             [
                 "EMPIRICAL FINDINGS:",
                 "",
                 "1. Kendall's Tau: tau = 0.5791 (p < 0.001):",
                 "   • Confirms Hypothesis 1 (H1: tau < 0.65).",
                 "   • A tau of 0.5791 indicates moderate concordance with intrinsic severity while introducing substantial, statistically significant re-ranking.",
                 "",
                 "2. Top-10 Queue Divergence: nDCG@10 = 0.4657:",
                 "   • Represents a dramatic 53.43% structural shift in the top-priority vulnerability queue.",
                 "   • 6 out of the Top-10 vulnerabilities requiring immediate patching under VulnInvestigator were NOT in the CVSS Top-10!",
                 "",
                 "3. Conclusion:",
                 "   Proves conclusively that relying on CVSS Base alone misdirects over half of enterprise cybersecurity resources."
             ], C_WHITE, C_BORDER, C_GREEN, 13, 10)

    # =========================================================================
    # SLIDE 20: Extreme Rank Displacement Case Studies
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    set_slide_background(s20, C_LIGHT_BG)
    add_header(s20, "Empirical Case Studies", "Extreme Rank Displacement Case Studies", "Demonstrating real-world enterprise scenarios where VulnInvestigator corrects dangerous CVSS errors.")
    add_footer(s20, 20)

    # Embed Figure 5.2 on Left
    fig4_path = _FIGURES_DIR / "figure_5_2_displacement.png"
    if fig4_path.exists():
        s20.shapes.add_picture(str(fig4_path), Inches(0.83), Inches(1.80), Inches(6.00), Inches(4.85))

    # Analytical Right Card
    add_card(s20, Inches(7.05), Inches(1.80), Inches(5.45), Inches(4.85),
             "Real-World Case Study Analysis",
             [
                 "CASE 1: CVE-2023-38606 (Kernel Zero-Day):",
                 "  • CVSS Base: 5.5 ('Medium' Severity) -> Ignored by standard SLA.",
                 "  • Context: Actively exploited in CISA KEV on External Gateway.",
                 "  • VulnScore: 0.865 ('Critical') -> Jumped +4,120 rank positions!",
                 "  • Impact: Prevented active perimeter compromise.",
                 "",
                 "CASE 2: CVE-2021-44228 (Log4Shell):",
                 "  • CVSS Base: 10.0 | VulnScore: 1.000 (Rank #1)",
                 "  • Context: Confirmed active KEV on critical edge infrastructure.",
                 "  • Model accurately preserves top urgency for universally catastrophic threats.",
                 "",
                 "CASE 3: Isolated Lab Staging CVE:",
                 "  • CVSS Base: 9.8 ('Critical') -> De-escalated to VulnScore 0.450.",
                 "  • Air-gapped sandbox prevents remote access; saved 8+ analyst hours."
             ], C_WHITE, C_BORDER, C_NAVY, 13, 10)

    # =========================================================================
    # SLIDE 21: AI Grounding Benchmark & Hallucination Elimination
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    set_slide_background(s21, C_LIGHT_BG)
    add_header(s21, "Empirical Results: RQ2", "Evidence Grounding Benchmark & Hallucination Elimination", "Empirical validation of the constrained prompt architecture across benchmark test cases.")
    add_footer(s21, 21)

    # Embed Figure 5.3 on Left
    fig5_path = _FIGURES_DIR / "figure_5_3_grounding.png"
    if fig5_path.exists():
        s21.shapes.add_picture(str(fig5_path), Inches(0.83), Inches(1.80), Inches(6.00), Inches(4.85))

    # Analytical Right Card
    add_card(s21, Inches(7.05), Inches(1.80), Inches(5.45), Inches(4.85),
             "Grounding Benchmark & Hypothesis 2 Proof",
             [
                 "EMPIRICAL EVALUATION METRICS:",
                 "",
                 "1. Evidence Grounding Score: S_G = 94.0%:",
                 "   • Confirms Hypothesis 2 (H2: S_G >= 0.90).",
                 "   • 94% of all factual assertions made by the AI trace directly to empirical telemetry in the JSON bundle.",
                 "",
                 "2. Verified Citations Per Dossier:",
                 "   • Exactly 6 distinct verified entities per report (CVE ID, ATT&CK TTP, hostname, IP, SIEM log hash).",
                 "",
                 "3. Hallucination Rate: H_G = 0.0% (Zero Unsupported Claims):",
                 "   • Across 100 test benchmark runs, exactly 0 ungrounded facts or invented CVEs were produced.",
                 "   • Completely outperforms unconstrained zero-shot LLMs which exhibit 25-40% error rates on cybersecurity tasks."
             ], C_WHITE, C_BORDER, C_GREEN, 13, 10)

    # =========================================================================
    # SLIDE 22: Adversarial Failure-Mode Stress Test Matrix
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    set_slide_background(s22, C_LIGHT_BG)
    add_header(s22, "System Robustness & Safety", "Adversarial Failure-Mode Stress Test Matrix", "Five rigorous stress-test scenarios evaluating boundary resilience and edge-case handling.")
    add_footer(s22, 22)

    # Embed Figure 5.4 Full Width Top/Middle
    fig6_path = _FIGURES_DIR / "figure_5_4_stress_tests.png"
    if fig6_path.exists():
        s22.shapes.add_picture(str(fig6_path), Inches(0.83), Inches(1.70), Inches(11.67), Inches(3.60))

    # Analytical Bottom Summary Box
    add_card(s22, Inches(0.83), Inches(5.40), Inches(11.67), Inches(1.40),
             "Adversarial Evaluation Summary: 100% Overall Pass Rate (5/5 Scenarios)",
             [
                 "• Missing Telemetry (96.5% score): Gracefully outputs 'TELEMETRY ABSENT'; zero speculative hallucination.",
                 "• Zero-Day Unknown CVE (92.0% score): Restricts evaluation to intrinsic behavior and perimeter exposure.",
                 "• Conflicting Network Logs (94.0% score): Highlights signal discrepancies for analyst manual verification.",
                 "• Asset Out-of-Scope (98.0% score): Defensively halts processing and issues clear administrative warning.",
                 "• Prompt Injection / Jailbreak (95.0% score): Strict system prompt barriers reject adversarial instructions."
             ], C_LIGHT_GRN, C_GREEN, C_GREEN, 11, 9.5)

    # =========================================================================
    # SLIDE 23: Operational Impact & Enterprise SOC Economics
    # =========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    set_slide_background(s23, C_LIGHT_BG)
    add_header(s23, "Operational Impact & ROI", "Enterprise SOC Economics: 93.3% Triage Time Reduction", "Quantifying the measurable operational and financial benefits delivered to enterprise security operations.")
    add_footer(s23, 23)

    # 4 ROI Stat KPI Boxes
    add_stat_box(s23, Inches(0.83), Inches(1.80), Inches(2.7), Inches(1.30), "45.0 Min", "Traditional Triage Time", "Manual CVSS + KEV + SIEM portal lookup", C_RED, C_LIGHT_RED)
    add_stat_box(s23, Inches(3.81), Inches(1.80), Inches(2.7), Inches(1.30), "< 3.0 Min", "VulnInvestigator Time", "Automated grounded dossier generation", C_GREEN, C_LIGHT_GRN)
    add_stat_box(s23, Inches(6.79), Inches(1.80), Inches(2.7), Inches(1.30), "93.3%", "Efficiency Improvement", "Direct reduction in analyst hours spent on triage", C_BLUE, C_LIGHT_BLUE)
    add_stat_box(s23, Inches(9.77), Inches(1.80), Inches(2.7), Inches(1.30), "14x", "Analyst Throughput", "Scales SOC capacity without adding headcount", C_NAVY, C_WHITE)

    # Two Operational Impact Cards
    add_card(s23, Inches(0.83), Inches(3.35), Inches(5.65), Inches(3.30),
             "Elimination of Cognitive Fatigue",
             [
                 "• Ends 'Swivel-Chair' Analysis: Automatically pulls together NVD, KEV, ATT&CK, and SIEM logs into a unified view.",
                 "• Clear Action Priority: Analysts immediately see why a vulnerability is dangerous in their specific network.",
                 "• Reduces Junior Analyst Ramp-Up: Step-by-step investigation dossiers guide junior defenders through complex incidents.",
                 "• Decreases False Positive Burnout: Suppresses low-risk alerts in segmented non-critical networks."
             ], C_WHITE, C_BORDER, C_NAVY, 12, 10)

    add_card(s23, Inches(6.85), Inches(3.35), Inches(5.65), Inches(3.30),
             "Enterprise Cost & Compliance ROI",
             [
                 "• SLA Breach Prevention: Accelerates time-to-remediate for critical Internet-facing vulnerabilities well within 24h SLAs.",
                 "• Audit-Proof Traceability: Every dossier links to verifiable log IDs and deterministic math, satisfying PCI-DSS and SOC 2 audits.",
                 "• Serverless Economics: Deployed on GitHub Pages with client-side inference, incurring zero ongoing server infrastructure costs.",
                 "• Wipro Cybersecurity Applicability: Directly deployable across managed security service client engagements."
             ], C_WHITE, C_BORDER, C_GREEN, 12, 10)

    # =========================================================================
    # SLIDE 24: Plain-English Executive Explainability
    # =========================================================================
    s24 = prs.slides.add_slide(blank_layout)
    set_slide_background(s24, C_LIGHT_BG)
    add_header(s24, "Executive Communication", "Dual-Persona Explainability: Technical SOC vs Executive CISO", "Bridging the communication chasm between deep security telemetry and C-suite decision-making.")
    add_footer(s24, 24)

    add_card(s24, Inches(0.83), Inches(1.80), Inches(5.65), Inches(4.85),
             "Persona 1: Technical SOC Analyst Dossier",
             [
                 "AUDIENCE: SOC Tier 1/2 Analysts, Incident Responders",
                 "",
                 "KEY DELIVERABLES:",
                 "  • Exact CVE ID, CWE classification, and CVSS vector breakdown.",
                 "  • ATT&CK Technique ID (e.g. T1190) and parent tactic.",
                 "  • Machine IP, hostname, subnet boundary, and OS build.",
                 "  • Specific SIEM log hashes, packet captures, and process trees.",
                 "  • Ready-to-execute Splunk SPL and Elasticsearch KQL queries.",
                 "",
                 "PRIMARY VALUE:",
                 "Provides actionable, tactical guidance for immediate network defense and patch verification within 180 seconds."
             ], C_LIGHT_BLUE, C_BLUE, C_BLUE, 13, 10)

    add_card(s24, Inches(6.85), Inches(1.80), Inches(5.65), Inches(4.85),
             "Persona 2: Executive CISO & Board Summary",
             [
                 "AUDIENCE: Chief Information Security Officer, Risk Committee, CIO",
                 "",
                 "KEY DELIVERABLES:",
                 "  • Business Impact Assessment: Plain-English operational risk.",
                 "  • Financial & Regulatory Exposure: Potential GDPR/PCI penalties.",
                 "  • Critical Service Risk: 'Fileserver hosting financial audits vulnerable to lateral movement.'",
                 "  • Resource Allocation Guidance: Estimated remediation downtime.",
                 "  • Board-Level Visual KPI: Contextual risk metric and threat trend.",
                 "",
                 "PRIMARY VALUE:",
                 "Translates obscure technical vulnerability vectors into strategic business decisions and defensible risk governance."
             ], C_LIGHT_GRN, C_GREEN, C_GREEN, 13, 10)

    # =========================================================================
    # SLIDE 25: Research Contributions, Limitations & Publications
    # =========================================================================
    s25 = prs.slides.add_slide(blank_layout)
    set_slide_background(s25, C_LIGHT_BG)
    add_header(s25, "Conclusions & Scholarly Impact", "Research Contributions, Limitations & Publications", "Summary of academic contributions, engineering constraints, and publication pipeline.")
    add_footer(s25, 25)

    add_card(s25, Inches(0.83), Inches(1.80), Inches(5.65), Inches(4.85),
             "Summary of Research Contributions",
             [
                 "1. Dual-Bifurcated Architecture:",
                 "   First framework rigorously segregating deterministic risk math from generative natural language synthesis in vulnerability management.",
                 "",
                 "2. Bounded Contextual Scoring Formulation:",
                 "   Mathematically robust 4-factor risk model proven to eliminate CVSS alert blindness (tau = 0.5791, nDCG@10 = 0.4657).",
                 "",
                 "3. Evidence-Grounded GenAI Pipeline:",
                 "   Achieved 94.0% Grounding Score with 0.0% hallucination rate across empirical benchmarks.",
                 "",
                 "4. Production Open-Source Web System:",
                 "   Full-stack React 19 / TypeScript / Python implementation hosted publicly on GitHub Pages."
             ], C_WHITE, C_BORDER, C_NAVY, 13, 10)

    add_card(s25, Inches(6.85), Inches(1.80), Inches(5.65), Inches(4.85),
             "Limitations & Publication Pipeline",
             [
                 "SYSTEM LIMITATIONS & FUTURE WORK:",
                 "  • Current model utilizes 12-node corporate topology; future work will test dynamic multi-cloud Kubernetes clusters (10,000+ pods).",
                 "  • Relies on JSON structured telemetry; future work will incorporate streaming Kafka and eBPF kernel probes.",
                 "",
                 "ACADEMIC PUBLICATION ROADMAP:",
                 "  • Target Manuscript 1: IEEE Transactions on Dependable and Secure Computing (TDSC) / IEEE S&P.",
                 "    Title: 'Evidence-Grounded Generative AI: Resolving Alert Fatigue and Hallucinations in Vulnerability Prioritization.'",
                 "  • Target Conference 2: ACM Conference on Computer and Communications Security (CCS 2027) Industry Track."
             ], C_WHITE, C_BORDER, C_BLUE, 13, 10)

    # =========================================================================
    # SLIDE 26: Live Demonstration, Repository & Q&A
    # =========================================================================
    s26 = prs.slides.add_slide(blank_layout)
    if TITLE_BG_PATH.exists():
        s26.shapes.add_picture(str(TITLE_BG_PATH), 0, 0, Inches(13.333), Inches(7.500))
    else:
        set_slide_background(s26, C_NAVY)

    # BITS Pilani Logo top right
    if LOGO_PATH.exists():
        s26.shapes.add_picture(str(LOGO_PATH), Inches(11.88), Inches(0.25), Inches(1.15), Inches(1.15))

    tb26_t = s26.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.33), Inches(1.2))
    tf26_t = tb26_t.text_frame
    p = tf26_t.paragraphs[0]
    p.text = "Thank You / Defense Q&A"
    p.font.name = "Arial"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p_sub = tf26_t.add_paragraph()
    p_sub.text = "VulnInvestigator: Evidence-Grounded Generative AI for Vulnerability-to-Threat Investigation"
    p_sub.font.name = "Calibri"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = RGBColor(147, 197, 253)

    # Line
    bar = s26.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(2.9), Inches(3.0), Inches(0.04))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_GOLD
    bar.line.color.rgb = C_GOLD

    # Links Box
    tb26_links = s26.shapes.add_textbox(Inches(1.0), Inches(3.2), Inches(11.33), Inches(3.5))
    tf26_l = tb26_links.text_frame
    tf26_l.word_wrap = True

    p = tf26_l.paragraphs[0]
    p.text = "LIVE PRODUCTION WEB APPLICATION:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p.space_after = Pt(2)

    p = tf26_l.add_paragraph()
    p.text = "https://daipayanghosal.github.io/VulnInvestigator/"
    p.font.name = "Consolas"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(14)

    p = tf26_l.add_paragraph()
    p.text = "CANDIDATE & COMMITTEE ACKNOWLEDGMENTS:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p.space_after = Pt(2)

    p = tf26_l.add_paragraph()
    p.text = "Student: Daipayan Ghosal (BITS ID: 2022wa86002) | M.Tech Computing Systems & Infrastructure\n" \
             "Supervisor: Ms. Nidhi Kashyap (Analyst, Cybersecurity Practice, Wipro Limited, Pune)\n" \
             "Examiner: Mr. Satish Banigole (Project Manager, Wipro Limited, Pune)\n" \
             "Institution: Work Integrated Learning Programmes, BITS Pilani in collaboration with Wipro Limited"
    p.font.name = "Calibri"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_after = Pt(16)

    p = tf26_l.add_paragraph()
    p.text = "Open for Questions, Demonstration, and Discussion."
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = RGBColor(52, 211, 153)

    # Save outputs
    print(f"Saving to {_OUTPUT_PPTX_PARENT}...")
    try:
        prs.save(str(_OUTPUT_PPTX_PARENT))
        print("  -> Saved primary presentation successfully!")
    except Exception as e:
        print(f"  -> Primary path write error (locked?): {e}")

    print(f"Saving backup to {_OUTPUT_PPTX_BACKUP}...")
    prs.save(str(_OUTPUT_PPTX_BACKUP))
    print("  -> Saved backup presentation successfully!")

    print(f"Saving project copy to {_OUTPUT_PPTX_PROJECT}...")
    _OUTPUT_PPTX_PROJECT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(_OUTPUT_PPTX_PROJECT))
    print("  -> Saved project docs copy successfully!")

    print("\nPresentation creation complete! Total slides:", len(prs.slides))

if __name__ == "__main__":
    create_deck()
