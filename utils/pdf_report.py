"""
PDF Report Generator using ReportLab.
"""
import io
import datetime
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, Image, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


NAVY = colors.HexColor('#0A0E1A')
ACCENT = colors.HexColor('#00D4FF')
PANEL = colors.HexColor('#0F1629')
WHITE = colors.white
LIGHT = colors.HexColor('#C8D6F0')


def generate_pdf_report(params: dict, kpis: dict, figures: list,
                          output_path: str = None) -> bytes:
    """
    Generate a professional PDF report.
    
    params: dict of simulation parameters
    kpis: dict of key performance indicators
    figures: list of (title, matplotlib_figure) tuples
    output_path: if provided, save to file; always returns bytes
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, textColor=ACCENT,
        alignment=TA_CENTER, fontName='Helvetica-Bold',
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=14, textColor=ACCENT,
        fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=12
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=11, textColor=LIGHT,
        fontName='Helvetica-Bold', spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#8090B0'),
        fontName='Helvetica', spaceAfter=4
    )
    caption_style = ParagraphStyle(
        'Caption', parent=styles['Normal'],
        fontSize=8, textColor=LIGHT,
        alignment=TA_CENTER, fontName='Helvetica-Oblique', spaceAfter=6
    )

    story = []

    # ---- Cover ----
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Mobile Communication System Simulator", title_style))
    story.append(Paragraph("Simulation Report", ParagraphStyle(
        'Sub', parent=styles['Normal'], fontSize=13, textColor=LIGHT,
        alignment=TA_CENTER, fontName='Helvetica', spaceAfter=4
    )))
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Generated: {ts}", ParagraphStyle(
        'Date', parent=styles['Normal'], fontSize=9, textColor=colors.grey,
        alignment=TA_CENTER
    )))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=15))
    story.append(Spacer(1, 0.5*cm))

    # ---- KPI Summary ----
    story.append(Paragraph("Key Performance Indicators", h1_style))
    kpi_data = [["Metric", "Value", "Unit"]]
    kpi_items = [
        ("Average SINR", f"{kpis.get('avg_sinr', 0):.2f}", "dB"),
        ("Total Handovers", f"{kpis.get('handoff_count', 0)}", "events"),
        ("Active Users", f"{kpis.get('active_users', 0)}", "UEs"),
        ("Cell Load", f"{kpis.get('cell_load', 0)*100:.1f}", "%"),
        ("Avg Throughput", f"{kpis.get('avg_throughput', 0):.2f}", "Mbps"),
    ]
    kpi_data.extend(kpi_items)
    kpi_table = Table(kpi_data, colWidths=[8*cm, 5*cm, 4*cm])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PANEL),
        ('TEXTCOLOR', (0, 0), (-1, 0), ACCENT),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TEXTCOLOR', (0, 1), (-1, -1), LIGHT),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#0D1020'), colors.HexColor('#12182E')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#1A2040')),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.5*cm))

    # ---- Simulation Parameters ----
    story.append(Paragraph("Simulation Parameters", h1_style))
    param_data = [["Parameter", "Value"]]
    for k, v in params.items():
        param_data.append([str(k), str(v)])
    param_table = Table(param_data, colWidths=[9*cm, 8*cm])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PANEL),
        ('TEXTCOLOR', (0, 0), (-1, 0), ACCENT),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TEXTCOLOR', (0, 1), (-1, -1), LIGHT),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#0D1020'), colors.HexColor('#12182E')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#1A2040')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(param_table)

    # ---- Figures ----
    if figures:
        story.append(PageBreak())
        story.append(Paragraph("Simulation Results", h1_style))
        for fig_title, mpl_fig in figures:
            story.append(Paragraph(fig_title, h2_style))
            img_buf = io.BytesIO()
            mpl_fig.savefig(img_buf, format='png', dpi=120, bbox_inches='tight',
                             facecolor=mpl_fig.get_facecolor())
            img_buf.seek(0)
            img = Image(img_buf, width=17*cm, height=9*cm)
            story.append(img)
            story.append(Paragraph(fig_title, caption_style))
            story.append(Spacer(1, 0.3*cm))

    # ---- Footer note ----
    story.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceBefore=10))
    story.append(Paragraph(
        "Generated by Mobile Communication System Simulator | Graduation Project",
        ParagraphStyle('Footer', parent=styles['Normal'],
                        fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    pdf_bytes = buf.getvalue()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

    return pdf_bytes
