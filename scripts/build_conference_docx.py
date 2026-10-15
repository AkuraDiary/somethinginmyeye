"""
Automated IEEE Conference Manuscript Builder for Word (.docx).
Reads le-conference-dyslexia/conference_paper.md and compiles a professionally styled
IEEE Conference document into le-conference-dyslexia/elkinematics-conference.docx.
"""

import os
import re
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor


def set_cell_background(cell, fill_hex):
    """Sets the background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets padding inside table cells."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def compile_conference_manuscript(
    md_path: str = "le-conference-dyslexia/conference_paper.md",
    output_docx_path: str = "le-conference-dyslexia/elkinematics-conference.docx",
):
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"Markdown manuscript not found at {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = docx.Document()

    # Set IEEE Standard Margins (0.75 in top/bottom, 0.63 in left/right)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.63)
        section.right_margin = Inches(0.63)

    # Base Style configuration: Times New Roman, 10pt
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.05
    normal_style.paragraph_format.space_after = Pt(4)

    lines = md_text.split("\n")
    in_abstract = False
    in_table = False
    table_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line or line == "---":
            i += 1
            continue

        # Paper Title
        if line.startswith("# "):
            title_text = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run(title_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(20)
            run.font.bold = True
            i += 1
            continue

        # Author / Affiliation Block
        if line.startswith("**Asthiseta Pratama**"):
            p_author = doc.add_paragraph()
            p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_author.paragraph_format.space_after = Pt(2)
            run_author = p_author.add_run(line.replace("**", ""))
            run_author.font.name = "Times New Roman"
            run_author.font.size = Pt(11)
            run_author.font.bold = True

            # Next 3 lines are affiliation and email
            for _ in range(3):
                i += 1
                if i < len(lines):
                    affil_line = lines[i].strip().replace("*", "")
                    p_affil = doc.add_paragraph()
                    p_affil.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_affil.paragraph_format.space_after = Pt(2)
                    run_affil = p_affil.add_run(affil_line)
                    run_affil.font.name = "Times New Roman"
                    run_affil.font.size = Pt(9.5)
                    run_affil.font.italic = True
            i += 1
            continue

        # Abstract Header & Body
        if line.startswith("### Abstract"):
            i += 1
            abstract_parts = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("*Index Terms*") and lines[i].strip() != "---":
                abstract_parts.append(lines[i].strip())
                i += 1
            abstract_body = " ".join(abstract_parts)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(6)
            run_h = p.add_run("Abstract—")
            run_h.font.name = "Times New Roman"
            run_h.font.size = Pt(9)
            run_h.font.bold = True
            run_h.font.italic = True

            clean_abstract = (
                abstract_body.replace("*Background*—", "Background—")
                .replace("*Objective*—", "Objective—")
                .replace("*Methods*—", "Methods—")
                .replace("*Results*—", "Results—")
                .replace("*Conclusion*—", "Conclusion—")
                .replace("*", "")
                .replace("**", "")
            )
            run_body = p.add_run(clean_abstract)
            run_body.font.name = "Times New Roman"
            run_body.font.size = Pt(9)
            run_body.font.bold = True
            continue


        # Index Terms
        if line.startswith("*Index Terms*—"):
            terms = line.replace("*Index Terms*—", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(12)
            run_h = p.add_run("Index Terms—")
            run_h.font.name = "Times New Roman"
            run_h.font.size = Pt(9)
            run_h.font.bold = True
            run_h.font.italic = True
            run_body = p.add_run(terms)
            run_body.font.name = "Times New Roman"
            run_body.font.size = Pt(9)
            run_body.font.bold = True
            i += 1
            continue

        # Section Heading 1 (e.g. ## I. Introduction)
        if line.startswith("## "):
            sec_title = line[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(sec_title.upper())
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            run.font.bold = True
            i += 1
            continue

        # Subheading 2 (e.g. ### A. DSM-5 Diagnostic Criteria)
        if line.startswith("### "):
            subsec_title = line[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(subsec_title)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.italic = True
            i += 1
            continue

        # Table processing
        if line.startswith("|") and "|" in line[1:]:
            table_lines.append(line)
            i += 1
            # Check if table continues
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            # Render Table
            rows_data = []
            for t_line in table_lines:
                if re.match(r"^\|[\s\-:|]+\|$", t_line):
                    continue
                cells = [c.strip() for c in t_line.split("|")[1:-1]]
                rows_data.append(cells)

            if rows_data:
                table = doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                for r_idx, row in enumerate(rows_data):
                    for c_idx, cell_value in enumerate(row):
                        cell = table.cell(r_idx, c_idx)
                        clean_val = cell_value.replace("**", "").replace("*", "")
                        cell.text = clean_val
                        p = cell.paragraphs[0]
                        p.paragraph_format.space_after = Pt(2)
                        p.paragraph_format.space_before = Pt(2)
                        run = p.runs[0] if p.runs else p.add_run(clean_val)
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(8.5)
                        if r_idx == 0:
                            run.font.bold = True
                            set_cell_background(cell, "EEEEEE")
                        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)

                doc.add_paragraph().paragraph_format.space_after = Pt(4)

            table_lines = []
            continue

        # Table caption
        if line.startswith("**TABLE"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(line.replace("**", ""))
            run.font.name = "Times New Roman"
            run.font.size = Pt(8.5)
            run.font.bold = True
            i += 1
            continue

        # Bullet list item
        if line.startswith("- ") or line.startswith("* "):
            bullet_text = line[2:].strip().replace("**", "")
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(bullet_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            i += 1
            continue

        # Standard Body Paragraph
        clean_line = line.replace("**", "")
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(clean_line)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        i += 1

    doc.save(output_docx_path)
    print(f"Successfully compiled IEEE conference paper to: {output_docx_path}")


if __name__ == "__main__":
    compile_conference_manuscript()
