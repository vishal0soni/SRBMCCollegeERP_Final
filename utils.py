import os
import secrets
from datetime import datetime
from flask import current_app
from flask_mail import Mail, Message
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

from app import db
from models import Student, UserRole

# Initialize Flask-Mail
mail = Mail()

def generate_student_id(course_short, year):
    """Generate unique student ID like BA-25-001"""
    year_short = str(year)[-2:]  # Last 2 digits of year

    # Find existing students for this course and year pattern
    pattern = f"{course_short}-{year_short}-%"
    existing_students = Student.query.filter(Student.student_unique_id.like(pattern)).all()
    
    # Extract the highest number from existing IDs
    max_number = 0
    for student in existing_students:
        try:
            # Extract number from ID like "BA-25-001" -> 1
            id_parts = student.student_unique_id.split('-')
            if len(id_parts) >= 3:
                number = int(id_parts[2])
                max_number = max(max_number, number)
        except (ValueError, IndexError):
            continue
    
    # Generate next number
    next_number = max_number + 1
    return f"{course_short}-{year_short}-{next_number:03d}"

def generate_invoice_number():
    """Generate unique invoice number"""
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")

    # Count invoices for today
    pattern = f"INV{date_str}%"
    from models import Invoice
    count = Invoice.query.filter(Invoice.invoice_number.like(pattern)).count()

    next_number = count + 1
    return f"INV{date_str}{next_number:04d}"

def calculate_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B+'
    elif percentage >= 60:
        return 'B'
    elif percentage >= 50:
        return 'C+'
    elif percentage >= 40:
        return 'C'
    else:
        return 'F'

def can_edit_module(user, module):
    """Check if user can edit a specific module"""
    if not user or not user.is_authenticated:
        return False

    role = user.role
    if not role:
        return False

    # Administrator has access to everything
    if role.role_name == 'Administrator':
        return True

    # Module-specific permissions
    module_permissions = {
        'admin': ['Administrator'],
        'students': ['Administrator', 'Admission Officer'],
        'courses': ['Administrator', 'Admission Officer'],
        'fees': ['Administrator', 'Accountant'],
        'exams': ['Administrator', 'Exam Controller']
    }

    allowed_roles = module_permissions.get(module, [])
    return role.role_name in allowed_roles and role.access_type == 'Edit'

def send_email(to_email, subject, body):
    """Send email notification"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False

def generate_pdf_invoice(invoice):
    """Generate PDF invoice"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        alignment=TA_CENTER
    )

    story = []

    # College Header
    story.append(Paragraph("Shri Raghunath Bishnoi Memorial College (SRBMC), Raniwara", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("FEE RECEIPT", header_style))
    story.append(Spacer(1, 20))

    # Invoice details
    invoice_data = [
        ['Invoice Number:', invoice.invoice_number],
        ['Date:', invoice.date_time.strftime('%d/%m/%Y')],
        ['Student ID:', invoice.student.student_unique_id],
        ['Student Name:', f"{invoice.student.first_name} {invoice.student.last_name}"],
        ['Course:', invoice.student.current_course],
        ['Amount Paid:', f"₹{invoice.invoice_amount}"],
        ['Payment Mode:', 'Cash'],  # You can add this field to the model
    ]

    table = Table(invoice_data, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(table)
    story.append(Spacer(1, 30))

    # Footer
    story.append(Paragraph("Thank you for your payment!", styles['Normal']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("This is a computer-generated receipt.", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_pdf_report_card(exam):
    """Generate PDF report card"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        alignment=TA_CENTER
    )

    story = []

    # College Header
    story.append(Paragraph("Shri Raghunath Bishnoi Memorial College (SRBMC), Raniwara", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("REPORT CARD", header_style))
    story.append(Spacer(1, 20))

    # Student details
    student_data = [
        ['Student ID:', exam.student.student_unique_id],
        ['Student Name:', f"{exam.student.first_name} {exam.student.last_name}"],
        ['Course:', exam.student.current_course],
        ['Exam:', exam.exam_name],
        ['Semester:', exam.semester],
        ['Exam Date:', exam.exam_date.strftime('%d/%m/%Y') if exam.exam_date else 'N/A'],
    ]

    table = Table(student_data, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Marks table
    marks_data = [['Subject', 'Max Marks', 'Obtained Marks', 'Grade']]

    subjects = [
        (exam.subject1_name, exam.subject1_max_marks, exam.subject1_obtained_marks),
        (exam.subject2_name, exam.subject2_max_marks, exam.subject2_obtained_marks),
        (exam.subject3_name, exam.subject3_max_marks, exam.subject3_obtained_marks),
        (exam.subject4_name, exam.subject4_max_marks, exam.subject4_obtained_marks),
        (exam.subject5_name, exam.subject5_max_marks, exam.subject5_obtained_marks),
        (exam.subject6_name, exam.subject6_max_marks, exam.subject6_obtained_marks),
    ]

    for subject_name, max_marks, obtained_marks in subjects:
        if subject_name:
            percentage = (obtained_marks / max_marks * 100) if max_marks > 0 else 0
            grade = calculate_grade(percentage)
            marks_data.append([subject_name, str(max_marks), str(obtained_marks), grade])

    # Add total row
    marks_data.append(['TOTAL', str(exam.total_max_marks), str(exam.total_obtained_marks), exam.grade])

    marks_table = Table(marks_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
    marks_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))

    story.append(marks_table)
    story.append(Spacer(1, 20))

    # Result summary
    result_data = [
        ['Total Marks:', f"{exam.total_obtained_marks}/{exam.total_max_marks}"],
        ['Percentage:', f"{exam.percentage:.2f}%"],
        ['Grade:', exam.grade],
        ['Result:', exam.overall_status],
    ]

    result_table = Table(result_data, colWidths=[2*inch, 2*inch])
    result_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(result_table)
    story.append(Spacer(1, 30))

    # Footer
    story.append(Paragraph("Principal", styles['Normal']))
    story.append(Paragraph("SRBMC, Raniwara", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_pdf_student_report(student):
    # Create PDF for student details report
    buffer = io.BytesIO()

    # Simple text-based PDF content
    content = f"""
    SRBMC College - Student Details Report

    Personal Information:
    Student ID: {student.student_unique_id}
    Name: {student.first_name} {student.last_name}
    Father's Name: {student.father_name}
    Mother's Name: {student.mother_name}
    Gender: {student.gender}
    Category: {student.category}
    Email: {student.email}
    Phone: {student.phone}

    Academic Information:
    Current Course: {student.current_course}
    Subject 1: {student.subject_1_name}
    Subject 2: {student.subject_2_name}
    Subject 3: {student.subject_3_name}
    Percentage: {student.percentage}%

    Address Information:
    Street: {student.street}
    Area/Village: {student.area_village}
    City/Tehsil: {student.city_tehsil}
    State: {student.state}

    Other Information:
    Aadhaar Number: {student.aadhaar_card_number}
    School Name: {student.school_name}
    Scholarship Status: {student.scholarship_status}
    Admission Date: {student.admission_date}
    Status: {student.dropout_status}
    """

    buffer.write(content.encode('utf-8'))
    buffer.seek(0)
    return buffer.getvalue()