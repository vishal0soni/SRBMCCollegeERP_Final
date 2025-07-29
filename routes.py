from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, and_, or_
from datetime import datetime, date
import io
import csv
import pandas as pd

from app import app, db
from models import *
from forms import *
from utils import generate_student_id, generate_invoice_number, calculate_grade, can_edit_module, send_email, generate_pdf_invoice, generate_pdf_report_card

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserProfile.query.filter_by(username=form.username.data).first()
        if user and user.password_hash and check_password_hash(user.password_hash, form.password.data):
            if user.status == 'Active':
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Your account is inactive. Please contact administrator.', 'error')
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    stats = {
        'total_students': Student.query.count(),
        'active_students': Student.query.filter_by(dropout_status='Active').count(),
        'total_courses': Course.query.count(),
        'pending_fees': db.session.query(func.sum(CollegeFees.total_fee - 
                                                  (CollegeFees.installment_1 + CollegeFees.installment_2 + 
                                                   CollegeFees.installment_3 + CollegeFees.installment_4 + 
                                                   CollegeFees.installment_5 + CollegeFees.installment_6))).scalar() or 0
    }
    
    # Recent activities
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_payments = Invoice.query.order_by(Invoice.date_time.desc()).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, 
                         recent_students=recent_students, recent_payments=recent_payments)

# Admin Routes
@app.route('/admin/users')
@login_required
def admin_users():
    if not can_edit_module(current_user, 'admin'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    users = UserProfile.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if not can_edit_module(current_user, 'admin'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    form = UserForm()
    form.role_id.choices = [(r.role_id, r.role_name) for r in UserRole.query.all()]
    
    if form.validate_on_submit():
        user = UserProfile(
            role_id=form.role_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            gender=form.gender.data,
            birthdate=form.birthdate.data,
            street=form.street.data,
            area_village=form.area_village.data,
            city_tehsil=form.city_tehsil.data,
            state=form.state.data,
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data or 'password123'),
            status=form.status.data
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send welcome email
            if user.email:
                send_email(user.email, 'Welcome to SRBMC ERP', 
                          f'Your account has been created. Username: {user.username}, Password: {form.password.data or "password123"}')
            
            flash('User created successfully!', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('admin/user_form.html', form=form, title='Add User')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not can_edit_module(current_user, 'admin'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    user = UserProfile.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role_id.choices = [(r.role_id, r.role_name) for r in UserRole.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(user)
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        user.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')
    
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)

# Student Routes
@app.route('/students')
@login_required
def students():
    if not can_edit_module(current_user, 'students'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    course_filter = request.args.get('course', '')
    gender_filter = request.args.get('gender', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    
    query = Student.query
    
    if course_filter:
        query = query.filter(Student.current_course.contains(course_filter))
    if gender_filter:
        query = query.filter_by(gender=gender_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if status_filter:
        query = query.filter_by(dropout_status=status_filter)
    
    students = query.paginate(page=page, per_page=20, error_out=False)
    
    # Get filter options
    courses = db.session.query(Student.current_course).distinct().all()
    
    return render_template('students/students.html', students=students, courses=courses)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if not can_edit_module(current_user, 'students'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    form = StudentForm()
    form.current_course.choices = [(cd.course_full_name, cd.course_full_name) for cd in CourseDetails.query.all()]
    
    # Get subjects for the selected course
    subjects = Subject.query.all()
    form.subject_1_name.choices = [('', 'Select Subject')] + [(s.subject_name, s.subject_name) for s in subjects]
    form.subject_2_name.choices = [('', 'Select Subject')] + [(s.subject_name, s.subject_name) for s in subjects]
    form.subject_3_name.choices = [('', 'Select Subject')] + [(s.subject_name, s.subject_name) for s in subjects]
    
    if form.validate_on_submit():
        # Generate student unique ID
        course_details = CourseDetails.query.filter_by(course_full_name=form.current_course.data).first()
        course_short = course_details.course_short_name if course_details else 'STD'
        student_unique_id = generate_student_id(course_short, date.today().year)
        
        student = Student(
            student_unique_id=student_unique_id,
            external_id=form.external_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            father_name=form.father_name.data,
            mother_name=form.mother_name.data,
            gender=form.gender.data,
            category=form.category.data,
            email=form.email.data,
            current_course=form.current_course.data,
            subject_1_name=form.subject_1_name.data,
            subject_2_name=form.subject_2_name.data,
            subject_3_name=form.subject_3_name.data,
            percentage=form.percentage.data,
            street=form.street.data,
            area_village=form.area_village.data,
            city_tehsil=form.city_tehsil.data,
            state=form.state.data,
            phone=form.phone.data,
            aadhaar_card_number=form.aadhaar_card_number.data,
            school_name=form.school_name.data,
            scholarship_status=form.scholarship_status.data,
            rebate_meera_scholarship_status=form.rebate_meera_scholarship_status.data,
            admission_date=form.admission_date.data
        )
        
        try:
            db.session.add(student)
            db.session.flush()  # Get student ID
            
            # Create initial fee record
            course = Course.query.filter_by(course_short_name=course_short).first()
            if course:
                fee_record = CollegeFees(
                    student_id=student.id,
                    course_id=course.course_id
                )
                db.session.add(fee_record)
            
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'error')
    
    return render_template('students/student_form.html', form=form, title='Add Student')

@app.route('/students/summary')
@login_required
def student_summary():
    # Student summary dashboard with charts
    course_counts = db.session.query(
        Student.current_course, 
        func.count(Student.id)
    ).group_by(Student.current_course).all()
    
    gender_counts = db.session.query(
        Student.gender, 
        func.count(Student.id)
    ).group_by(Student.gender).all()
    
    category_counts = db.session.query(
        Student.category, 
        func.count(Student.id)
    ).group_by(Student.category).all()
    
    monthly_admissions = db.session.query(
        func.extract('month', Student.admission_date),
        func.extract('year', Student.admission_date),
        func.count(Student.id)
    ).group_by(
        func.extract('month', Student.admission_date),
        func.extract('year', Student.admission_date)
    ).all()
    
    return render_template('students/student_summary.html', 
                         course_counts=course_counts,
                         gender_counts=gender_counts,
                         category_counts=category_counts,
                         monthly_admissions=monthly_admissions)

# Course Routes
@app.route('/courses')
@login_required
def courses():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('courses/courses.html', courses=courses)

@app.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if not can_edit_module(current_user, 'courses'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            course_short_name=form.course_short_name.data,
            course_full_name=form.course_full_name.data,
            course_category=form.course_category.data,
            duration=form.duration.data
        )
        
        try:
            db.session.add(course)
            db.session.commit()
            flash('Course added successfully!', 'success')
            return redirect(url_for('courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course: {str(e)}', 'error')
    
    return render_template('courses/course_form.html', form=form, title='Add Course')

# Fee Routes
@app.route('/fees')
@login_required
def fees():
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    fees = db.session.query(CollegeFees, Student).join(Student).paginate(page=page, per_page=20, error_out=False)
    return render_template('fees/fees.html', fees=fees)

@app.route('/fees/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    form = PaymentForm()
    form.student_id.choices = [(s.id, f"{s.student_unique_id} - {s.first_name} {s.last_name}") for s in Student.query.all()]
    
    if form.validate_on_submit():
        student = Student.query.get(form.student_id.data)
        amount = form.amount.data
        
        # Find student's fee record
        fee_record = CollegeFees.query.filter_by(student_id=student.id).first()
        if not fee_record:
            flash('No fee record found for this student.', 'error')
            return redirect(url_for('payment'))
        
        # Find next available installment slot
        installments = [
            (fee_record.installment_1, 'installment_1', 'invoice1_number'),
            (fee_record.installment_2, 'installment_2', 'invoice2_number'),
            (fee_record.installment_3, 'installment_3', 'invoice3_number'),
            (fee_record.installment_4, 'installment_4', 'invoice4_number'),
            (fee_record.installment_5, 'installment_5', 'invoice5_number'),
            (fee_record.installment_6, 'installment_6', 'invoice6_number'),
        ]
        
        next_slot = None
        for i, (value, field, invoice_field) in enumerate(installments):
            if value == 0:
                next_slot = (i + 1, field, invoice_field)
                break
        
        if not next_slot:
            flash('All installment slots are filled for this student.', 'error')
            return redirect(url_for('payment'))
        
        # Generate invoice
        invoice_number = generate_invoice_number()
        invoice = Invoice(
            student_id=student.id,
            course_id=fee_record.course_id,
            invoice_number=invoice_number,
            invoice_amount=amount,
            installment_number=next_slot[0]
        )
        
        # Update fee record
        setattr(fee_record, next_slot[1], amount)
        setattr(fee_record, next_slot[2], invoice_number)
        
        try:
            db.session.add(invoice)
            db.session.commit()
            flash('Payment processed successfully!', 'success')
            return redirect(url_for('fees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing payment: {str(e)}', 'error')
    
    return render_template('fees/payment_form.html', form=form, title='Process Payment')

# Exam Routes
@app.route('/exams')
@login_required
def exams():
    if not can_edit_module(current_user, 'exams'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    exams = db.session.query(Exam, Student).join(Student).paginate(page=page, per_page=20, error_out=False)
    return render_template('exams/exams.html', exams=exams)

@app.route('/exams/add', methods=['GET', 'POST'])
@login_required
def add_exam():
    if not can_edit_module(current_user, 'exams'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    form = ExamForm()
    form.student_id.choices = [(s.id, f"{s.student_unique_id} - {s.first_name} {s.last_name}") for s in Student.query.all()]
    form.course_id.choices = [(c.course_id, c.course_full_name) for c in Course.query.all()]
    
    if form.validate_on_submit():
        # Calculate totals and grade
        subjects_data = [
            (form.subject1_name.data, form.subject1_max_marks.data, form.subject1_obtained_marks.data),
            (form.subject2_name.data, form.subject2_max_marks.data, form.subject2_obtained_marks.data),
            (form.subject3_name.data, form.subject3_max_marks.data, form.subject3_obtained_marks.data),
        ]
        
        total_max = sum(max_marks for name, max_marks, obtained in subjects_data if name)
        total_obtained = sum(obtained for name, max_marks, obtained in subjects_data if name)
        percentage = (total_obtained / total_max * 100) if total_max > 0 else 0
        grade = calculate_grade(percentage)
        status = 'Pass' if percentage >= 40 else 'Fail'
        
        exam = Exam(
            student_id=form.student_id.data,
            course_id=form.course_id.data,
            semester=form.semester.data,
            exam_name=form.exam_name.data,
            exam_date=form.exam_date.data,
            subject1_name=form.subject1_name.data,
            subject1_max_marks=form.subject1_max_marks.data,
            subject1_obtained_marks=form.subject1_obtained_marks.data,
            subject2_name=form.subject2_name.data,
            subject2_max_marks=form.subject2_max_marks.data,
            subject2_obtained_marks=form.subject2_obtained_marks.data,
            subject3_name=form.subject3_name.data,
            subject3_max_marks=form.subject3_max_marks.data,
            subject3_obtained_marks=form.subject3_obtained_marks.data,
            total_max_marks=total_max,
            total_obtained_marks=total_obtained,
            percentage=percentage,
            grade=grade,
            overall_status=status
        )
        
        try:
            db.session.add(exam)
            db.session.commit()
            flash('Exam results saved successfully!', 'success')
            return redirect(url_for('exams'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving exam results: {str(e)}', 'error')
    
    return render_template('exams/exam_form.html', form=form, title='Add Exam Results')

# Analytics Routes
@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics/analytics.html')

# API Routes for charts
@app.route('/api/student-stats')
@login_required
def api_student_stats():
    course_counts = db.session.query(
        Student.current_course, 
        func.count(Student.id)
    ).group_by(Student.current_course).all()
    
    return jsonify({
        'courses': [course for course, count in course_counts],
        'counts': [count for course, count in course_counts]
    })

@app.route('/api/fee-stats')
@login_required
def api_fee_stats():
    monthly_collections = db.session.query(
        func.extract('month', Invoice.date_time),
        func.sum(Invoice.invoice_amount)
    ).group_by(func.extract('month', Invoice.date_time)).all()
    
    return jsonify({
        'months': [int(month) for month, amount in monthly_collections],
        'amounts': [float(amount) for month, amount in monthly_collections]
    })

# Export Routes
@app.route('/export/students')
@login_required
def export_students():
    students = Student.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Student ID', 'Name', 'Course', 'Gender', 'Category', 'Email', 'Phone', 'Status'])
    
    # Data
    for student in students:
        writer.writerow([
            student.student_unique_id,
            f"{student.first_name} {student.last_name}",
            student.current_course,
            student.gender,
            student.category,
            student.email,
            student.phone,
            student.dropout_status
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=students_export.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response

# PDF Generation Routes
@app.route('/invoice/<int:invoice_id>/pdf')
@login_required
def invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    pdf_data = generate_pdf_invoice(invoice)
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
    
    return response

@app.route('/report-card/<int:exam_id>/pdf')
@login_required
def report_card_pdf(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    pdf_data = generate_pdf_report_card(exam)
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=report_card_{exam.student.student_unique_id}.pdf'
    
    return response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
