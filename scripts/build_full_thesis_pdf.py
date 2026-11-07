import os
import re
import subprocess
import shutil

MD_PATH = r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents\DISSERTATION_FINAL_THESIS.md"
DOC_DIR = r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents"
TEX_PATH = os.path.join(DOC_DIR, "DISSERTATION_FINAL_THESIS.tex")
PDF_PATH = os.path.join(DOC_DIR, "DISSERTATION_FINAL_THESIS.pdf")
FINAL_NAMED_PDF = os.path.join(DOC_DIR, "Daipayan_Ghosal_2022wa86002_Final_Dissertation.pdf")

with open(MD_PATH, 'r', encoding='utf-8') as f:
    raw_text = f.read()

# 1. Unicode substitutions
unicode_map = {
    '–': '--', '—': '---', '“': '``', '”': "''", '‘': '`', '’': "'",
    '…': '...', '≤': r'$\le$', '≥': r'$\ge$', '≠': r'$\ne$', '±': r'$\pm$',
    '×': r'$\times$', '∈': r'$\in$', '∑': r'$\sum$', '•': r'\textbullet{} ',
    '·': r'$\cdot$', '→': r'$\rightarrow$', '←': r'$\leftarrow$',
    '│': '|', '─': '-', '┌': '+', '┐': '+', '└': '+', '┘': '+',
    '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
    '▼': 'v', '▲': '^', '►': '>', '◄': '<', '▶': '>', '◀': '<',
    '°': r'$^\circ$', 'τ': r'$\tau$', 'ρ': r'$\rho$', 'λ': r'$\lambda$',
    'α': r'$\alpha$', 'β': r'$\beta$', '✓': r'[PASS]', '✗': r'[FAIL]',
    'ä': r'\"{a}', 'ü': r'\"{u}', '−': '-', '✅': r'[PASS]', '❌': r'[FAIL]'
}
for k, v in unicode_map.items():
    raw_text = raw_text.replace(k, v)

def escape_prose(s):
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$|`.*?`)', s, flags=re.DOTALL)
    out = []
    for part in parts:
        if not part:
            continue
        if part.startswith('$$') or (part.startswith('$') and part.endswith('$')):
            out.append(part)
        elif part.startswith('`') and part.endswith('`'):
            inner = part[1:-1]
            inner_esc = (inner.replace('\\', r'\textbackslash{}')
                              .replace('&', r'\&')
                              .replace('%', r'\%')
                              .replace('#', r'\#')
                              .replace('_', r'\_')
                              .replace('{', r'\{')
                              .replace('}', r'\}')
                              .replace('^', r'\textasciicircum{}')
                              .replace('~', r'\textasciitilde{}'))
            out.append(r'\texttt{' + inner_esc + '}')
        else:
            p = part
            p = p.replace('&', r'\&').replace('%', r'\%').replace('#', r'\#').replace('_', r'\_')
            p = re.sub(r'"([^"]*)"', r"``\1''", p)
            p = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', p)
            p = re.sub(r'\*(.*?)\*', r'\\textit{\1}', p)
            p = re.sub(r'\[(.*?)\]\((https?://.*?)\)', r'\\href{\2}{\1}', p)
            out.append(p)
    return ''.join(out)

def clean_for_toc(s):
    s = s.replace('**', '').replace('*', '')
    s = re.sub(r'\$S_{\\text\{cvss\}}\$', 'S_cvss', s)
    s = re.sub(r'\$S_{\\text\{kev\}}\$', 'S_kev', s)
    s = re.sub(r'\$S_{\\text\{asset\}}\$', 'S_asset', s)
    s = re.sub(r'\$S_{\\text\{exp\}}\$', 'S_exp', s)
    s = re.sub(r'\$\\tau\s*=\s*0\.5791\$', 'tau = 0.5791', s)
    s = re.sub(r'\$\\rho\s*=\s*0\.7539\$', 'rho = 0.7539', s)
    s = re.sub(r'\$0\.4657\$', '0.4657', s)
    s = re.sub(r'\$\\tau\$', 'tau', s)
    s = re.sub(r'\$\\rho\$', 'rho', s)
    s = re.sub(r'\$([^\$]+)\$', r'\1', s)
    s = s.replace('&', 'and').replace('_', ' ').replace('#', '')
    return s.strip()

# Parse Abbreviations table
pos_abbr = raw_text.find('## LIST OF ABBREVIATIONS & SYMBOLS')
pos_chap1 = raw_text.find('# CHAPTER 1: INTRODUCTION')
abbr_section = raw_text[pos_abbr:pos_chap1]
abbr_lines = []
for line in abbr_section.splitlines():
    m = re.match(r'^\*\s+\*\*(.*?)\*\*:\s*(.*)', line.strip())
    if m:
        abbr_lines.append((m.group(1).strip(), m.group(2).strip()))

abbr_table_tex = [
    r"\chapter*{List of Abbreviations \& Symbols}",
    r"\addcontentsline{toc}{chapter}{List of Abbreviations \& Symbols}",
    r"\noindent",
    r"\begin{tabularx}{\textwidth}{@{}p{3.8cm} L@{}}",
    r"\hline",
    r"\textbf{Abbreviation / Symbol} & \textbf{Full Term / Definition} \\",
    r"\hline\hline"
]
for ab, desc in abbr_lines:
    abbr_table_tex.append(escape_prose(ab) + " & " + escape_prose(desc) + r" \\ \hline")
abbr_table_tex.append(r"\end{tabularx}")
abbr_table_tex_str = "\n".join(abbr_table_tex)

# Parse Chapters (from Chapter 1 up to References)
pos_ref = raw_text.find('# REFERENCES')
body_text = raw_text[pos_chap1:pos_ref]

def render_table(tbl_lines, cap, is_checklist=False):
    rows = []
    for l in tbl_lines:
        cells = [c.strip() for c in l.split('|')[1:-1]]
        if all(re.match(r'^:?-+:?$', c) for c in cells if c):
            continue
        rows.append(cells)
    if not rows:
        return ""
    ncols = len(rows[0])
    first_row_str = " ".join(rows[0])
    
    if is_checklist or "S.No." in first_row_str or "Checklist" in first_row_str:
        spec = "|>{\\centering\\arraybackslash}p{1.0cm}|>{\\raggedright\\arraybackslash}p{6.5cm}|>{\\centering\\arraybackslash}p{1.4cm}|>{\\raggedright\\arraybackslash}X|"
        size = "\\footnotesize"
        out = [r"\begin{center}", size, r"\setlength{\tabcolsep}{3pt}"]
        out.append(r"\begin{tabularx}{\textwidth}{" + spec + r"}")
        out.append(r"\hline")
        hcells = [r"\textbf{" + escape_prose(c) + r"}" for c in rows[0]]
        out.append(" & ".join(hcells) + r" \\ \hline\hline")
        for r in rows[1:]:
            while len(r) < ncols:
                r.append("")
            cells = [escape_prose(c) for c in r[:ncols]]
            out.append(" & ".join(cells) + r" \\ \hline")
        out.append(r"\end{tabularx}")
        out.append(r"\end{center}")
        return "\n".join(out)
    
    if ncols == 8: # Table 4.1
        spec = "|>{\\raggedright\\arraybackslash}p{1.4cm}|>{\\raggedright\\arraybackslash}p{1.6cm}|>{\\raggedright\\arraybackslash}p{1.5cm}|>{\\raggedright\\arraybackslash}p{1.7cm}|>{\\raggedright\\arraybackslash}X|>{\\centering\\arraybackslash}p{1.2cm}|>{\\centering\\arraybackslash}p{1.6cm}|>{\\raggedright\\arraybackslash}X|"
        size = "\\scriptsize"
    elif ncols == 7: # Table 5.3
        spec = "|>{\\raggedright\\arraybackslash}p{2.1cm}|>{\\centering\\arraybackslash}p{1.2cm}|>{\\centering\\arraybackslash}p{1.1cm}|>{\\centering\\arraybackslash}p{1.4cm}|>{\\centering\\arraybackslash}p{1.3cm}|>{\\centering\\arraybackslash}p{1.3cm}|>{\\raggedright\\arraybackslash}X|"
        size = "\\scriptsize"
    elif ncols == 6: # Table 2.1
        spec = "|>{\\raggedright\\arraybackslash}p{2.0cm}|>{\\centering\\arraybackslash}p{2.0cm}|>{\\centering\\arraybackslash}p{1.8cm}|>{\\centering\\arraybackslash}p{1.8cm}|>{\\centering\\arraybackslash}p{2.0cm}|>{\\raggedright\\arraybackslash}X|"
        size = "\\scriptsize"
    elif ncols == 5: # Table 5.5
        spec = "|>{\\raggedright\\arraybackslash}p{2.5cm}|>{\\raggedright\\arraybackslash}p{2.8cm}|>{\\raggedright\\arraybackslash}X|>{\\raggedright\\arraybackslash}X|>{\\centering\\arraybackslash}p{1.2cm}|"
        size = "\\scriptsize"
    elif ncols == 4:
        spec = "|>{\\raggedright\\arraybackslash}p{4.2cm}|>{\\centering\\arraybackslash}p{2.0cm}|>{\\centering\\arraybackslash}p{2.0cm}|>{\\raggedright\\arraybackslash}X|"
        size = "\\small"
    elif ncols == 3: # Table 3.2, 3.3, 5.1
        spec = "|>{\\raggedright\\arraybackslash}p{3.8cm}|>{\\centering\\arraybackslash}p{2.2cm}|>{\\raggedright\\arraybackslash}X|"
        size = "\\small"
    else:
        spec = "|" + "X|" * ncols
        size = "\\small"
    
    out = [r"\begin{table}[htbp]", r"\centering", size, r"\setlength{\tabcolsep}{3pt}"]
    out.append(r"\begin{tabularx}{\textwidth}{" + spec + r"}")
    out.append(r"\hline")
    hcells = [r"\textbf{" + escape_prose(c) + r"}" for c in rows[0]]
    out.append(" & ".join(hcells) + r" \\ \hline\hline")
    for r in rows[1:]:
        while len(r) < ncols:
            r.append("")
        cells = [escape_prose(c) for c in r[:ncols]]
        out.append(" & ".join(cells) + r" \\ \hline")
    out.append(r"\end{tabularx}")
    if cap:
        m = re.match(r'\*\*Table\s+(\d+\.\d+)\*\*:\s*(.*)', cap)
        if m:
            out.append(r"\caption{" + escape_prose(m.group(2)) + r"}")
            out.append(r"\label{tab:" + m.group(1).replace('.', '_') + r"}")
        else:
            out.append(r"\caption{" + escape_prose(cap.replace('**', '')) + r"}")
    out.append(r"\end{table}")
    return "\n".join(out)

def parse_blocks(md_text):
    lines = md_text.splitlines()
    i = 0
    blocks = []
    while i < len(lines):
        line = lines[i]
        sline = line.strip()
        if not sline or sline == '---' or '<div' in sline or '</div>' in sline or sline.startswith('<br'):
            i += 1
            continue
        
        # 1. Code blocks
        if sline.startswith('```'):
            lang = sline[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            code_str = '\n'.join(code_lines)
            
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            cap = ""
            label = ""
            if j < len(lines) and (lines[j].strip().startswith('**Figure') or lines[j].strip().startswith('*Figure')):
                m = re.match(r'[\*]+\s*Figure\s+(\d+\.\d+)[\*:]+\s*(.*?)(?:\*|$)', lines[j].strip())
                if m:
                    fnum = m.group(1)
                    if fnum != "3.2":
                        cap = m.group(2).strip()
                        label = f"fig:{fnum.replace('.', '_')}"
                    i = j + 1
            blocks.append(('code', lang, code_str, cap, label))
            continue
        
        # 2. Display math
        if sline.startswith('$$'):
            math_lines = []
            if sline.endswith('$$') and len(sline) > 2:
                math_lines.append(sline[2:-2].strip())
                i += 1
            else:
                first = sline[2:].strip()
                if first:
                    math_lines.append(first)
                i += 1
                while i < len(lines) and not lines[i].strip().endswith('$$'):
                    math_lines.append(lines[i].strip())
                    i += 1
                if i < len(lines):
                    last = lines[i].strip()[:-2].strip()
                    if last:
                        math_lines.append(last)
                    i += 1
            blocks.append(('display_math', '\n'.join(math_lines)))
            continue
        
        # 3. Image
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', sline)
        if img_match:
            raw_cap = img_match.group(1)
            src = img_match.group(2)
            i += 1
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            cap = raw_cap
            label = ""
            if j < len(lines) and (lines[j].strip().startswith('**Figure') or lines[j].strip().startswith('*Figure')):
                m = re.match(r'[\*]+\s*Figure\s+(\d+\.\d+)[\*:]+\s*(.*?)(?:\*|$)', lines[j].strip())
                if m:
                    cap = m.group(2).strip()
                    label = f"fig:{m.group(1).replace('.', '_')}"
                    i = j + 1
            else:
                m = re.match(r'Figure\s+(\d+\.\d+):\s*(.*)', raw_cap)
                if m:
                    cap = m.group(2).strip()
                    label = f"fig:{m.group(1).replace('.', '_')}"
            blocks.append(('image', cap, src, label))
            continue
        
        # 4. Table
        if sline.startswith('|') and sline.endswith('|'):
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                tbl_lines.append(lines[i].strip())
                i += 1
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            cap = ""
            if j < len(lines) and lines[j].strip().startswith('**Table'):
                cap = lines[j].strip()
                i = j + 1
            blocks.append(('table', tbl_lines, cap))
            continue
        
        # 5. Headings
        if sline.startswith('# '):
            title = sline[2:].strip()
            title = re.sub(r'^CHAPTER\s+\d+:\s*', '', title, flags=re.IGNORECASE)
            blocks.append(('h1', title))
            i += 1
            continue
        
        if sline.startswith('## '):
            title = sline[3:].strip()
            title = re.sub(r'^\d+\.\d+\s+', '', title)
            blocks.append(('h2', title))
            i += 1
            continue
        
        if sline.startswith('### '):
            title = sline[4:].strip()
            title = re.sub(r'^\d+\.\d+\.\d+\s+', '', title)
            title = title.replace('**', '')
            blocks.append(('h3', title))
            i += 1
            continue
        
        if sline.startswith('#### '):
            title = sline[5:].strip()
            title = title.replace('**', '')
            blocks.append(('h4', title))
            i += 1
            continue
        
        # 6. Blockquote
        if sline.startswith('>'):
            qlines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                qlines.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(('quote', '\n'.join(qlines)))
            continue
        
        # 7. Unordered list
        if sline.startswith('* ') or sline.startswith('- '):
            items = []
            while i < len(lines) and (lines[i].strip().startswith('* ') or lines[i].strip().startswith('- ')):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append(('itemize', items))
            continue
        
        # 8. Numbered list
        if re.match(r'^\d+\.\s+', sline):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                m = re.match(r'^\d+\.\s+(.*)', lines[i].strip())
                items.append(m.group(1).strip())
                i += 1
            blocks.append(('enumerate', items))
            continue
        
        # 9. Normal paragraph
        para = []
        while i < len(lines):
            l = lines[i]
            sl = l.strip()
            if (not sl or sl.startswith('#') or sl.startswith('|') or sl.startswith('```') or 
                sl.startswith('$$') or sl.startswith('![') or sl.startswith('>') or 
                sl.startswith('* ') or sl.startswith('- ') or re.match(r'^\d+\.\s+', sl) or 
                sl == '---' or '<div' in sl or sl.startswith('<br')):
                break
            para.append(l)
            i += 1
        if para:
            blocks.append(('para', ' '.join(para)))

    return blocks

def render_blocks(blocks):
    out = []
    for b in blocks:
        btype = b[0]
        if btype == 'h1':
            toc_title = clean_for_toc(b[1])
            out.append(r"\chapter[" + toc_title + r"]{" + escape_prose(b[1]) + r"}")
        elif btype == 'h2':
            toc_title = clean_for_toc(b[1])
            out.append(r"\section[" + toc_title + r"]{" + escape_prose(b[1]) + r"}")
        elif btype == 'h3':
            toc_title = clean_for_toc(b[1])
            out.append(r"\subsection[" + toc_title + r"]{" + escape_prose(b[1]) + r"}")
        elif btype == 'h4':
            toc_title = clean_for_toc(b[1])
            out.append(r"\subsubsection[" + toc_title + r"]{" + escape_prose(b[1]) + r"}")
        elif btype == 'para':
            out.append(escape_prose(b[1]) + "\n")
        elif btype == 'quote':
            out.append(r"\begin{quote}" + "\n" + escape_prose(b[1]) + "\n" + r"\end{quote}")
        elif btype == 'display_math':
            out.append(r"\begin{equation}" + "\n" + b[1] + "\n" + r"\end{equation}")
        elif btype == 'itemize':
            out.append(r"\begin{itemize}")
            for item in b[1]:
                out.append(r"  \item " + escape_prose(item))
            out.append(r"\end{itemize}")
        elif btype == 'enumerate':
            out.append(r"\begin{enumerate}")
            for item in b[1]:
                out.append(r"  \item " + escape_prose(item))
            out.append(r"\end{enumerate}")
        elif btype == 'table':
            out.append(render_table(b[1], b[2]))
        elif btype == 'image':
            cap, src, label = b[1], b[2], b[3]
            out.append(r"\begin{figure}[htbp]")
            out.append(r"\centering")
            out.append(r"\includegraphics[width=0.88\textwidth,keepaspectratio]{" + src + r"}")
            out.append(r"\caption{" + escape_prose(cap) + r"}")
            if label:
                out.append(r"\label{" + label + r"}")
            out.append(r"\end{figure}")
        elif btype == 'code':
            lang, code_str, cap, label = b[1], b[2], b[3], b[4]
            if cap:
                out.append(r"\begin{figure}[htbp]")
                out.append(r"\centering")
                out.append(r"\begin{lstlisting}")
                out.append(code_str)
                out.append(r"\end{lstlisting}")
                out.append(r"\caption{" + escape_prose(cap) + r"}")
                if label:
                    out.append(r"\label{" + label + r"}")
                out.append(r"\end{figure}")
            else:
                out.append(r"\begin{lstlisting}")
                out.append(code_str)
                out.append(r"\end{lstlisting}")
    return "\n\n".join(out)

chapters_tex = render_blocks(parse_blocks(body_text))

# Parse References
pos_app = raw_text.find('# APPENDICES')
ref_text = raw_text[pos_ref:pos_app]
ref_items = []
for l in ref_text.splitlines():
    m = re.match(r'^\d+\.\s+(.*)', l.strip())
    if m:
        ref_items.append(m.group(1).strip())

refs_tex = [
    r"\chapter*{References}",
    r"\addcontentsline{toc}{chapter}{References}",
    r"\begin{enumerate}"
]
for item in ref_items:
    refs_tex.append(r"  \item " + escape_prose(item))
refs_tex.append(r"\end{enumerate}")
refs_tex_str = "\n".join(refs_tex)

# Parse Appendices
pos_pub = raw_text.find('## LIST OF PUBLICATIONS / CONFERENCE PRESENTATIONS')
app_text = raw_text[pos_app:pos_pub]

app_sections = re.split(r'##\s+APPENDIX\s+([A-Z]):\s*(.*)', app_text)
appendices_tex = [r"\appendix"]
for k in range(1, len(app_sections), 3):
    app_letter = app_sections[k]
    app_title = app_sections[k+1].strip()
    app_content = app_sections[k+2].strip()
    toc_app_title = clean_for_toc(app_title)
    appendices_tex.append(r"\chapter[" + toc_app_title + r"]{" + escape_prose(app_title) + r"}")
    appendices_tex.append(render_blocks(parse_blocks(app_content)))

appendices_tex_str = "\n\n".join(appendices_tex)

# Parse Publications
pos_chk = raw_text.find('## CHECK LIST OF ITEMS FOR FINAL REPORT')
pub_text = raw_text[pos_pub:pos_chk]
pub_items = []
for l in pub_text.splitlines():
    m = re.match(r'^\d+\.\s+(.*)', l.strip())
    if m:
        pub_items.append(m.group(1).strip())

pubs_tex = [
    r"\chapter*{List of Publications / Conference Presentations}",
    r"\addcontentsline{toc}{chapter}{List of Publications / Conference Presentations}",
    r"\begin{enumerate}"
]
for item in pub_items:
    pubs_tex.append(r"  \item " + escape_prose(item))
pubs_tex.append(r"\end{enumerate}")
pubs_tex_str = "\n".join(pubs_tex)

# Parse Checklist
chk_text = raw_text[pos_chk:]
chk_lines = chk_text.splitlines()
chk_table_lines = [l.strip() for l in chk_lines if l.strip().startswith('|') and l.strip().endswith('|')]
chk_table_tex = render_table(chk_table_lines, "", is_checklist=True)

checklist_tex_str = f"""
\\chapter*{{Check List of Items for Final Report}}
\\addcontentsline{{toc}}{{chapter}}{{Check List of Items for Final Report}}

\\textit{{(As prescribed by Birla Institute of Technology \\& Science, Pilani -- CSIW ZG628T Guidelines)}}\\par
\\vspace{{0.3cm}}

{chk_table_tex}

\\vspace{{0.8cm}}
\\textbf{{Student Declaration:}}\\par
I hereby declare that this dissertation report entitled \\textit{{``Evidence-Grounded Generative AI for Vulnerability-to-Threat Investigation and Risk Prioritization''}} embodies my original research, design, and implementation work under the guidance of my supervisor. All literature citations and external data sources have been rigorously referenced.\\par
\\vspace{{1.6cm}}
\\noindent
\\rule{{7cm}}{{0.4pt}}\\\\
\\textbf{{Daipayan Ghosal}}\\\\
(BITS ID: 2022wa86002)\\\\
Student, M.Tech (Computing Systems \\& Infrastructure)\\\\
BITS Pilani -- Wipro Collaborative Programme (WIMS)\\\\
Date: November 06, 2026\\par
\\vspace{{1.0cm}}
\\textbf{{Supervisor Endorsement:}}\\par
I have reviewed this final dissertation report and verified the completion of all items in the checklist above. The report satisfies the technical and academic requirements of CSIW ZG628T Dissertation.\\par
\\vspace{{1.6cm}}
\\noindent
\\rule{{7cm}}{{0.4pt}}\\\\
\\textbf{{Ms. Nidhi Kashyap}}\\\\
Analyst, Cybersecurity Practice\\\\
Wipro Limited, Pune\\\\
Dissertation Supervisor\\\\
Date: November 06, 2026
"""

# Extract Acknowledgements and Abstract
pos_ack = raw_text.find('## ACKNOWLEDGEMENTS')
pos_abs = raw_text.find('## ABSTRACT')
pos_toc = raw_text.find('## TABLE OF CONTENTS')

ack_body = raw_text[pos_ack:pos_abs].replace('## ACKNOWLEDGEMENTS', '').strip()
ack_body = re.sub(r'<div.*?>.*?</div>', '', ack_body)
ack_body = re.sub(r'---', '', ack_body)
ack_body = re.sub(r'<br\s*/?>', '\n', ack_body).strip()
ack_lines = [l for l in ack_body.splitlines() if not (l.startswith('**Daipayan') or l.startswith('BITS ID') or l.startswith('Pune,'))]
ack_prose = "\n\n".join(l.strip() for l in "\n".join(ack_lines).split("\n\n") if l.strip())

abs_body = raw_text[pos_abs:pos_toc].replace('## ABSTRACT', '').strip()
abs_body = re.sub(r'<div.*?>.*?</div>', '', abs_body)
abs_body = re.sub(r'---', '', abs_body)
abs_prose = "\n\n".join(l.strip() for l in abs_body.split("\n\n") if l.strip())

# Full LaTeX document assembly
full_tex = f"""\\documentclass[12pt,a4paper]{{report}}
\\usepackage[a4paper,left=1.5in,right=1.0in,top=1.0in,bottom=1.0in]{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{tabularx}}
\\usepackage{{array}}
\\usepackage{{xcolor}}
\\usepackage{{listings}}
\\usepackage{{url}}
\\usepackage[pdftex,colorlinks=true,linkcolor=black,citecolor=blue,urlcolor=blue]{{hyperref}}

% Line spacing
\\linespread{{1.3}}

% Custom column types for tabularx
\\newcolumntype{{L}}{{>{{\\raggedright\\arraybackslash}}X}}
\\newcolumntype{{C}}{{>{{\\centering\\arraybackslash}}X}}
\\newcolumntype{{R}}{{>{{\\raggedleft\\arraybackslash}}X}}

% Listings configuration
\\lstset{{
  basicstyle=\\fontsize{{7.5pt}}{{9pt}}\\ttfamily,
  breaklines=true,
  breakatwhitespace=false,
  frame=single,
  framerule=0.5pt,
  rulecolor=\\color{{gray!60}},
  backgroundcolor=\\color{{gray!4}},
  numbers=none,
  tabsize=2,
  columns=fullflexible,
  keepspaces=true
}}

\\setlength{{\\parskip}}{{0.6em}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}

% FRONT COVER
\\begin{{titlepage}}
\\centering
\\vspace*{{0.5cm}}
{{\\Large\\bfseries EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION\\par}}
\\vspace{{1.5cm}}
{{\\large\\bfseries CSIW ZG628T DISSERTATION\\par}}
\\vspace{{2.0cm}}
{{\\large\\bfseries Daipayan Ghosal\\par}}
{{\\large\\bfseries BITS ID No.: 2022wa86002\\par}}
\\vspace{{2.5cm}}
{{\\bfseries Dissertation Work Carried Out At:}}\\par
{{\\large Wipro Limited\\par}}
\\vfill
{{\\large\\bfseries BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE\\par}}
{{\\normalsize Pilani (Rajasthan) India\\par}}
\\vspace{{0.3cm}}
{{\\normalsize November, 2026\\par}}
\\end{{titlepage}}

% INNER TITLE PAGE
\\begin{{titlepage}}
\\centering
\\vspace*{{0.3cm}}
{{\\large\\bfseries CSIW ZG628T DISSERTATION\\par}}
\\vspace{{0.8cm}}
{{\\Large\\bfseries EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION\\par}}
\\vspace{{0.8cm}}
{{\\normalsize Submitted in partial fulfilment of the requirements of\\par}}
{{\\bfseries M. Tech Computing Systems \\& Infrastructure Degree Program\\par}}
{{\\normalsize (BITS -- WIPRO Collaborative Programme -- WIMS)\\par}}
\\vspace{{1.0cm}}
{{\\bfseries Daipayan Ghosal\\par}}
{{\\normalsize ID No.: 2022wa86002\\par}}
{{\\normalsize\\textit{{Email}}: \\url{{2022wa86002@wilp.bits-pilani.ac.in}}\\par}}
\\vspace{{1.0cm}}
{{\\normalsize Under the Supervision of\\par}}
{{\\bfseries Ms. Nidhi Kashyap\\par}}
{{\\normalsize Analyst, Cybersecurity Practice\\par}}
{{\\normalsize Wipro Limited, Pune\\par}}
{{\\normalsize\\textit{{Email}}: \\url{{nidhi.kashyap@wipro.com}}\\par}}
\\vspace{{0.8cm}}
{{\\normalsize Additional Examiner:\\par}}
{{\\bfseries Mr. Satish Banigole\\par}}
{{\\normalsize Project Manager, Wipro Limited, Pune\\par}}
{{\\normalsize\\textit{{Email}}: \\url{{satish.banigole@wipro.com}}\\par}}
\\vspace{{0.8cm}}
{{\\normalsize\\bfseries Dissertation Work Carried Out At:\\par}}
{{\\normalsize Wipro Limited, Pune / Bangalore\\par}}
\\vfill
{{\\large\\bfseries BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE\\par}}
{{\\normalsize PILANI (RAJASTHAN)\\par}}
\\vspace{{0.3cm}}
{{\\normalsize November, 2026\\par}}
\\end{{titlepage}}

\\pagenumbering{{roman}}
\\setcounter{{page}}{{1}}

% CERTIFICATE FROM SUPERVISOR
\\chapter*{{Certificate from the Supervisor}}
\\addcontentsline{{toc}}{{chapter}}{{Certificate from the Supervisor}}
\\begin{{center}}
\\textbf{{BIRLA INSTITUTE OF TECHNOLOGY \\& SCIENCE, PILANI}}\\\\
\\textbf{{WORK INTEGRATED LEARNING PROGRAMMES (WILP) DIVISION}}
\\end{{center}}
\\vspace{{0.5cm}}
This is to certify that the Dissertation entitled:
\\begin{{quote}}
\\textbf{{``Evidence-Grounded Generative AI for Vulnerability-to-Threat Investigation and Risk Prioritization''}}
\\end{{quote}}
submitted by \\textbf{{Daipayan Ghosal}} (BITS ID No. \\textbf{{2022wa86002}}) in partial fulfillment of the requirements of course \\textbf{{CSIW ZG628T: Dissertation}} for the \\textbf{{M.Tech in Computing Systems \\& Infrastructure}} Degree Program, embodies the bonafide work done by him under my supervision at \\textbf{{Wipro Limited}}.

In my opinion, this dissertation fulfills the rigorous academic and practical standards established by the Institute for Master of Technology level research. The results presented in this report have been verified against working prototype implementations, empirical benchmarks on 8,328 vulnerability records, and end-to-end evidence validation experiments.

\\vspace{{2.5cm}}
\\noindent
\\rule{{7cm}}{{0.4pt}}\\\\
\\textbf{{Ms. Nidhi Kashyap}}\\\\
\\textit{{Dissertation Supervisor}}\\\\
Analyst, Cybersecurity Practice\\\\
Wipro Limited, Pune, India\\\\
Date: November 06, 2026

\\clearpage

% ACKNOWLEDGEMENTS
\\chapter*{{Acknowledgements}}
\\addcontentsline{{toc}}{{chapter}}{{Acknowledgements}}

{escape_prose(ack_prose)}

\\vspace{{1.5cm}}
\\noindent
\\textbf{{Daipayan Ghosal}}\\\\
BITS ID: 2022wa86002\\\\
Pune, India

\\clearpage

% ABSTRACT
\\chapter*{{Abstract}}
\\addcontentsline{{toc}}{{chapter}}{{Abstract}}

{escape_prose(abs_prose)}

\\clearpage

% TOC, LOF, LOT
\\tableofcontents
\\clearpage
\\listoffigures
\\clearpage
\\listoftables
\\clearpage

% LIST OF ABBREVIATIONS
{abbr_table_tex_str}
\\clearpage

% CORE BODY (ARABIC PAGE NUMBERING)
\\pagenumbering{{arabic}}
\\setcounter{{page}}{{1}}

{chapters_tex}

\\clearpage

% REFERENCES
{refs_tex_str}

\\clearpage

% APPENDICES
{appendices_tex_str}

\\clearpage

% PUBLICATIONS
{pubs_tex_str}

\\clearpage

% CHECKLIST
{checklist_tex_str}

\\end{{document}}
"""

print(f"Writing LaTeX source to {TEX_PATH}...")
with open(TEX_PATH, 'w', encoding='utf-8') as f:
    f.write(full_tex)

print(f"File written successfully ({len(full_tex)} characters).")

# Run pdflatex 3 times in DOC_DIR
print("Running pdflatex (Pass 1)...")
res1 = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'DISSERTATION_FINAL_THESIS.tex'],
                      cwd=DOC_DIR, capture_output=True, text=True)
print("Pass 1 return code:", res1.returncode)

if res1.returncode != 0:
    print("Pass 1 errors detected:")
    for line in res1.stdout.splitlines()[-40:]:
        print(line)
else:
    print("Pass 1 completed successfully.")
    print("Running pdflatex (Pass 2 for cross-references)...")
    res2 = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'DISSERTATION_FINAL_THESIS.tex'],
                          cwd=DOC_DIR, capture_output=True, text=True)
    print("Pass 2 return code:", res2.returncode)
    
    print("Running pdflatex (Pass 3 for final TOC/LOF/LOT)...")
    res3 = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'DISSERTATION_FINAL_THESIS.tex'],
                          cwd=DOC_DIR, capture_output=True, text=True)
    print("Pass 3 return code:", res3.returncode)
    
    if os.path.exists(PDF_PATH):
        pdf_size = os.path.getsize(PDF_PATH)
        print(f"Generated PDF successfully: {PDF_PATH} ({pdf_size:,} bytes)")
        shutil.copy2(PDF_PATH, FINAL_NAMED_PDF)
        print(f"Copied to student named PDF: {FINAL_NAMED_PDF}")
    else:
        print("ERROR: PDF was not generated.")
