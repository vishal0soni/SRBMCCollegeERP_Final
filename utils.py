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
from reportlab.pdfgen import canvas

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
        'students': ['Administrator', 'Manager', 'Admission Officer'],
        'courses': ['Administrator', 'Manager', 'Admission Officer'],
        'fees': ['Administrator', 'Manager', 'Accountant'],
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
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=TA_CENTER)

        content = []

        # Determine college name based on course
        student = invoice.student
        college_name = "SHRI RAGHUNATH BISHNOI MEMORIAL COLLEGE"
        if student and student.current_course and ('Bachelor of Pharmacy' in student.current_course or 'B.Pharm' in student.current_course or 'Diploma of Pharmacy' in student.current_course or 'D Pharma' in student.current_course or 'D.Pharm' in student.current_course or 'DIPLOMA OF PHARMACY' in student.current_course.upper()):
            college_name = "SUNDHA MATA INSTITUTE FOR HIGHER STUDIES"

        # Header
        content.append(Paragraph(college_name, title_style))
        content.append(Paragraph("Raniwara, Jalore, Rajasthan", styles['Normal']))
        content.append(Paragraph("FEE RECEIPT", getSampleStyleSheet()['Heading2']))
        content.append(Spacer(1, 20))

        # Invoice details
        invoice_data = [
            ['Invoice Number:', invoice.invoice_number],
            ['Date:', invoice.date_time.strftime('%d/%m/%Y')],
            ['Student ID:', invoice.student.student_unique_id],
            ['Student Name:', f"{invoice.student.first_name} {invoice.student.last_name}"],
            ['Course:', invoice.student.current_course or 'N/A'],
            ['Amount Paid:', f"₹ {invoice.invoice_amount:.2f}"]
        ]

        invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        content.append(invoice_table)
        content.append(Spacer(1, 30))

        # Footer
        content.append(Paragraph("Thank you for your payment!", styles['Normal']))
        content.append(Paragraph("This is a computer-generated receipt.", styles['Normal']))

        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

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
    """Generate a PDF report for student details"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from datetime import datetime

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        # Build content
        story = []

        # Title
        title = Paragraph("SRBMC College - Student Details Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # Personal Information
        story.append(Paragraph("<b>Personal Information</b>", styles['Heading2']))
        personal_data = [
            ['Student ID:', student.student_unique_id or 'N/A'],
            ['Name:', f"{student.first_name} {student.last_name}"],
            ['Father\'s Name:', student.father_name or 'N/A'],
            ['Mother\'s Name:', student.mother_name or 'N/A'],
            ['Gender:', student.gender or 'N/A'],
            ['Category:', student.category or 'N/A'],
            ['Email:', student.email or 'N/A'],
            ['Phone:', student.phone or 'N/A'],
        ]

        personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
        personal_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(personal_table)
        story.append(Spacer(1, 20))

        # Academic Information
        story.append(Paragraph("<b>Academic Information</b>", styles['Heading2']))
        academic_data = [
            ['Current Course:', student.current_course or 'N/A'],
            ['Subject 1:', student.subject_1_name or 'N/A'],
            ['Subject 2:', student.subject_2_name or 'N/A'],
            ['Subject 3:', student.subject_3_name or 'N/A'],
            ['Percentage:', f"{student.percentage}%" if student.percentage else 'N/A'],
            ['School Name:', student.school_name or 'N/A'],
            ['Admission Date:', student.admission_date.strftime('%d/%m/%Y') if student.admission_date else 'N/A'],
            ['Status:', student.dropout_status or 'N/A'],
        ]

        academic_table = Table(academic_data, colWidths=[2*inch, 4*inch])
        academic_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(academic_table)
        story.append(Spacer(1, 20))

        # Address Information
        story.append(Paragraph("<b>Address Information</b>", styles['Heading2']))
        address_data = [
            ['Street:', student.street or 'N/A'],
            ['Area/Village:', student.area_village or 'N/A'],
            ['City/Tehsil:', student.city_tehsil or 'N/A'],
            ['State:', student.state or 'N/A'],
        ]

        address_table = Table(address_data, colWidths=[2*inch, 4*inch])
        address_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(address_table)
        story.append(Spacer(1, 20))

        # Other Information
        story.append(Paragraph("<b>Other Information</b>", styles['Heading2']))
        other_data = [
            ['Aadhaar Number:', student.aadhaar_card_number or 'N/A'],
            ['Government Scholarship:', student.scholarship_status or 'N/A'],
            ['Meera Scholarship:', student.rebate_meera_scholarship_status or 'N/A'],
        ]

        other_table = Table(other_data, colWidths=[2*inch, 4*inch])
        other_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(other_table)
        story.append(Spacer(1, 30))

        # Footer
        footer_text = f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        story.append(Paragraph(footer_text, styles['Normal']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except ImportError:
        # Fallback to simple text-based PDF if reportlab is not available
        buffer = io.BytesIO()
        content = f"""SRBMC College - Student Details Report

Personal Information:
Student ID: {student.student_unique_id or 'N/A'}
Name: {student.first_name} {student.last_name}
Father's Name: {student.father_name or 'N/A'}
Mother's Name: {student.mother_name or 'N/A'}
Gender: {student.gender or 'N/A'}
Category: {student.category or 'N/A'}
Email: {student.email or 'N/A'}
Phone: {student.phone or 'N/A'}

Academic Information:
Current Course: {student.current_course or 'N/A'}
Subject 1: {student.subject_1_name or 'N/A'}
Subject 2: {student.subject_2_name or 'N/A'}
Subject 3: {student.subject_3_name or 'N/A'}
Percentage: {student.percentage}% if student.percentage else 'N/A'
School Name: {student.school_name or 'N/A'}
Admission Date: {student.admission_date.strftime('%d/%m/%Y') if student.admission_date else 'N/A'}
Status: {student.dropout_status or 'N/A'}

Address Information:
Street: {student.street or 'N/A'}
Area/Village: {student.area_village or 'N/A'}
City/Tehsil: {student.city_tehsil or 'N/A'}
State: {student.state or 'N/A'}

Other Information:
Aadhaar Number: {student.aadhaar_card_number or 'N/A'}
APAAR ID: {student.apaar_id or 'N/A'}
Government Scholarship: {student.scholarship_status or 'N/A'}
Meera Scholarship: {student.rebate_meera_scholarship_status or 'N/A'}

Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        buffer.write(content.encode('utf-8'))
        buffer.seek(0)
        return buffer.getvalue()

def generate_pdf_fee_statement(student, fee_record, invoices):
    """Generate comprehensive PDF fee statement with payment history"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        import io

        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=TA_CENTER)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, alignment=TA_LEFT)
        normal_style = styles['Normal']

        # Build PDF content
        content = []

        # College header
        content.append(Paragraph("SHRI RAGHUNATH BISHNOI MEMORIAL COLLEGE", title_style))
        content.append(Paragraph("Raniwara, Jalore, Rajasthan", styles['Normal']))
        content.append(Paragraph("FEE STATEMENT", heading_style))
        content.append(Spacer(1, 20))

        if not fee_record:
            content.append(Paragraph("No fee record found for this student.", normal_style))
            doc.build(content)
            buffer.seek(0)
            return buffer.getvalue()

        # Student details
        student_data = [
            ['Student ID:', student.student_unique_id],
            ['Student Name:', f"{student.first_name} {student.last_name}"],
            ['Father Name:', student.father_name or 'N/A'],
            ['Course:', student.current_course or 'N/A'],
            ['Phone:', student.phone or 'N/A'],
            ['Email:', student.email or 'N/A'],
        ]

        student_table = Table(student_data, colWidths=[2*inch, 4*inch])
        student_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        content.append(student_table)
        content.append(Spacer(1, 20))

        # Fee summary
        total_paid = (
            (fee_record.installment_1 or 0) +
            (fee_record.installment_2 or 0) +
            (fee_record.installment_3 or 0) +
            (fee_record.installment_4 or 0) +
            (fee_record.installment_5 or 0) +
            (fee_record.installment_6 or 0)
        )

        balance_due = (fee_record.total_fee or 0) - total_paid

        fee_summary_data = [
            ['Total Fee:', f"₹ {fee_record.total_fee or 0:.2f}"],
            ['Total Paid:', f"₹ {total_paid:.2f}"],
            ['Balance Due:', f"₹ {balance_due:.2f}"],
        ]

        fee_summary_table = Table(fee_summary_data, colWidths=[2*inch, 4*inch])
        fee_summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        content.append(Paragraph("Fee Summary", heading_style))
        content.append(fee_summary_table)
        content.append(Spacer(1, 20))

        # Payment history
        if invoices:
            content.append(Paragraph("Payment History", heading_style))

            payment_data = [['Date', 'Invoice Number', 'Amount', 'Installment']]
            for invoice in invoices:
                payment_data.append([
                    invoice.date_time.strftime('%d/%m/%Y'),
                    invoice.invoice_number,
                    f"₹ {invoice.invoice_amount:.2f}",
                    f"Installment {invoice.installment_number or 'N/A'}"
                ])

            payment_table = Table(payment_data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 1.3*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            content.append(payment_table)

        content.append(Spacer(1, 30))

        # Footer
        content.append(Paragraph("Generated on: " + datetime.now().strftime('%d/%m/%Y %H:%M'), normal_style))

        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        print(f"Error generating fee statement PDF: {e}")
        return None

def generate_pdf_fee_statement_print(student, fee_record):
    """Generate PDF fee statement for printing"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        import io

        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=TA_CENTER)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, alignment=TA_LEFT)
        normal_style = styles['Normal']

        # Build PDF content
        content = []

        # Determine college name based on course
        college_name = "SHRI RAGHUNATH BISHNOI MEMORIAL COLLEGE"
        college_location = "Raniwara, Jalore, Rajasthan"

        if student.current_course and ('Bachelor of Pharmacy' in student.current_course or 'B.Pharm' in student.current_course or 'Diploma of Pharmacy' in student.current_course or 'D Pharma' in student.current_course or 'D.Pharm' in student.current_course or 'DIPLOMA OF PHARMACY' in student.current_course.upper()):
            college_name = "SUNDHA MATA INSTITUTE FOR HIGHER STUDIES"

        # College header
        content.append(Paragraph(college_name, title_style))
        content.append(Paragraph(college_location, styles['Normal']))
        content.append(Paragraph("FEE STATEMENT", heading_style))
        content.append(Spacer(1, 20))

        if not fee_record:
            content.append(Paragraph("No fee record found for this student.", normal_style))
            doc.build(content)
            buffer.seek(0)
            return buffer.getvalue()

        # Student details
        student_data = [
            ['Student ID:', student.student_unique_id],
            ['Student Name:', f"{student.first_name} {student.last_name}"],
            ['Father Name:', student.father_name or 'N/A'],
            ['Course:', student.current_course or 'N/A'],
            ['Phone:', student.phone or 'N/A'],
        ]

        student_table = Table(student_data, colWidths=[2*inch, 4*inch])
        student_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        content.append(student_table)
        content.append(Spacer(1, 20))

        # Fee summary
        total_paid = (
            (fee_record.installment_1 or 0) +
            (fee_record.installment_2 or 0) +
            (fee_record.installment_3 or 0) +
            (fee_record.installment_4 or 0) +
            (fee_record.installment_5 or 0) +
            (fee_record.installment_6 or 0)
        )

        balance_due = (fee_record.total_fee or 0) - total_paid

        fee_summary_data = [
            ['Total Fee:', f"₹ {fee_record.total_fee or 0:.2f}"],
            ['Total Paid:', f"₹ {total_paid:.2f}"],
            ['Balance Due:', f"₹ {balance_due:.2f}"],
        ]

        fee_summary_table = Table(fee_summary_data, colWidths=[2*inch, 4*inch])
        fee_summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        content.append(Paragraph("Fee Summary", heading_style))
        content.append(fee_summary_table)
        content.append(Spacer(1, 30))

        # Footer
        content.append(Paragraph("Generated on: " + datetime.now().strftime('%d/%m/%Y %H:%M'), normal_style))

        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        print(f"Error generating fee statement PDF: {e}")
        return None