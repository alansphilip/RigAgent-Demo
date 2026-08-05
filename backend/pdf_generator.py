"""
PDF Checklist Generator using ReportLab.
Generates professional industrial-style PDF checklists.
"""
import os
import uuid
from datetime import datetime
from typing import List

PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "./generated_pdfs")


def generate_checklist_pdf(
    checklist_name: str,
    equipment: str,
    procedure: str,
    items: List[dict],
    inspector: str = "N/A",
    work_pack_code: str = "",
) -> str:
    """
    Generate a professional PDF checklist.
    Returns the filename of the generated PDF.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    
    # Generate unique filename
    safe_name = checklist_name.replace(" ", "_").replace("/", "-")[:50]
    filename = f"{safe_name}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(PDF_OUTPUT_DIR, filename)
    
    # Colors
    DARK_BG = colors.HexColor("#1a1a1a")
    AMBER = colors.HexColor("#f59e0b")
    DARK_GRAY = colors.HexColor("#2a2a2a")
    MID_GRAY = colors.HexColor("#6b7280")
    WHITE = colors.white
    BLACK = colors.black
    LIGHT_GRAY = colors.HexColor("#f3f4f6")
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=BLACK,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        fontSize=11,
        textColor=MID_GRAY,
        fontName="Helvetica",
        spaceAfter=4,
    )
    header_label_style = ParagraphStyle(
        "HeaderLabel",
        fontSize=8,
        textColor=MID_GRAY,
        fontName="Helvetica",
        spaceAfter=2,
    )
    header_value_style = ParagraphStyle(
        "HeaderValue",
        fontSize=10,
        textColor=BLACK,
        fontName="Helvetica-Bold",
        spaceAfter=8,
    )
    section_style = ParagraphStyle(
        "Section",
        fontSize=10,
        textColor=BLACK,
        fontName="Helvetica-Bold",
        spaceAfter=4,
        spaceBefore=12,
    )
    item_style = ParagraphStyle(
        "Item",
        fontSize=9,
        textColor=BLACK,
        fontName="Helvetica",
        leftIndent=0,
    )
    footer_style = ParagraphStyle(
        "Footer",
        fontSize=8,
        textColor=MID_GRAY,
        fontName="Helvetica",
        alignment=TA_CENTER,
    )
    
    story = []
    
    # --- HEADER BANNER ---
    header_data = [
        [
            Paragraph("<b>RIG QUERY AGENT</b>", ParagraphStyle("logo", fontSize=14, textColor=WHITE, fontName="Helvetica-Bold")),
            Paragraph("MAINTENANCE CHECKLIST", ParagraphStyle("tag", fontSize=9, textColor=AMBER, fontName="Helvetica-Bold", alignment=TA_RIGHT)),
        ]
    ]
    header_table = Table(header_data, colWidths=[12*cm, 5*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("PADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))
    
    # --- TITLE ---
    story.append(Paragraph(checklist_name, title_style))
    story.append(Paragraph(f"Equipment: {equipment} | Procedure: {procedure}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=AMBER, spaceAfter=12))
    
    # --- META INFO TABLE ---
    now = datetime.now()
    meta_data = [
        ["WORK PACK", "INSPECTOR", "DATE", "STATUS"],
        [
            work_pack_code or "N/A",
            inspector,
            now.strftime("%Y-%m-%d"),
            "IN PROGRESS",
        ]
    ]
    meta_table = Table(meta_data, colWidths=[4.25*cm, 4.25*cm, 4.25*cm, 4.25*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_GRAY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GRAY),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, 1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))
    
    # --- CHECKLIST ITEMS ---
    story.append(Paragraph("INSPECTION CHECKLIST", section_style))
    
    required_items = [i for i in items if i.get("is_required", True)]
    optional_items = [i for i in items if not i.get("is_required", True)]
    
    def make_items_table(items_list):
        if not items_list:
            return None
        rows = [["#", "☐", "INSPECTION ITEM", "RESULT", "INITIALS"]]
        for item in items_list:
            rows.append([
                str(item.get("step_number", "")),
                "",
                Paragraph(item.get("description", ""), item_style),
                "",
                "",
            ])
        t = Table(rows, colWidths=[1*cm, 1*cm, 9.5*cm, 3*cm, 2.5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTNAME", (1, 1), (1, -1), "Helvetica"),
            ("FONTSIZE", (1, 1), (1, -1), 14),  # Checkbox size
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (1, -1), "CENTER"),
            ("ALIGN", (3, 0), (-1, -1), "CENTER"),
        ]))
        return t
    
    req_table = make_items_table(required_items)
    if req_table:
        story.append(req_table)
    
    if optional_items:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("OPTIONAL CHECKS", section_style))
        opt_table = make_items_table(optional_items)
        if opt_table:
            story.append(opt_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # --- SIGN OFF SECTION ---
    story.append(Paragraph("SIGN-OFF", section_style))
    signoff_data = [
        ["INSPECTOR SIGNATURE", "DATE", "SUPERVISOR REVIEW", "DATE"],
        ["", "", "", ""],
        ["", "", "", ""],
    ]
    signoff_table = Table(signoff_data, colWidths=[5.5*cm, 2*cm, 5.5*cm, 2*cm])
    signoff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_GRAY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("PADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(signoff_table)
    story.append(Spacer(1, 0.8*cm))
    
    # --- FOOTER ---
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=6))
    story.append(Paragraph(
        f"RIG Query Agent | Maintenance Checklist | Generated: {now.strftime('%Y-%m-%d %H:%M UTC')} | "
        f"Document ID: {uuid.uuid4().hex[:12].upper()} | CONFIDENTIAL",
        footer_style
    ))
    
    doc.build(story)
    return filename
