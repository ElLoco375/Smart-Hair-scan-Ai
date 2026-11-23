from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm

def make_pdf(records, title="Laporan Pemeriksaan Smart HairScan AI"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=16*mm, leftMargin=16*mm,
        topMargin=16*mm, bottomMargin=16*mm
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"],
        alignment=TA_CENTER, textColor=colors.HexColor("#17324D")
    ))
    story = [
        Paragraph(title, styles["ReportTitle"]),
        Spacer(1, 6*mm),
        Paragraph(
            "Dokumen sulit. Keputusan saringan AI perlu disahkan oleh guru "
            "yang diberi kuasa sebelum sebarang tindakan diambil.",
            styles["BodyText"]
        ),
        Spacer(1, 5*mm)
    ]

    data = [[
        "Tarikh", "ID", "Nama", "Kelas",
        "Rambut panjang", "Rambut berwarna", "Pemeriksa"
    ]]
    for r in records:
        data.append([
            str(r["inspected_at"]), str(r["student_id"]),
            str(r["student_name"]), str(r["student_class"]),
            str(r["long_hair"]), str(r["colored_hair"]),
            str(r["reviewer"] or "-")
        ])

    table = Table(data, repeatRows=1, colWidths=[
        25*mm, 13*mm, 32*mm, 18*mm, 27*mm, 27*mm, 25*mm
    ])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324D")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("LEADING", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#B7C3CE")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#F1F5F8")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer
