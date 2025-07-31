#!/usr/bin/env python3
"""
SRBMC College Management ERP - Dummy Data Population Script
This script populates the database with realistic sample data for testing and demonstration purposes.
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add the current directory to sys.path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (UserRole, UserProfile, Course, CourseDetails, Subject,
                    Student, CollegeFees, Invoice, Exam)
from werkzeug.security import generate_password_hash
from utils import generate_student_id, generate_invoice_number, calculate_grade


def clear_existing_data():
    """Clear existing data from all tables (except user roles and profiles)"""
    print("Clearing existing data...")

    # Clear data in dependency order
    Exam.query.delete()
    Invoice.query.delete()
    CollegeFees.query.delete()
    Student.query.delete()
    Subject.query.delete()
    CourseDetails.query.delete()
    Course.query.delete()

    db.session.commit()
    print("✓ Existing data cleared")


def create_courses_and_subjects():
    """Create courses, course details, and subjects"""
    print("Creating courses and subjects...")

    # Courses data
    courses_data = [{
        'course_short_name': 'BA',
        'course_full_name': 'Bachelor of Arts',
        'course_category': 'Undergraduate',
        'duration': 3
    }, {
        'course_short_name': 'BSC',
        'course_full_name': 'Bachelor of Science',
        'course_category': 'Undergraduate',
        'duration': 3
    }, {
        'course_short_name': 'MA',
        'course_full_name': 'Master of Arts',
        'course_category': 'Postgraduate',
        'duration': 2
    }, {
        'course_short_name': 'BCOM',
        'course_full_name': 'Bachelor of Commerce',
        'course_category': 'Undergraduate',
        'duration': 3
    }]

    # Create courses
    for course_data in courses_data:
        if not Course.query.filter_by(
                course_short_name=course_data['course_short_name']).first():
            course = Course(**course_data)
            db.session.add(course)

    db.session.commit()

    # Course details with fees
    course_details_data = [
        # Bachelor of Arts
        {
            'course_full_name': 'Bachelor of Arts - 1st Year',
            'course_short_name': 'BA',
            'year_semester': '1st Year',
            'course_tuition_fee': 12000,
            'total_course_fees': 15000
        },
        {
            'course_full_name': 'Bachelor of Arts - 2nd Year',
            'course_short_name': 'BA',
            'year_semester': '2nd Year',
            'course_tuition_fee': 12000,
            'total_course_fees': 15000
        },
        {
            'course_full_name': 'Bachelor of Arts - 3rd Year',
            'course_short_name': 'BA',
            'year_semester': '3rd Year',
            'course_tuition_fee': 12000,
            'total_course_fees': 15000
        },

        # Bachelor of Science
        {
            'course_full_name': 'Bachelor of Science - 1st Year',
            'course_short_name': 'BSC',
            'year_semester': '1st Year',
            'course_tuition_fee': 15000,
            'total_course_fees': 18000
        },
        {
            'course_full_name': 'Bachelor of Science - 2nd Year',
            'course_short_name': 'BSC',
            'year_semester': '2nd Year',
            'course_tuition_fee': 15000,
            'total_course_fees': 18000
        },
        {
            'course_full_name': 'Bachelor of Science - 3rd Year',
            'course_short_name': 'BSC',
            'year_semester': '3rd Year',
            'course_tuition_fee': 15000,
            'total_course_fees': 18000
        },

        # Master of Arts
        {
            'course_full_name': 'Master of Arts - 1st Year',
            'course_short_name': 'MA',
            'year_semester': '1st Year',
            'course_tuition_fee': 20000,
            'total_course_fees': 25000
        },
        {
            'course_full_name': 'Master of Arts - 2nd Year',
            'course_short_name': 'MA',
            'year_semester': '2nd Year',
            'course_tuition_fee': 20000,
            'total_course_fees': 25000
        },

        # Bachelor of Commerce
        {
            'course_full_name': 'Bachelor of Commerce - 1st Year',
            'course_short_name': 'BCOM',
            'year_semester': '1st Year',
            'course_tuition_fee': 14000,
            'total_course_fees': 17000
        },
        {
            'course_full_name': 'Bachelor of Commerce - 2nd Year',
            'course_short_name': 'BCOM',
            'year_semester': '2nd Year',
            'course_tuition_fee': 14000,
            'total_course_fees': 17000
        },
        {
            'course_full_name': 'Bachelor of Commerce - 3rd Year',
            'course_short_name': 'BCOM',
            'year_semester': '3rd Year',
            'course_tuition_fee': 14000,
            'total_course_fees': 17000
        },
    ]

    for detail_data in course_details_data:
        if not CourseDetails.query.filter_by(
                course_full_name=detail_data['course_full_name']).first():
            course_detail = CourseDetails(**detail_data)
            db.session.add(course_detail)

    db.session.commit()

    # Subjects data
    subjects_data = [
        # BA Subjects
        {
            'course_short_name': 'BA',
            'subject_name': 'English Literature',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BA',
            'subject_name': 'Hindi Literature',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BA',
            'subject_name': 'History',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BA',
            'subject_name': 'Political Science',
            'subject_type': 'Elective'
        },
        {
            'course_short_name': 'BA',
            'subject_name': 'Economics',
            'subject_type': 'Elective'
        },
        {
            'course_short_name': 'BA',
            'subject_name': 'Philosophy',
            'subject_type': 'Elective'
        },
        {
            'course_short_name': 'BA',
            'subject_name': 'Psychology',
            'subject_type': 'Elective'
        },

        # BSC Subjects
        {
            'course_short_name': 'BSC',
            'subject_name': 'Mathematics',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BSC',
            'subject_name': 'Physics',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BSC',
            'subject_name': 'Chemistry',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BSC',
            'subject_name': 'Biology',
            'subject_type': 'Elective'
        },
        {
            'course_short_name': 'BSC',
            'subject_name': 'Computer Science',
            'subject_type': 'Elective'
        },
        {
            'course_short_name': 'BSC',
            'subject_name': 'Statistics',
            'subject_type': 'Elective'
        },

        # MA Subjects
        {
            'course_short_name': 'MA',
            'subject_name': 'Advanced English Literature',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'MA',
            'subject_name': 'Research Methodology',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'MA',
            'subject_name': 'Modern Indian History',
            'subject_type': 'Elective'
        },
        {
            'course_short_name': 'MA',
            'subject_name': 'International Relations',
            'subject_type': 'Elective'
        },

        # BCOM Subjects
        {
            'course_short_name': 'BCOM',
            'subject_name': 'Accounting',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BCOM',
            'subject_name': 'Business Studies',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BCOM',
            'subject_name': 'Economics',
            'subject_type': 'Compulsory'
        },
        {
            'course_short_name': 'BCOM',
            'subject_name': 'Mathematics',
            'subject_type': 'Elective'
        },
        {
            'course_short_name': 'BCOM',
            'subject_name': 'Computer Applications',
            'subject_type': 'Elective'
        },
    ]

    for subject_data in subjects_data:
        if not Subject.query.filter_by(
                course_short_name=subject_data['course_short_name'],
                subject_name=subject_data['subject_name']).first():
            subject = Subject(**subject_data)
            db.session.add(subject)

    db.session.commit()
    print("✓ Courses and subjects created")


def create_students():
    """Create sample students with realistic data"""
    print("Creating students...")

    # Sample student names and data
    first_names = [
        'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh',
        'Ayaan', 'Krishna', 'Ishaan', 'Ananya', 'Aanya', 'Kiara', 'Diya',
        'Pihu', 'Priya', 'Anvi', 'Riya', 'Navya', 'Kavya', 'Rajesh', 'Suresh',
        'Mahesh', 'Ramesh', 'Dinesh', 'Ganesh', 'Naresh', 'Umesh', 'Ritesh',
        'Lokesh', 'Sunita', 'Geeta', 'Seeta', 'Meera', 'Deepa', 'Reeta',
        'Neeta', 'Veena', 'Leela', 'Sheela'
    ]

    last_names = [
        'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Agarwal', 'Jain',
        'Bansal', 'Garg', 'Mittal', 'Joshi', 'Saxena', 'Tiwari', 'Pandey',
        'Mishra', 'Srivastava', 'Shukla', 'Dubey', 'Yadav', 'Patel', 'Shah',
        'Mehta', 'Modi', 'Desai', 'Thakkar', 'Vyas', 'Trivedi', 'Jha', 'Sinha',
        'Mathur'
    ]

    father_names = [
        'Ramesh Kumar', 'Suresh Singh', 'Mahesh Sharma', 'Dinesh Gupta',
        'Rajesh Verma', 'Mukesh Agarwal', 'Naresh Jain', 'Umesh Bansal',
        'Ganesh Garg', 'Lokesh Mittal'
    ]

    mother_names = [
        'Sunita Devi', 'Geeta Sharma', 'Meera Singh', 'Deepa Gupta',
        'Seeta Verma', 'Reeta Agarwal', 'Neeta Jain', 'Veena Bansal',
        'Leela Garg', 'Sheela Mittal'
    ]

    cities = [
        'Raniwara', 'Jalore', 'Sirohi', 'Pali', 'Jodhpur', 'Barmer',
        'Jaisalmer', 'Bikaner', 'Udaipur', 'Ajmer'
    ]

    schools = [
        'Government Senior Secondary School, Raniwara',
        'Rajasthan Public School, Jalore',
        'Vidya Mandir Senior Secondary School', 'Saint Mary\'s Convent School',
        'Government Girls Senior Secondary School', 'Kendriya Vidyalaya',
        'Modern Public School', 'Delhi Public School', 'Central Academy',
        'Regional Institute of Education'
    ]

    courses = [
        'Bachelor of Arts - 1st Year', 'Bachelor of Arts - 2nd Year',
        'Bachelor of Arts - 3rd Year', 'Bachelor of Science - 1st Year',
        'Bachelor of Science - 2nd Year', 'Bachelor of Science - 3rd Year',
        'Bachelor of Commerce - 1st Year', 'Bachelor of Commerce - 2nd Year',
        'Bachelor of Commerce - 3rd Year', 'Master of Arts - 1st Year',
        'Master of Arts - 2nd Year'
    ]

    # Get subjects for assignment
    ba_subjects = [
        s.subject_name
        for s in Subject.query.filter_by(course_short_name='BA').all()
    ]
    bsc_subjects = [
        s.subject_name
        for s in Subject.query.filter_by(course_short_name='BSC').all()
    ]
    bcom_subjects = [
        s.subject_name
        for s in Subject.query.filter_by(course_short_name='BCOM').all()
    ]
    ma_subjects = [
        s.subject_name
        for s in Subject.query.filter_by(course_short_name='MA').all()
    ]

    # Create 150 students
    for i in range(150):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        father_name = random.choice(father_names)
        mother_name = random.choice(mother_names)
        current_course = random.choice(courses)

        # Determine course short name for ID generation
        if 'Bachelor of Arts' in current_course:
            course_short = 'BA'
            available_subjects = ba_subjects
        elif 'Bachelor of Science' in current_course:
            course_short = 'BSC'
            available_subjects = bsc_subjects
        elif 'Bachelor of Commerce' in current_course:
            course_short = 'BCOM'
            available_subjects = bcom_subjects
        else:  # Master of Arts
            course_short = 'MA'
            available_subjects = ma_subjects

        # Generate unique student ID
        admission_year = random.choice([2022, 2023, 2024])
        student_unique_id = generate_student_id(course_short, admission_year)

        # Ensure unique ID
        while Student.query.filter_by(
                student_unique_id=student_unique_id).first():
            student_unique_id = generate_student_id(course_short,
                                                    admission_year)

        # Select subjects
        selected_subjects = random.sample(available_subjects,
                                          min(3, len(available_subjects)))

        student_data = {
            'student_unique_id':
            student_unique_id,
            'external_id':
            f'EXT{2024000 + i}',
            'first_name':
            first_name,
            'last_name':
            last_name,
            'father_name':
            father_name,
            'mother_name':
            mother_name,
            'gender':
            random.choice(['Male', 'Female']),
            'category':
            random.choice(['General', 'OBC', 'SC', 'ST']),
            'email':
            f'{first_name.lower()}.{last_name.lower()}@example.com',
            'current_course':
            current_course,
            'subject_1_name':
            selected_subjects[0] if len(selected_subjects) > 0 else None,
            'subject_2_name':
            selected_subjects[1] if len(selected_subjects) > 1 else None,
            'subject_3_name':
            selected_subjects[2] if len(selected_subjects) > 2 else None,
            'percentage':
            round(random.uniform(60.0, 95.0), 2),
            'street':
            f'{random.randint(1, 999)} Main Street',
            'area_village':
            f'Ward {random.randint(1, 10)}',
            'city_tehsil':
            random.choice(cities),
            'state':
            'Rajasthan',
            'phone':
            f'9{random.randint(100000000, 999999999)}',
            'aadhaar_card_number':
            f'{random.randint(100000000000, 999999999999)}',
            'school_name':
            random.choice(schools),
            'scholarship_status':
            random.choice(['Applied', 'Approved', 'Rejected']),
            'rebate_meera_scholarship_status':
            random.choice(['Applied', 'Approved', 'Rejected']),
            'dropout_status':
            random.choice(['Active'] * 9 + ['Dropout']),  # 90% active
            'admission_date':
            date(admission_year, random.randint(6, 8), random.randint(1, 28))
        }

        student = Student(**student_data)
        db.session.add(student)

        # Commit every 25 students to avoid memory issues
        if (i + 1) % 25 == 0:
            db.session.commit()

    db.session.commit()
    print("✓ Students created")


def create_fees_and_invoices():
    """Create fee records and invoices for students"""
    print("Creating fees and invoices...")

    students = Student.query.all()
    courses = Course.query.all()
    course_details = CourseDetails.query.all()

    payment_modes = ['Cash', 'Online', 'Cheque', 'DD']

    for student in students:
        # Find matching course
        course = None
        course_detail = None

        for cd in course_details:
            if cd.course_full_name == student.current_course:
                course_detail = cd
                for c in courses:
                    if c.course_short_name == cd.course_short_name:
                        course = c
                        break
                break

        if not course or not course_detail:
            continue

        # Create fee record
        total_fee = float(course_detail.total_course_fees)

        # Generate installments (2-4 installments)
        num_installments = random.randint(2, 4)
        installment_amount = total_fee / num_installments

        installments = [installment_amount] * num_installments
        # Add some variation
        for i in range(len(installments) - 1):
            variation = random.uniform(-0.1, 0.1) * installment_amount
            installments[i] += variation
            installments[-1] -= variation

        fee_data = {
            'student_id':
            student.id,
            'course_id':
            course.course_id,
            'course_tuition_fee':
            course_detail.course_tuition_fee,
            'enrollment_fee':
            500,
            'eligibility_certificate_fee':
            200,
            'university_affiliation_fee':
            300,
            'university_sports_fee':
            100,
            'university_development_fee':
            400,
            'tc_cc_fee':
            50,
            'miscellaneous_fee_1':
            200,
            'miscellaneous_fee_2':
            150,
            'miscellaneous_fee_3':
            100,
            'total_fee':
            total_fee,
            'payment_mode':
            random.choice(payment_modes),
            'installment_1':
            round(installments[0], 2) if len(installments) > 0 else 0,
            'installment_2':
            round(installments[1], 2) if len(installments) > 1 else 0,
            'installment_3':
            round(installments[2], 2) if len(installments) > 2 else 0,
            'installment_4':
            round(installments[3], 2) if len(installments) > 3 else 0,
            'installment_5':
            0,
            'installment_6':
            0
        }

        college_fee = CollegeFees(**fee_data)
        db.session.add(college_fee)
        db.session.flush()  # Get the fee ID

        # Create invoices for paid installments (80% of students have paid at least 1 installment)
        if random.random() < 0.8:
            num_paid = random.randint(1, num_installments)

            for installment_num in range(1, num_paid + 1):
                invoice_number = generate_invoice_number()
                while Invoice.query.filter_by(
                        invoice_number=invoice_number).first():
                    invoice_number = generate_invoice_number()

                installment_amount = getattr(college_fee,
                                             f'installment_{installment_num}')

                if installment_amount > 0:
                    invoice_data = {
                        'student_id':
                        student.id,
                        'course_id':
                        course.course_id,
                        'invoice_number':
                        invoice_number,
                        'date_time':
                        datetime.now() -
                        timedelta(days=random.randint(1, 180)),
                        'invoice_amount':
                        installment_amount,
                        'original_invoice_printed':
                        random.choice([True, False]),
                        'installment_number':
                        installment_num
                    }

                    invoice = Invoice(**invoice_data)
                    db.session.add(invoice)

                    # Update fee record with invoice number
                    setattr(college_fee, f'invoice{installment_num}_number',
                            invoice_number)

    db.session.commit()
    print("✓ Fees and invoices created")


def create_exams():
    """Create exam records for students"""
    print("Creating exam records...")

    students = Student.query.all()
    courses = Course.query.all()

    exam_names = [
        'First Semester Examination', 'Second Semester Examination',
        'Third Semester Examination', 'Fourth Semester Examination',
        'Fifth Semester Examination', 'Sixth Semester Examination',
        'Annual Examination', 'Supplementary Examination'
    ]

    for student in students:
        # Find student's course
        course = None
        for c in courses:
            if c.course_short_name in student.current_course:
                course = c
                break

        if not course:
            continue

        # Create 1-3 exam records per student
        num_exams = random.randint(1, 3)

        for exam_num in range(num_exams):
            exam_name = random.choice(exam_names)
            semester = f"Semester {random.randint(1, 6)}"

            # Get subjects for this student
            subjects = [
                student.subject_1_name, student.subject_2_name,
                student.subject_3_name
            ]
            subjects = [s for s in subjects if s]  # Remove None values

            # Generate marks for each subject
            subject_marks = []
            total_max = 0
            total_obtained = 0

            for i, subject in enumerate(subjects[:6]):  # Max 6 subjects
                if subject:
                    max_marks = 100
                    # Generate realistic marks (60-95% of max marks)
                    obtained_marks = random.randint(int(max_marks * 0.6),
                                                    int(max_marks * 0.95))

                    subject_marks.append({
                        'name': subject,
                        'max': max_marks,
                        'obtained': obtained_marks
                    })

                    total_max += max_marks
                    total_obtained += obtained_marks

            # Calculate percentage and grade
            percentage = (total_obtained / total_max *
                          100) if total_max > 0 else 0
            grade = calculate_grade(percentage)
            overall_status = 'Pass' if percentage >= 40 else 'Fail'

            exam_data = {
                'student_id': student.id,
                'course_id': course.course_id,
                'semester': semester,
                'exam_name': exam_name,
                'total_max_marks': total_max,
                'total_obtained_marks': total_obtained,
                'percentage': round(percentage, 2),
                'grade': grade,
                'overall_status': overall_status,
                'exam_date':
                date.today() - timedelta(days=random.randint(30, 365))
            }

            # Add subject-wise marks
            for i, marks in enumerate(subject_marks):
                if i < 6:  # Database supports up to 6 subjects
                    exam_data[f'subject{i+1}_name'] = marks['name']
                    exam_data[f'subject{i+1}_max_marks'] = marks['max']
                    exam_data[f'subject{i+1}_obtained_marks'] = marks[
                        'obtained']

            exam = Exam(**exam_data)
            db.session.add(exam)

    db.session.commit()
    print("✓ Exam records created")


def create_additional_users():
    """Create additional users for different roles"""
    print("Creating additional users...")

    # Get roles
    roles = {role.role_name: role for role in UserRole.query.all()}

    additional_users = [{
        'username': 'admission_officer',
        'password': 'admission123',
        'first_name': 'Rajesh',
        'last_name': 'Kumar',
        'email': 'admission@srbmc.edu.in',
        'role': 'Admission Officer',
        'phone': '9876543210'
    }, {
        'username': 'accountant',
        'password': 'account123',
        'first_name': 'Priya',
        'last_name': 'Sharma',
        'email': 'accounts@srbmc.edu.in',
        'role': 'Accountant',
        'phone': '9876543211'
    }, {
        'username': 'exam_controller',
        'password': 'exam123',
        'first_name': 'Suresh',
        'last_name': 'Gupta',
        'email': 'exams@srbmc.edu.in',
        'role': 'Exam Controller',
        'phone': '9876543212'
    }, {
        'username': 'admission_assistant',
        'password': 'assist123',
        'first_name': 'Neha',
        'last_name': 'Jain',
        'email': 'assist.admission@srbmc.edu.in',
        'role': 'Admission Assistant',
        'phone': '9876543213'
    }]

    for user_data in additional_users:
        if not UserProfile.query.filter_by(
                username=user_data['username']).first():
            role = roles.get(user_data['role'])
            if role:
                user = UserProfile(role_id=role.role_id,
                                   first_name=user_data['first_name'],
                                   last_name=user_data['last_name'],
                                   email=user_data['email'],
                                   phone=user_data['phone'],
                                   username=user_data['username'],
                                   password_hash=generate_password_hash(
                                       user_data['password']),
                                   status='Active',
                                   gender='Male' if user_data['first_name']
                                   in ['Rajesh', 'Suresh'] else 'Female',
                                   city_tehsil='Raniwara',
                                   state='Rajasthan')
                db.session.add(user)

    db.session.commit()
    print("✓ Additional users created")


def print_summary():
    """Print summary of created data"""
    print("\n" + "=" * 50)
    print("DUMMY DATA CREATION SUMMARY")
    print("=" * 50)

    print(f"User Roles: {UserRole.query.count()}")
    print(f"User Profiles: {UserProfile.query.count()}")
    print(f"Courses: {Course.query.count()}")
    print(f"Course Details: {CourseDetails.query.count()}")
    print(f"Subjects: {Subject.query.count()}")
    print(f"Students: {Student.query.count()}")
    print(f"Fee Records: {CollegeFees.query.count()}")
    print(f"Invoices: {Invoice.query.count()}")
    print(f"Exam Records: {Exam.query.count()}")

    print("\n" + "=" * 50)
    print("DEFAULT LOGIN CREDENTIALS")
    print("=" * 50)
    print("Administrator: admin/admin")
    print("User 1: Vishal/Vishal")
    print("User 2: Sonali/Sonali")
    print("Admission Officer: admission_officer/admission123")
    print("Accountant: accountant/account123")
    print("Exam Controller: exam_controller/exam123")
    print("Admission Assistant: admission_assistant/assist123")
    print("=" * 50)


def main():
    """Main function to populate dummy data"""
    with app.app_context():
        print("Starting SRBMC ERP Dummy Data Population...")
        print("=" * 50)

        # Clear existing data (except users and roles)
        clear_existing_data()

        # Create all data
        create_courses_and_subjects()
        create_students()
        create_fees_and_invoices()
        create_exams()
        create_additional_users()

        # Print summary
        print_summary()

        print("\n✅ Dummy data population completed successfully!")
        print(
            "You can now log in to the system and explore all features with realistic data."
        )


if __name__ == "__main__":
    main()
