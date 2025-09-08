import csv
import json
import io
import pandas as pd
from flask import make_response, request, flash
from werkzeug.utils import secure_filename
from models import Student, Course, CourseDetails, Subject, UserProfile, CollegeFees, Exam, Invoice
from app import db
from datetime import datetime, date
import uuid

def export_to_csv(data, headers, filename):
    """Export data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow(headers)

    # Write data
    for row in data:
        writer.writerow(row)

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'text/csv'

    return response

def export_to_excel(data, headers, filename):
    """Export data to Excel format"""
    df = pd.DataFrame(data, columns=headers)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return response

def export_to_json(data, headers, filename):
    """Export data to JSON format"""
    json_data = []
    for row in data:
        row_dict = {}
        for i, header in enumerate(headers):
            if i < len(row):
                row_dict[header] = row[i]
            else:
                row_dict[header] = None
        json_data.append(row_dict)

    json_string = json.dumps(json_data, indent=2, default=str)

    response = make_response(json_string)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'application/json'

    return response

def get_students_export_data():
    """Get students data for export"""
    students = Student.query.all()
    headers = [
        'Student ID', 'External ID', 'First Name', 'Last Name', 'Father Name', 'Mother Name',
        'Gender', 'Category', 'Email', 'Current Course', 'Subject 1', 'Subject 2', 'Subject 3',
        'Percentage', 'Street', 'Area/Village', 'City/Tehsil', 'State', 'Phone', 
        'Aadhaar Number', 'APAAR ID', 'School Name', 'Scholarship Status', 
        'Meera Rebate Status', 'Student Status', 'Admission Date'
    ]

    data = []
    for student in students:
        data.append([
            student.student_unique_id,
            student.external_id or '',
            student.first_name,
            student.last_name,
            student.father_name or '',
            student.mother_name or '',
            student.gender,
            student.category or '',
            student.email or '',
            student.current_course or '',
            student.subject_1_name or '',
            student.subject_2_name or '',
            student.subject_3_name or '',
            float(student.percentage) if student.percentage else '',
            student.street or '',
            student.area_village or '',
            student.city_tehsil or '',
            student.state or '',
            student.phone or '',
            student.aadhaar_card_number or '',
            student.apaar_id or '',
            student.school_name or '',
            student.scholarship_status or '',
            student.rebate_meera_scholarship_status or '',
            student.student_status or 'Active',
            student.admission_date.strftime('%Y-%m-%d') if student.admission_date else ''
        ])

    return data, headers

def get_courses_export_data():
    """Get courses data for export"""
    courses = Course.query.all()
    headers = ['Course ID', 'Short Name', 'Full Name', 'Category', 'Duration (Years)']

    data = []
    for course in courses:
        data.append([
            course.course_id,
            course.course_short_name,
            course.course_full_name,
            course.course_category or '',
            course.duration or ''
        ])

    return data, headers

def get_course_details_export_data():
    """Get course details data for export"""
    course_details = CourseDetails.query.all()
    headers = [
        'ID', 'Course Full Name', 'Course Short Name', 'Year/Semester', 
        'Course Tuition Fee', 'Course Type', 'Misc Fee 1', 'Misc Fee 2', 
        'Misc Fee 3', 'Misc Fee 4', 'Misc Fee 5', 'Misc Fee 6', 'Total Course Fees'
    ]

    data = []
    for detail in course_details:
        data.append([
            detail.id,
            detail.course_full_name,
            detail.course_short_name,
            detail.year_semester,
            float(detail.course_tuition_fee) if detail.course_tuition_fee else 0,
            detail.course_type or '',
            float(detail.misc_course_fees_1) if detail.misc_course_fees_1 else 0,
            float(detail.misc_course_fees_2) if detail.misc_course_fees_2 else 0,
            float(detail.misc_course_fees_3) if detail.misc_course_fees_3 else 0,
            float(detail.misc_course_fees_4) if detail.misc_course_fees_4 else 0,
            float(detail.misc_course_fees_5) if detail.misc_course_fees_5 else 0,
            float(detail.misc_course_fees_6) if detail.misc_course_fees_6 else 0,
            float(detail.total_course_fees) if detail.total_course_fees else 0
        ])

    return data, headers

def get_fees_export_data():
    """Get fees data for export"""
    fees = db.session.query(CollegeFees, Student).join(Student).all()
    headers = [
        'Student ID', 'Student Name', 'Course', 'Total Fee', 'Paid Amount', 'Due Amount',
        'Installment 1', 'Installment 2', 'Installment 3', 'Installment 4', 
        'Installment 5', 'Installment 6', 'Payment Status'
    ]

    data = []
    for fee, student in fees:
        # Use database-calculated values directly
        paid_amount = float(fee.total_fees_paid or 0)
        total_fee = float(fee.total_fee or 0)
        due_amount = total_fee - paid_amount

        payment_status = 'Paid' if due_amount <= 0 else ('Partial' if paid_amount > 0 else 'Pending')

        data.append([
            student.student_unique_id,
            f"{student.first_name} {student.last_name}",
            student.current_course or '',
            total_fee,
            paid_amount,
            due_amount,
            float(fee.installment_1 or 0),
            float(fee.installment_2 or 0),
            float(fee.installment_3 or 0),
            float(fee.installment_4 or 0),
            float(fee.installment_5 or 0),
            float(fee.installment_6 or 0),
            payment_status
        ])

    return data, headers

def get_invoices_export_data():
    """Get invoices data for export"""
    fees = db.session.query(CollegeFees, Student).join(Student).all()
    headers = [
        'Invoice Number', 'Student ID', 'Student Name', 'Course', 'Invoice Date',
        'Amount', 'Payment Mode', 'Status', 'Academic Year'
    ]

    data = []
    for fee, student in fees:
        # Create invoice records for each installment
        installments = [
            (fee.installment_1, fee.invoice1_number, 'Installment 1'),
            (fee.installment_2, fee.invoice2_number, 'Installment 2'),
            (fee.installment_3, fee.invoice3_number, 'Installment 3'),
            (fee.installment_4, fee.invoice4_number, 'Installment 4'),
            (fee.installment_5, fee.invoice5_number, 'Installment 5'),
            (fee.installment_6, fee.invoice6_number, 'Installment 6')
        ]

        for amount, invoice_num, installment_type in installments:
            if amount and amount > 0:
                data.append([
                    invoice_num or f"INV-{student.student_unique_id}-{installment_type.replace(' ', '').lower()}",
                    student.student_unique_id,
                    f"{student.first_name} {student.last_name}",
                    student.current_course or '',
                    fee.created_at.strftime('%Y-%m-%d') if fee.created_at else '',
                    float(amount),
                    'Cash',  # Default payment mode
                    'Paid',
                    '2024-25'  # Default academic year
                ])

    return data, headers

def get_exams_export_data():
    """Get exams data for export"""
    exams = db.session.query(Exam, Student).join(Student).all()
    headers = [
        'Student ID', 'Student Name', 'Course', 'Exam Name', 'Semester', 'Exam Date',
        'Subject 1', 'Subject 1 Max', 'Subject 1 Obtained',
        'Subject 2', 'Subject 2 Max', 'Subject 2 Obtained',
        'Subject 3', 'Subject 3 Max', 'Subject 3 Obtained',
        'Total Max Marks', 'Total Obtained', 'Percentage', 'Grade', 'Status'
    ]

    data = []
    for exam, student in exams:
        data.append([
            student.student_unique_id,
            f"{student.first_name} {student.last_name}",
            student.current_course or '',
            exam.exam_name,
            exam.semester or '',
            exam.exam_date.strftime('%Y-%m-%d') if exam.exam_date else '',
            exam.subject1_name or '',
            exam.subject1_max_marks or 0,
            exam.subject1_obtained_marks or 0,
            exam.subject2_name or '',
            exam.subject2_max_marks or 0,
            exam.subject2_obtained_marks or 0,
            exam.subject3_name or '',
            exam.subject3_max_marks or 0,
            exam.subject3_obtained_marks or 0,
            exam.total_max_marks or 0,
            exam.total_obtained_marks or 0,
            float(exam.percentage) if exam.percentage else 0,
            exam.grade or '',
            exam.overall_status or ''
        ])

    return data, headers

def get_users_export_data():
    """Get users data for export"""
    users = db.session.query(UserProfile).join(UserProfile.role).all()
    headers = [
        'User ID', 'Username', 'First Name', 'Last Name', 'Email', 'Phone', 
        'Gender', 'Role', 'Status', 'Created Date'
    ]

    data = []
    for user in users:
        data.append([
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.email,
            user.phone or '',
            user.gender or '',
            user.role.role_name if user.role else '',
            user.status,
            user.created_at.strftime('%Y-%m-%d') if user.created_at else ''
        ])

    return data, headers

def process_import_file(file, data_type):
    """Process uploaded file for import"""
    try:
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if file_ext == 'csv':
            df = pd.read_csv(file)
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(file)
        else:
            return False, "Unsupported file format. Please use CSV or Excel files."

        # Convert DataFrame to records
        records = df.to_dict('records')

        if data_type == 'students':
            return import_students_data(records)
        elif data_type == 'courses':
            return import_courses_data(records)
        elif data_type == 'course_details':
            return import_course_details_data(records)
        elif data_type == 'users':
            return import_users_data(records)
        elif data_type == 'invoices':
            return import_invoices_data(records)
        else:
            return False, "Invalid data type specified."

    except Exception as e:
        return False, f"Error processing file: {str(e)}"

def _parse_admission_date(date_value):
    """Parse admission date from various formats (string, Timestamp, etc.)"""
    if not date_value:
        return date.today()
    
    # If it's already a pandas Timestamp, convert to date
    if hasattr(date_value, 'date'):
        return date_value.date()
    
    # If it's a string, try to parse it
    if isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, '%Y-%m-%d').date()
        except ValueError:
            # Try other common date formats
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
    
    # If it's a datetime object, extract the date
    if isinstance(date_value, datetime):
        return date_value.date()
    
    # Default fallback
    return date.today()

def import_students_data(records):
    """Import students data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                # Check if student already exists
                existing_student = Student.query.filter_by(
                    student_unique_id=record.get('Student ID', '')
                ).first()

                if existing_student:
                    errors.append(f"Row {i}: Student with ID {record.get('Student ID')} already exists")
                    continue

                # Create new student
                student = Student(
                    student_unique_id=record.get('Student ID', ''),
                    external_id=record.get('External ID', ''),
                    first_name=record.get('First Name', ''),
                    last_name=record.get('Last Name', ''),
                    father_name=record.get('Father Name', ''),
                    mother_name=record.get('Mother Name', ''),
                    gender=record.get('Gender', 'Male'),
                    category=record.get('Category', 'General'),
                    email=record.get('Email', ''),
                    current_course=record.get('Current Course', ''),
                    subject_1_name=record.get('Subject 1', ''),
                    subject_2_name=record.get('Subject 2', ''),
                    subject_3_name=record.get('Subject 3', ''),
                    percentage=float(record.get('Percentage', 0)) if record.get('Percentage') else None,
                    street=record.get('Street', ''),
                    area_village=record.get('Area/Village', ''),
                    city_tehsil=record.get('City/Tehsil', ''),
                    state=record.get('State', ''),
                    phone=record.get('Phone', ''),
                    aadhaar_card_number=record.get('Aadhaar Number', ''),
                    apaar_id=record.get('APAAR ID', ''),
                    school_name=record.get('School Name', ''),
                    scholarship_status=record.get('Scholarship Status', 'Applied'),
                    rebate_meera_scholarship_status=record.get('Meera Rebate Status', 'Applied'),
                    student_status=record.get('Student Status', 'Active'), # Changed from dropout_status
                    admission_date=_parse_admission_date(record.get('Admission Date'))
                )

                db.session.add(student)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.session.commit()

        message = f"Successfully imported {imported_count} students."
        if errors:
            message += f" {len(errors)} errors occurred:\n" + "\n".join(errors)

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def import_courses_data(records):
    """Import courses data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                # Check if course already exists
                existing_course = Course.query.filter_by(
                    course_short_name=record.get('Short Name', '')
                ).first()

                if existing_course:
                    errors.append(f"Row {i}: Course with short name {record.get('Short Name')} already exists")
                    continue

                # Create new course
                course = Course(
                    course_short_name=record.get('Short Name', ''),
                    course_full_name=record.get('Full Name', ''),
                    course_category=record.get('Category', ''),
                    duration=int(record.get('Duration (Years)', 3)) if record.get('Duration (Years)') else 3
                )

                db.session.add(course)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.session.commit()

        message = f"Successfully imported {imported_count} courses."
        if errors:
            message += f" {len(errors)} errors occurred."

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def import_course_details_data(records):
    """Import course details data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                # Create new course detail
                course_detail = CourseDetails(
                    course_full_name=record.get('Course Full Name', ''),
                    course_short_name=record.get('Course Short Name', ''),
                    year_semester=record.get('Year/Semester', ''),
                    course_tuition_fee=float(record.get('Course Tuition Fee', 0)) if record.get('Course Tuition Fee') else 0,
                    course_type=record.get('Course Type', ''),
                    misc_course_fees_1=float(record.get('Misc Fee 1', 0)) if record.get('Misc Fee 1') else 0,
                    misc_course_fees_2=float(record.get('Misc Fee 2', 0)) if record.get('Misc Fee 2') else 0,
                    misc_course_fees_3=float(record.get('Misc Fee 3', 0)) if record.get('Misc Fee 3') else 0,
                    misc_course_fees_4=float(record.get('Misc Fee 4', 0)) if record.get('Misc Fee 4') else 0,
                    misc_course_fees_5=float(record.get('Misc Fee 5', 0)) if record.get('Misc Fee 5') else 0,
                    misc_course_fees_6=float(record.get('Misc Fee 6', 0)) if record.get('Misc Fee 6') else 0,
                    total_course_fees=float(record.get('Total Course Fees', 0)) if record.get('Total Course Fees') else 0
                )

                db.session.add(course_detail)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.session.commit()

        message = f"Successfully imported {imported_count} course details."
        if errors:
            message += f" {len(errors)} errors occurred."

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def import_users_data(records):
    """Import users data from records"""
    try:
        imported_count = 0
        errors = []

        from werkzeug.security import generate_password_hash

        for i, record in enumerate(records, 1):
            try:
                # Check if user already exists
                existing_user = UserProfile.query.filter_by(
                    username=record.get('Username', '')
                ).first()

                if existing_user:
                    errors.append(f"Row {i}: User with username {record.get('Username')} already exists")
                    continue

                # Create new user
                user = UserProfile(
                    role_id=1,  # Default role
                    username=record.get('Username', ''),
                    first_name=record.get('First Name', ''),
                    last_name=record.get('Last Name', ''),
                    email=record.get('Email', ''),
                    phone=record.get('Phone', ''),
                    gender=record.get('Gender', ''),
                    password_hash=generate_password_hash('password123'),  # Default password
                    status=record.get('Status', 'Active')
                )

                db.session.add(user)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.session.commit()

        message = f"Successfully imported {imported_count} users."
        if errors:
            message += f" {len(errors)} errors occurred."

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def import_invoices_data(records):
    """Import invoices data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                # Find student by ID
                student = Student.query.filter_by(
                    student_unique_id=record.get('Student ID', '')
                ).first()

                if not student:
                    errors.append(f"Row {i}: Student with ID {record.get('Student ID')} not found")
                    continue

                # Find course by name
                course = Course.query.filter_by(
                    course_full_name=record.get('Course', '')
                ).first()

                if not course:
                    errors.append(f"Row {i}: Course {record.get('Course')} not found")
                    continue

                # Check if invoice already exists
                existing_invoice = Invoice.query.filter_by(
                    invoice_number=record.get('Invoice Number', '')
                ).first()

                if existing_invoice:
                    errors.append(f"Row {i}: Invoice with number {record.get('Invoice Number')} already exists")
                    continue

                # Parse date
                invoice_date = datetime.strptime(record.get('Invoice Date', ''), '%Y-%m-%d') if record.get('Invoice Date') else datetime.now()

                # Create new invoice
                invoice = Invoice(
                    student_id=student.id,
                    course_id=course.course_id,
                    invoice_number=record.get('Invoice Number', ''),
                    date_time=invoice_date,
                    invoice_amount=float(record.get('Amount', 0)) if record.get('Amount') else 0,
                    original_invoice_printed=record.get('Status', 'Not Printed') == 'Printed',
                    installment_number=int(record.get('Installment Number', 1)) if record.get('Installment Number') else 1
                )

                db.session.add(invoice)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.session.commit()

        message = f"Successfully imported {imported_count} invoices."
        if errors:
            message += f" {len(errors)} errors occurred."

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def get_export_data(data_type):
    """Get data for export based on data type"""
    if data_type == 'students':
        return get_students_export_data()
    elif data_type == 'courses':
        return get_courses_export_data()
    elif data_type == 'course_details':
        return get_course_details_export_data()
    elif data_type == 'fees':
        return get_fees_export_data()
    elif data_type == 'exams':
        return get_exams_export_data()
    elif data_type == 'invoices':
        return get_invoices_export_data()
    elif data_type == 'users':
        return get_users_export_data()
    elif data_type == 'subjects':
        return get_subjects_export_data()
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

def import_data(data_type, records):
    """Import data based on data type"""
    if data_type == 'students':
        return import_students_data(records)
    elif data_type == 'courses':
        return import_courses_data(records)
    elif data_type == 'course_details':
        return import_course_details_data(records)
    elif data_type == 'fees':
        return import_fees_data(records)
    elif data_type == 'exams':
        return import_exams_data(records)
    elif data_type == 'invoices':
        return import_invoices_data(records)
    elif data_type == 'users':
        return import_users_data(records)
    elif data_type == 'subjects':
        return import_subjects_data(records)
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

def import_fees_data(records):
    """Import fees data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                # Validate required fields
                student_id = str(record.get('Student ID', '')).strip()
                
                if not student_id:
                    errors.append(f"Row {i}: Student ID is required")
                    continue

                # Find student by student_unique_id
                student = Student.query.filter_by(student_unique_id=student_id).first()
                if not student:
                    errors.append(f"Row {i}: Student with ID '{student_id}' not found")
                    continue

                # Check if fee record already exists
                existing_fee = CollegeFees.query.filter_by(student_id=student.id).first()
                if existing_fee:
                    errors.append(f"Row {i}: Fee record for student '{student_id}' already exists")
                    continue

                # Get course information
                course = None
                if student.current_course:
                    course_detail = CourseDetails.query.filter_by(course_full_name=student.current_course).first()
                    if course_detail:
                        course = Course.query.filter_by(course_short_name=course_detail.course_short_name).first()

                # Create new fee record
                fee_record = CollegeFees(
                    student_id=student.id,
                    course_id=course.course_id if course else None,
                    total_course_fees=float(record.get('Total Fee', 0) or 0),
                    installment_1=float(record.get('Installment 1', 0) or 0),
                    installment_2=float(record.get('Installment 2', 0) or 0),
                    installment_3=float(record.get('Installment 3', 0) or 0),
                    installment_4=float(record.get('Installment 4', 0) or 0),
                    installment_5=float(record.get('Installment 5', 0) or 0),
                    installment_6=float(record.get('Installment 6', 0) or 0)
                )

                db.session.add(fee_record)
                imported_count += 1

            except Exception as e:
                db.session.rollback()
                errors.append(f"Row {i}: {str(e)}")
                continue

        # Commit all fee records at once
        if imported_count > 0:
            db.session.commit()

        message = f"Successfully imported {imported_count} fee records."
        if errors:
            message += f" {len(errors)} errors occurred:\n" + "\n".join(errors)

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def import_exams_data(records):
    """Import exams data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                # Validate required fields
                student_id = str(record.get('Student ID', '')).strip()
                exam_name = str(record.get('Exam Name', '')).strip()
                
                if not student_id:
                    errors.append(f"Row {i}: Student ID is required")
                    continue
                    
                if not exam_name:
                    errors.append(f"Row {i}: Exam Name is required")
                    continue

                # Find student by student_unique_id
                student = Student.query.filter_by(student_unique_id=student_id).first()
                if not student:
                    errors.append(f"Row {i}: Student with ID '{student_id}' not found")
                    continue

                # Get course information
                course = None
                if student.current_course:
                    course_detail = CourseDetails.query.filter_by(course_full_name=student.current_course).first()
                    if course_detail:
                        course = Course.query.filter_by(course_short_name=course_detail.course_short_name).first()

                # Parse exam date
                exam_date = None
                if record.get('Exam Date'):
                    try:
                        from datetime import datetime
                        exam_date = datetime.strptime(str(record.get('Exam Date')), '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            exam_date = datetime.strptime(str(record.get('Exam Date')), '%m/%d/%Y').date()
                        except ValueError:
                            errors.append(f"Row {i}: Invalid exam date format. Use YYYY-MM-DD or MM/DD/YYYY")
                            continue

                # Get subject data and calculate totals
                subjects_data = []
                total_max = 0
                total_obtained = 0

                for j in range(1, 7):  # Support up to 6 subjects
                    subject_name = record.get(f'Subject {j}')
                    max_marks = record.get(f'Subject {j} Max')
                    obtained_marks = record.get(f'Subject {j} Obtained')

                    if subject_name and max_marks is not None and obtained_marks is not None:
                        try:
                            max_marks = int(max_marks)
                            obtained_marks = int(obtained_marks)
                            
                            if obtained_marks > max_marks:
                                errors.append(f"Row {i}: Subject {j} obtained marks cannot exceed max marks")
                                continue
                                
                            subjects_data.append({
                                'name': str(subject_name),
                                'max': max_marks,
                                'obtained': obtained_marks
                            })
                            total_max += max_marks
                            total_obtained += obtained_marks
                        except ValueError:
                            errors.append(f"Row {i}: Invalid marks format for Subject {j}")
                            continue

                if not subjects_data:
                    errors.append(f"Row {i}: At least one subject is required")
                    continue

                # Calculate percentage and grade
                percentage = (total_obtained / total_max * 100) if total_max > 0 else 0
                
                # Calculate grade based on percentage
                if percentage >= 90:
                    grade = 'A+'
                elif percentage >= 80:
                    grade = 'A'
                elif percentage >= 70:
                    grade = 'B+'
                elif percentage >= 60:
                    grade = 'B'
                elif percentage >= 50:
                    grade = 'C+'
                elif percentage >= 40:
                    grade = 'C'
                else:
                    grade = 'F'

                overall_status = 'Pass' if percentage >= 40 else 'Fail'

                # Create exam record
                exam_data = {
                    'student_id': student.id,
                    'course_id': course.course_id if course else None,
                    'exam_name': exam_name,
                    'semester': str(record.get('Semester', '')).strip(),
                    'exam_date': exam_date,
                    'total_max_marks': total_max,
                    'total_obtained_marks': total_obtained,
                    'percentage': round(percentage, 2),
                    'grade': grade,
                    'overall_status': overall_status
                }

                # Add subject-wise marks
                for j, subject_data in enumerate(subjects_data[:6]):  # Max 6 subjects
                    exam_data[f'subject{j+1}_name'] = subject_data['name']
                    exam_data[f'subject{j+1}_max_marks'] = subject_data['max']
                    exam_data[f'subject{j+1}_obtained_marks'] = subject_data['obtained']

                exam = Exam(**exam_data)
                db.session.add(exam)
                imported_count += 1

            except Exception as e:
                db.session.rollback()
                errors.append(f"Row {i}: {str(e)}")
                continue

        # Commit all exam records at once
        if imported_count > 0:
            db.session.commit()

        message = f"Successfully imported {imported_count} exam records."
        if errors:
            message += f" {len(errors)} errors occurred:\n" + "\n".join(errors)

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def export_users_data():
    """Export users data"""
    from models import UserProfile, UserRole

    users = db.session.query(UserProfile).join(UserProfile.role).all()

    data = []
    for user in users:
        data.append([
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.email,
            user.phone or '',
            user.gender or '',
            user.role.role_name if user.role else '',
            user.status,
            user.created_at.strftime('%Y-%m-%d') if user.created_at else ''
        ])

    headers = [
        'User ID', 'Username', 'First Name', 'Last Name', 'Email', 'Phone',
        'Gender', 'Role', 'Status', 'Created Date'
    ]

    return data, headers

def import_users_data(records):
    """Import users data from records"""
    from models import UserProfile, UserRole
    from werkzeug.security import generate_password_hash

    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                # Validate required fields
                username = str(record.get('Username', '')).strip()
                first_name = str(record.get('First Name', '')).strip()
                last_name = str(record.get('Last Name', '')).strip()
                email = str(record.get('Email', '')).strip()

                if not username:
                    errors.append(f"Row {i}: Username is required")
                    continue

                if not first_name:
                    errors.append(f"Row {i}: First Name is required")
                    continue

                if not last_name:
                    errors.append(f"Row {i}: Last Name is required")
                    continue

                if not email:
                    errors.append(f"Row {i}: Email is required")
                    continue

                # Check if user already exists
                existing_user = UserProfile.query.filter_by(username=username).first()
                if existing_user:
                    errors.append(f"Row {i}: User with username '{username}' already exists")
                    continue

                # Check if email already exists
                existing_email = UserProfile.query.filter_by(email=email).first()
                if existing_email:
                    errors.append(f"Row {i}: User with email '{email}' already exists")
                    continue

                # Get role_id - default to 1 if not specified or role doesn't exist
                role_id = 1  # Default role
                role_name = str(record.get('Role', '')).strip()
                if role_name:
                    role = UserRole.query.filter_by(role_name=role_name).first()
                    if role:
                        role_id = role.role_id
                    else:
                        errors.append(f"Row {i}: Role '{role_name}' not found, using default role")

                # Create new user
                user = UserProfile(
                    role_id=role_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=str(record.get('Phone', '')).strip(),
                    gender=str(record.get('Gender', '')).strip(),
                    password_hash=generate_password_hash('password123'),  # Default password
                    status=str(record.get('Status', 'Active')).strip()
                )

                db.session.add(user)
                imported_count += 1

            except Exception as e:
                db.session.rollback()
                errors.append(f"Row {i}: {str(e)}")
                continue

        # Commit all users at once
        if imported_count > 0:
            db.session.commit()

        message = f"Successfully imported {imported_count} users."
        if errors:
            message += f" {len(errors)} errors occurred:\n" + "\n".join(errors)

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"


def get_subjects_export_data():
    """Export subjects data"""
    subjects = Subject.query.all()

    data = []
    for subject in subjects:
        data.append([
            subject.course_short_name,
            subject.subject_name,
            subject.subject_type,
        ])
    headers = [
        'Course Short Name', 'Subject Name', 'Subject Type',
    ]

    return data, headers

def import_subjects_data(records):
    """Import subjects data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                course_short_name = record.get('Course Short Name', '')
                subject_name = record.get('Subject Name', '')
                subject_type = record.get('Subject Type', 'Core')

                if not course_short_name or not subject_name:
                    errors.append(f"Row {i}: Course Short Name and Subject Name are required.")
                    continue

                # Check if subject already exists
                existing_subject = Subject.query.filter_by(
                    course_short_name=course_short_name,
                    subject_name=subject_name
                ).first()

                if existing_subject:
                    errors.append(f"Row {i}: Subject with name {subject_name} already exists for course {course_short_name}.")
                    continue

                # Create new subject
                subject = Subject(
                    course_short_name=course_short_name,
                    subject_name=subject_name,
                    subject_type=subject_type,
                )

                db.session.add(subject)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.session.commit()

        message = f"Successfully imported {imported_count} subjects."
        if errors:
            message += f" {len(errors)} errors occurred."

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def process_import_file(file, data_type):
    """Process uploaded file for import"""
    try:
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if file_ext == 'csv':
            df = pd.read_csv(file)
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(file)
        else:
            return False, "Unsupported file format. Please use CSV or Excel files."

        # Convert DataFrame to records
        records = df.to_dict('records')

        if data_type == 'students':
            return import_students_data(records)
        elif data_type == 'courses':
            return import_courses_data(records)
        elif data_type == 'course_details':
            return import_course_details_data(records)
        elif data_type == 'users':
            return import_users_data(records)
        elif data_type == 'fees':
            return import_fees_data(records)
        elif data_type == 'invoices':
            return import_invoices_data(records)
        elif data_type == 'exams':
            return import_exams_data(records)
        elif data_type == 'subjects':
            return import_subjects_data(records)
        else:
            return False, "Invalid data type specified."

    except Exception as e:
        return False, f"Error processing file: {str(e)}"

def import_subjects_data(records):
    """Import subjects data from records"""
    try:
        imported_count = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                course_short_name = record.get('Course Short Name', '')
                subject_name = record.get('Subject Name', '')
                subject_type = record.get('Subject Type', 'Compulsory')

                if not course_short_name or not subject_name:
                    errors.append(f"Row {i}: Course Short Name and Subject Name are required.")
                    continue

                # Check if subject already exists
                existing_subject = Subject.query.filter_by(
                    course_short_name=course_short_name,
                    subject_name=subject_name
                ).first()

                if existing_subject:
                    errors.append(f"Row {i}: Subject with name {subject_name} already exists for course {course_short_name}.")
                    continue

                # Create new subject
                subject = Subject(
                    course_short_name=course_short_name,
                    subject_name=subject_name,
                    subject_type=subject_type,
                )

                db.session.add(subject)
                imported_count += 1

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        db.session.commit()

        message = f"Successfully imported {imported_count} subjects."
        if errors:
            message += f" {len(errors)} errors occurred."

        return True, message

    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

