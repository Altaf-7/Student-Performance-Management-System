"""Generates a real, professional-looking marksheet PDF with ReportLab.
No fake/placeholder content - every field is pulled from the actual
calculated semester GPA data passed in."""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def build_marksheet_pdf(student, semester, gpa_data) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=4)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, textColor=colors.grey)

    elements = [
        Paragraph("Student Performance Management System", title_style),
        Paragraph("Official Semester Marksheet", sub_style),
        Spacer(1, 10),
    ]

    student_name = student.get_full_name() or student.username
    student_id = getattr(getattr(student, "student_profile", None), "student_id", student.username)
    department = getattr(getattr(student, "student_profile", None), "department", None)

    info_table = Table([
        ["Student Name:", student_name, "Student ID:", student_id],
        ["Department:", str(department) if department else "-", "Semester:", f"{semester.name} ({semester.academic_year})"],
    ], colWidths=[80, 160, 80, 160])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    header = ["Course Code", "Course Name", "Credits", "Marks", "Percentage", "Grade", "Grade Point"]
    rows = [header]
    for c in gpa_data["courses"]:
        course = c["course"]
        rows.append([
            course.course_code,
            course.course_name,
            str(c["credits"]),
            f"{c['total_obtained']}/{c['total_max']}",
            f"{c['percentage']}%",
            c["grade"],
            str(c["grade_point"]),
        ])

    table = Table(rows, colWidths=[65, 140, 45, 65, 65, 45, 65])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))

    summary = Table([
        ["Semester GPA:", str(gpa_data["gpa"]), "Total Credits:", str(gpa_data["total_credits"])],
    ], colWidths=[90, 100, 100, 100])
    summary.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(summary)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "This is a system-generated marksheet from the Student Performance Management System.",
        sub_style,
    ))

    doc.build(elements)
    return buffer.getvalue()
