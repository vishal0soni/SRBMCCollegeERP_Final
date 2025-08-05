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
from utils import generate_student_id, generate_invoice_number, calculate_grade, can_edit_module, send_email, generate_pdf_invoice, generate_pdf_report_card, generate_pdf_student_report, generate_pdf_fee_statement, generate_pdf_fee_statement_print
from bulk_operations import (
    get_students_export_data, get_courses_export_data, get_course_details_export_data,
    get_exams_export_data, get_fees_export_data, get_invoices_export_data, get_users_export_data,
    get_subjects_export_data, export_to_csv, export_to_excel, export_to_json, process_import_file
)

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
    total_students = Student.query.count()
    active_students = Student.query.filter_by(dropout_status='Active').count()

    # Calculate total collected fees from all installments
    total_collected_fees = db.session.query(
        func.sum(
            (CollegeFees.installment_1 or 0) + 
            (CollegeFees.installment_2 or 0) + 
            (CollegeFees.installment_3 or 0) + 
            (CollegeFees.installment_4 or 0) + 
            (CollegeFees.installment_5 or 0) + 
            (CollegeFees.installment_6 or 0)
        )
    ).scalar() or 0

    # Calculate pending fees (total fees - collected fees)
    pending_fees = db.session.query(
        func.sum(
            (CollegeFees.total_fee or 0) - 
            ((CollegeFees.installment_1 or 0) + 
             (CollegeFees.installment_2 or 0) + 
             (CollegeFees.installment_3 or 0) + 
             (CollegeFees.installment_4 or 0) + 
             (CollegeFees.installment_5 or 0) + 
             (CollegeFees.installment_6 or 0))
        )
    ).scalar() or 0

    # Ensure pending fees is not negative
    pending_fees = max(0, pending_fees)

    stats = {
        'total_students': total_students,
        'active_students': active_students,
        'total_collected_fees': total_collected_fees,
        'pending_fees': pending_fees
    }

    # Recent activities - get dynamic data
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
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')

    query = UserProfile.query.join(UserRole)

    # Search filters
    if search:
        search_filter = or_(
            UserProfile.first_name.contains(search),
            UserProfile.last_name.contains(search),
            UserProfile.username.contains(search),
            UserProfile.email.contains(search)
        )
        query = query.filter(search_filter)

    if role_filter:
        query = query.filter(UserProfile.role_id == role_filter)

    # Default ordering by first name
    query = query.order_by(UserProfile.first_name)

    users = query.paginate(page=page, per_page=20, error_out=False)
    roles = UserRole.query.all()

    return render_template('admin/users.html', users=users, roles=roles)

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

@app.route('/admin/users/delete/<int:user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    if not can_edit_module(current_user, 'admin'):
        return jsonify({'error': 'Permission denied'}), 403

    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400

    user = UserProfile.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
    sort_by = request.args.get('sort', 'first_name')
    sort_order = request.args.get('order', 'asc')

    query = Student.query

    if course_filter:
        query = query.filter(Student.current_course.contains(course_filter))
    if gender_filter:
        query = query.filter_by(gender=gender_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if status_filter:
        query = query.filter_by(dropout_status=status_filter)

    # Sorting
    if hasattr(Student, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Student, sort_by).desc())
        else:
            query = query.order_by(getattr(Student, sort_by))

    students = query.paginate(page=page, per_page=20, error_out=False)

    # Get filter options
    courses = db.session.query(Student.current_course).distinct().filter(Student.current_course != None).all()
    courses = [course[0] for course in courses]

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
        if not course_details:
            flash('Course details not found. Please select a valid course.', 'error')
            return render_template('students/student_form.html', form=form, title='Add Student')

        course_short = course_details.course_short_name
        student_unique_id = generate_student_id(course_short, date.today().year)

        # Double-check for uniqueness (safety measure)
        existing_student = Student.query.filter_by(student_unique_id=student_unique_id).first()
        counter = 1
        base_id = student_unique_id
        while existing_student:
            # If somehow we still have a duplicate, increment until unique
            year_short = str(date.today().year)[-2:]
            counter += 1
            student_unique_id = f"{course_short}-{year_short}-{counter:03d}"
            existing_student = Student.query.filter_by(student_unique_id=student_unique_id).first()

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
            apaar_id=form.apaar_id.data,
            school_name=form.school_name.data,
            scholarship_status=form.scholarship_status.data,
            rebate_meera_scholarship_status=form.rebate_meera_scholarship_status.data,
            admission_date=form.admission_date.data
        )

        try:
            db.session.add(student)
            db.session.flush()  # This will assign the auto-generated ID

            # Create initial fee record with course details sync
            course = Course.query.filter_by(course_short_name=course_short).first()
            course_detail = CourseDetails.query.filter_by(course_full_name=form.current_course.data).first()

            if course and course_detail:
                # Get fee data from form (submitted via JavaScript)
                course_tuition_fee = float(request.form.get('fee_course_tuition_fee', course_detail.total_course_fees) or 0)
                enrollment_fee = float(request.form.get('fee_enrollment_fee', 0) or 0)
                eligibility_certificate_fee = float(request.form.get('fee_eligibility_certificate_fee', 0) or 0)
                university_affiliation_fee = float(request.form.get('fee_university_affiliation_fee', 0) or 0)
                university_sports_fee = float(request.form.get('fee_university_sports_fee', 0) or 0)
                university_development_fee = float(request.form.get('fee_university_development_fee', 0) or 0)
                tc_cc_fee = float(request.form.get('fee_tc_cc_fee', 0) or 0)
                miscellaneous_fee_1 = float(request.form.get('fee_miscellaneous_fee_1', 0) or 0)
                miscellaneous_fee_2 = float(request.form.get('fee_miscellaneous_fee_2', 0) or 0)
                miscellaneous_fee_3 = float(request.form.get('fee_miscellaneous_fee_3', 0) or 0)
                total_fee = float(request.form.get('fee_total_fee', course_detail.total_course_fees) or 0)

                # Get new fee management fields from form
                total_fees_paid = float(request.form.get('fee_total_fees_paid', 0) or 0)
                meera_rebate_applied = request.form.get('fee_meera_rebate_applied') == 'true'
                meera_rebate_approved = request.form.get('fee_meera_rebate_approved') == 'true'
                meera_rebate_granted = request.form.get('fee_meera_rebate_granted') == 'true'
                meera_rebate_amount = float(request.form.get('fee_meera_rebate_amount', 0) or 0)
                scholarship_applied = request.form.get('fee_scholarship_applied') == 'true'
                scholarship_approved = request.form.get('fee_scholarship_approved') == 'true'
                scholarship_granted = request.form.get('fee_scholarship_granted') == 'true'
                government_scholarship_amount = float(request.form.get('fee_government_scholarship_amount', 0) or 0)
                total_amount_due = float(request.form.get('fee_total_amount_due', 0) or 0)
                pending_dues_for_libraries = request.form.get('fee_pending_dues_for_libraries') == 'true'
                pending_dues_for_hostel = request.form.get('fee_pending_dues_for_hostel') == 'true'
                exam_admit_card_issued = request.form.get('fee_exam_admit_card_issued') == 'true'

                fee_record = CollegeFees(
                    student_id=student.id,
                    course_id=course.course_id,
                    course_tuition_fee=course_tuition_fee,
                    enrollment_fee=enrollment_fee,
                    eligibility_certificate_fee=eligibility_certificate_fee,
                    university_affiliation_fee=university_affiliation_fee,
                    university_sports_fee=university_sports_fee,
                    university_development_fee=university_development_fee,
                    tc_cc_fee=tc_cc_fee,
                    miscellaneous_fee_1=miscellaneous_fee_1,
                    miscellaneous_fee_2=miscellaneous_fee_2,
                    miscellaneous_fee_3=miscellaneous_fee_3,
                    total_fee=total_fee,
                    # New fee management fields
                    total_fees_paid=total_fees_paid,
                    meera_rebate_applied=meera_rebate_applied,
                    meera_rebate_approved=meera_rebate_approved,
                    meera_rebate_granted=meera_rebate_granted,
                    meera_rebate_amount=meera_rebate_amount,
                    scholarship_applied=scholarship_applied,
                    scholarship_approved=scholarship_approved,
                    scholarship_granted=scholarship_granted,
                    government_scholarship_amount=government_scholarship_amount,
                    total_amount_due=total_amount_due,
                    pending_dues_for_libraries=pending_dues_for_libraries,
                    pending_dues_for_hostel=pending_dues_for_hostel,
                    exam_admit_card_issued=exam_admit_card_issued
                )
                db.session.add(fee_record)

            db.session.commit()
            flash('Student added successfully with fee record!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'error')

    return render_template('students/student_form.html', form=form, title='Add Student', today_date=date.today().strftime('%Y-%m-%d'))

@app.route('/students/summary')
@login_required
def student_summary():
    # Student summary dashboard with charts
    course_counts = db.session.query(
        Student.current_course, 
        func.count(Student.id)
    ).filter(Student.current_course != None).group_by(Student.current_course).all()

    gender_counts = db.session.query(
        Student.gender, 
        func.count(Student.id)
    ).filter(Student.gender != None).group_by(Student.gender).all()

    category_counts = db.session.query(
        Student.category, 
        func.count(Student.id)
    ).filter(Student.category != None).group_by(Student.category).all()

    monthly_admissions = db.session.query(
        func.extract('month', Student.admission_date),
        func.extract('year', Student.admission_date),
        func.count(Student.id)
    ).filter(Student.admission_date != None).group_by(
        func.extract('month', Student.admission_date),
        func.extract('year', Student.admission_date)
    ).order_by(
        func.extract('year', Student.admission_date),
        func.extract('month', Student.admission_date)
    ).all()

    # Provide default empty data if no students exist
    if not course_counts:
        course_counts = []
    if not gender_counts:
        gender_counts = []
    if not category_counts:
        category_counts = []
    if not monthly_admissions:
        monthly_admissions = []

    return render_template('students/student_summary.html', 
                         course_counts=course_counts,
                         gender_counts=gender_counts,
                         category_counts=category_counts,
                         monthly_admissions=monthly_admissions)

# CourseDetails Routes
@app.route('/course-details')
@login_required
def course_details():
    if not can_edit_module(current_user, 'courses'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    course_filter = request.args.get('course', '')

    query = CourseDetails.query

    # Search filters
    if search:
        search_filter = or_(
            CourseDetails.course_full_name.contains(search),
            CourseDetails.course_short_name.contains(search),
            CourseDetails.year_semester.contains(search)
        )
        query = query.filter(search_filter)

    if course_filter:
        query = query.filter(CourseDetails.course_short_name == course_filter)

    course_details = query.paginate(page=page, per_page=20, error_out=False)
    courses = Course.query.all()

    return render_template('courses/course_details.html', course_details=course_details, courses=courses)

@app.route('/course-details/add', methods=['GET', 'POST'])
@login_required
def add_course_details():
    if not can_edit_module(current_user, 'courses'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    form = CourseDetailsForm()
    form.course_short_name.choices = [(c.course_short_name, f"{c.course_short_name} - {c.course_full_name}") for c in Course.query.all()]

    if form.validate_on_submit():
        # Calculate total course fees
        total_fees = (form.course_tuition_fee.data + form.misc_course_fees_1.data + 
                     form.misc_course_fees_2.data + form.misc_course_fees_3.data + 
                     form.misc_course_fees_4.data + form.misc_course_fees_5.data + 
                     form.misc_course_fees_6.data)

        course_detail = CourseDetails(
            course_full_name=form.course_full_name.data,
            course_short_name=form.course_short_name.data,
            year_semester=form.year_semester.data,
            course_tuition_fee=form.course_tuition_fee.data,
            course_type=form.course_type.data,
            misc_course_fees_1=form.misc_course_fees_1.data,
            misc_course_fees_2=form.misc_course_fees_2.data,
            misc_course_fees_3=form.misc_course_fees_3.data,
            misc_course_fees_4=form.misc_course_fees_4.data,
            misc_course_fees_5=form.misc_course_fees_5.data,
            misc_course_fees_6=form.misc_course_fees_6.data,
            total_course_fees=total_fees
        )

        try:
            db.session.add(course_detail)

            # Check if course exists, if not create it
            course = Course.query.filter_by(course_short_name=form.course_short_name.data).first()
            if not course:
                course = Course(
                    course_short_name=form.course_short_name.data,
                    course_full_name=form.course_full_name.data,
                    course_category='General',
                    duration=3  # Default duration
                )
                db.session.add(course)

            # Update existing fee records for this course
            if course:
                existing_fees = CollegeFees.query.filter_by(course_id=course.course_id).all()
                for fee_record in existing_fees:
                    fee_record.course_tuition_fee = total_fees
                    fee_record.total_fee = total_fees

            db.session.commit()
            flash('Course details added successfully!', 'success')
            return redirect(url_for('course_details'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course details: {str(e)}', 'error')

    return render_template('courses/course_details_form.html', form=form, title='Add Course Details')

@app.route('/course-details/edit/<int:detail_id>', methods=['GET', 'POST'])
@login_required
def edit_course_details(detail_id):
    if not can_edit_module(current_user, 'courses') or current_user.role.access_type != 'Edit':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    course_detail = CourseDetails.query.get_or_404(detail_id)
    form = CourseDetailsForm(obj=course_detail)
    form.course_short_name.choices = [(c.course_short_name, f"{c.course_short_name} - {c.course_full_name}") for c in Course.query.all()]

    if form.validate_on_submit():
        # Calculate total course fees
        total_fees = (form.course_tuition_fee.data + form.misc_course_fees_1.data + 
                     form.misc_course_fees_2.data + form.misc_course_fees_3.data + 
                     form.misc_course_fees_4.data + form.misc_course_fees_5.data + 
                     form.misc_course_fees_6.data)

        form.populate_obj(course_detail)
        course_detail.total_course_fees = total_fees

        try:
            db.session.commit()
            flash('Course details updated successfully!', 'success')
            return redirect(url_for('course_details'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course details: {str(e)}', 'error')

    return render_template('courses/course_details_form.html', form=form, title='Edit Course Details', course_detail=course_detail)

@app.route('/course-details/delete/<int:detail_id>', methods=['DELETE'])
@login_required
def delete_course_details(detail_id):
    if not can_edit_module(current_user, 'courses') or current_user.role.access_type != 'Edit':
        return jsonify({'error': 'Permission denied'}), 403

    course_detail = CourseDetails.query.get_or_404(detail_id)

    try:
        db.session.delete(course_detail)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Course Routes
@app.route('/courses')
@login_required
def courses():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    sort_by = request.args.get('sort', 'course_full_name')
    sort_order = request.args.get('order', 'asc')

    query = Course.query

    # Search filters
    if search:
        search_filter = or_(
            Course.course_short_name.contains(search),
            Course.course_full_name.contains(search)
        )
        query = query.filter(search_filter)

    if category_filter:
        query = query.filter(Course.course_category == category_filter)

    # Sorting
    if hasattr(Course, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Course, sort_by).desc())
        else:
            query = query.order_by(getattr(Course, sort_by))

    courses = query.paginate(page=page, per_page=20, error_out=False)

    # Get unique categories for filter
    categories = db.session.query(Course.course_category).distinct().filter(Course.course_category != None).all()
    categories = [cat[0] for cat in categories]

    return render_template('courses/courses.html', courses=courses, categories=categories)

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
            duration=int(form.duration.data) if form.duration.data else 3
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

@app.route('/courses/view/<int:course_id>')
@login_required
def view_course(course_id):
    if not can_edit_module(current_user, 'courses'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    course = Course.query.get_or_404(course_id)
    return render_template('courses/course_detail.html', course=course)

@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if not can_edit_module(current_user, 'courses') or current_user.role.access_type != 'Edit':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)

    if form.validate_on_submit():
        course.course_short_name = form.course_short_name.data
        course.course_full_name = form.course_full_name.data
        course.course_category = form.course_category.data
        course.duration = int(form.duration.data) if form.duration.data else course.duration

        try:
            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {str(e)}', 'error')

    return render_template('courses/course_form.html', form=form, title='Edit Course', course=course)

@app.route('/courses/delete/<int:course_id>', methods=['DELETE'])
@login_required
def delete_course(course_id):
    if not can_edit_module(current_user, 'courses') or current_user.role.access_type != 'Edit':
        return jsonify({'error': 'Permission denied'}), 403

    course = Course.query.get_or_404(course_id)

    try:
        # Delete related subjects first
        Subject.query.filter_by(course_short_name=course.course_short_name).delete()

        # Delete course details
        CourseDetails.query.filter_by(course_short_name=course.course_short_name).delete()

        # Delete the course
        db.session.delete(course)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Fee Routes
@app.route('/fees')
@login_required
def fees():
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    course_filter = request.args.get('course', '')
    payment_status_filter = request.args.get('payment_status', '')
    scholarship_filter = request.args.get('scholarship', '')
    sort_by = request.args.get('sort', 'student_unique_id')
    sort_order = request.args.get('order', 'asc')

    query = db.session.query(CollegeFees, Student).join(Student)

    # Search filters
    if search:
        search_filter = or_(
            Student.first_name.contains(search),
            Student.last_name.contains(search),
            Student.student_unique_id.contains(search),
            Student.current_course.contains(search)
        )
        query = query.filter(search_filter)

    if course_filter:
        query = query.filter(Student.current_course.contains(course_filter))

    if scholarship_filter:
        query = query.filter(Student.scholarship_status == scholarship_filter)

    # Payment status filtering
    if payment_status_filter:
        if payment_status_filter == 'paid':
            query = query.filter(
                (CollegeFees.installment_1 + CollegeFees.installment_2 + CollegeFees.installment_3 + 
                 CollegeFees.installment_4 + CollegeFees.installment_5 + CollegeFees.installment_6) >= CollegeFees.total_fee
            )
        elif payment_status_filter == 'pending':
            query = query.filter(
                (CollegeFees.installment_1 + CollegeFees.installment_2 + CollegeFees.installment_3 + 
                 CollegeFees.installment_4 + CollegeFees.installment_5 + CollegeFees.installment_6) == 0
            )
        elif payment_status_filter == 'partial':
            query = query.filter(
                and_(
                    (CollegeFees.installment_1 + CollegeFees.installment_2 + CollegeFees.installment_3 + 
                     CollegeFees.installment_4 + CollegeFees.installment_5 + CollegeFees.installment_6) > 0,
                    (CollegeFees.installment_1 + CollegeFees.installment_2 + CollegeFees.installment_3 + 
                     CollegeFees.installment_4 + CollegeFees.installment_5 + CollegeFees.installment_6) < CollegeFees.total_fee
                )
            )

    # Sorting
    if hasattr(Student, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Student, sort_by).desc())
        else:
            query = query.order_by(getattr(Student, sort_by))
    elif hasattr(CollegeFees, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(CollegeFees, sort_by).desc())
        else:
            query = query.order_by(getattr(CollegeFees, sort_by))

    fees = query.paginate(page=page, per_page=20, error_out=False)

    # Get unique courses for filter
    courses = db.session.query(Student.current_course).distinct().filter(Student.current_course != None).all()
    courses = [course[0] for course in courses]

    return render_template('fees/fees.html', fees=fees, courses=courses)

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
    search = request.args.get('search', '')
    course_filter = request.args.get('course', '')
    semester_filter = request.args.get('semester', '')
    result_filter = request.args.get('result', '')
    sort_by = request.args.get('sort', 'exam_name')
    sort_order = request.args.get('order', 'asc')

    query = db.session.query(Exam, Student).join(Student)

    # Search filters
    if search:
        search_filter = or_(
            Student.first_name.contains(search),
            Student.last_name.contains(search),
            Student.student_unique_id.contains(search),
            Exam.exam_name.contains(search),
            Student.current_course.contains(search)
        )
        query = query.filter(search_filter)

    if course_filter:
        query = query.filter(Student.current_course.contains(course_filter))

    if semester_filter:
        query = query.filter(Exam.semester == semester_filter)

    if result_filter:
        query = query.filter(Exam.overall_status == result_filter)

    # Sorting
    if hasattr(Exam, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Exam, sort_by).desc())
        else:
            query = query.order_by(getattr(Exam, sort_by))
    elif hasattr(Student, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Student, sort_by).desc())
        else:
            query = query.order_by(getattr(Student, sort_by))

    exams = query.paginate(page=page, per_page=20, error_out=False)

    # Get filter options
    courses = db.session.query(Student.current_course).distinct().filter(Student.current_course != None).all()
    courses = [course[0] for course in courses]

    semesters = db.session.query(Exam.semester).distinct().filter(Exam.semester != None).all()
    semesters = [sem[0] for sem in semesters]

    return render_template('exams/exams.html', exams=exams, courses=courses, semesters=semesters)

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

@app.route('/exams/view/<int:exam_id>')
@login_required
def view_exam(exam_id):
    if not can_edit_module(current_user, 'exams'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    exam = Exam.query.get_or_404(exam_id)
    return render_template('exams/exam_detail.html', exam=exam)

@app.route('/exams/edit/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def edit_exam(exam_id):
    if not can_edit_module(current_user, 'exams') or current_user.role.access_type != 'Edit':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    exam = Exam.query.get_or_404(exam_id)
    form = ExamForm(obj=exam)
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

        exam.student_id = form.student_id.data
        exam.course_id = form.course_id.data
        exam.semester = form.semester.data
        exam.exam_name = form.exam_name.data
        exam.subject1_name = form.subject1_name.data
        exam.subject1_max_marks = form.subject1_max_marks.data
        exam.subject1_obtained_marks = form.subject1_obtained_marks.data
        exam.subject2_name = form.subject2_name.data
        exam.subject2_max_marks = form.subject2_max_marks.data
        exam.subject2_obtained_marks = form.subject2_obtained_marks.data
        exam.subject3_name = form.subject3_name.data
        exam.subject3_max_marks = form.subject3_max_marks.data
        exam.subject3_obtained_marks = form.subject3_obtained_marks.data
        exam.total_max_marks = total_max
        exam.total_obtained_marks = total_obtained
        exam.percentage = percentage
        exam.grade = grade
        exam.overall_status = status

        try:
            db.session.commit()
            flash('Exam results updated successfully!', 'success')
            return redirect(url_for('exams'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating exam results: {str(e)}', 'error')

    return render_template('exams/exam_form.html', form=form, title='Edit Exam Results', exam=exam)

@app.route('/students/promote/<int:student_id>', methods=['POST'])
@login_required
def promote_student(student_id):
    if not can_edit_module(current_user, 'exams') or current_user.role.access_type != 'Edit':
        return jsonify({'error': 'Permission denied'}), 403

    student = Student.query.get_or_404(student_id)

    try:
        # Create new fee record for next class
        course = Course.query.filter_by(course_full_name=student.current_course).first()
        if course:
            fee_record = CollegeFees(
                student_id=student.id,
                course_id=course.course_id
            )
            db.session.add(fee_record)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Student promoted successfully! New fee record created.'})
        else:
            return jsonify({'error': 'Course not found'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Analytics Routes
@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics/analytics.html')

# API Routes for AJAX calls
@app.route('/api/subjects/<course_name>')
@login_required
def api_get_subjects(course_name):
    try:
        # Extract course short name from full name
        course_detail = CourseDetails.query.filter_by(course_full_name=course_name).first()
        if course_detail:
            subjects = Subject.query.filter_by(course_short_name=course_detail.course_short_name).all()
            subject_list = [{'name': s.subject_name, 'type': s.subject_type} for s in subjects]
            return jsonify({'success': True, 'subjects': subject_list})
        else:
            return jsonify({'success': False, 'subjects': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'subjects': []})

@app.route('/api/course-fees/<course_name>')
@login_required
def api_get_course_fees(course_name):
    try:
        course_detail = CourseDetails.query.filter_by(course_full_name=course_name).first()
        if course_detail:
            fees_data = {
                'course_tuition_fee': float(course_detail.course_tuition_fee or 0),
                'misc_course_fees_1': float(course_detail.misc_course_fees_1 or 0),
                'misc_course_fees_2': float(course_detail.misc_course_fees_2 or 0),
                'misc_course_fees_3': float(course_detail.misc_course_fees_3 or 0),
                'misc_course_fees_4': float(course_detail.misc_course_fees_4 or 0),
                'misc_course_fees_5': float(course_detail.misc_course_fees_5 or 0),
                'misc_course_fees_6': float(course_detail.misc_course_fees_6 or 0),
                'total_course_fees': float(course_detail.total_course_fees or 0)
            }
            return jsonify({'success': True, 'fees': fees_data})
        else:
            return jsonify({'success': False, 'fees': None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'fees': None})

# API Routes for charts
@app.route('/api/student-stats')
@login_required
def api_student_stats():
    try:
        query = Student.query
        
        # Apply filters based on query parameters
        course_filter = request.args.get('course', '')
        status_filter = request.args.get('status', '')
        gender_filter = request.args.get('gender', '')
        
        if course_filter:
            query = query.filter(Student.current_course == course_filter)
        if status_filter:
            query = query.filter(Student.dropout_status == status_filter)
        if gender_filter:
            query = query.filter(Student.gender == gender_filter)
        
        # Get course distribution
        course_counts = query.with_entities(
            Student.current_course, 
            func.count(Student.id)
        ).filter(Student.current_course.isnot(None)).group_by(Student.current_course).all()

        # Handle case where no data exists
        if not course_counts:
            return jsonify({
                'courses': ['No Data Available'],
                'counts': [0]
            })

        return jsonify({
            'courses': [course or 'Not Assigned' for course, count in course_counts],
            'counts': [int(count) for course, count in course_counts]
        })
    except Exception as e:
        print(f"Error in api_student_stats: {e}")
        return jsonify({
            'courses': ['Error Loading Data'],
            'counts': [0]
        })

@app.route('/api/course-list')
@login_required
def api_course_list():
    try:
        courses = db.session.query(Student.current_course).distinct().filter(
            Student.current_course.isnot(None)
        ).all()
        course_list = [course[0] for course in courses if course[0]]
        return jsonify({'courses': sorted(course_list)})
    except Exception as e:
        print(f"Error in api_course_list: {e}")
        return jsonify({'courses': []})

@app.route('/api/fee-stats')
@login_required
def api_fee_stats():
    try:
        # Get monthly fee collections from invoices for current year
        current_year = datetime.now().year
        monthly_collections = db.session.query(
            func.extract('month', Invoice.date_time),
            func.sum(Invoice.invoice_amount)
        ).filter(
            func.extract('year', Invoice.date_time) == current_year
        ).group_by(func.extract('month', Invoice.date_time)).order_by(func.extract('month', Invoice.date_time)).all()

        # Initialize all 12 months with 0
        months_data = {i: 0 for i in range(1, 13)}

        # Fill in actual data
        for month, amount in monthly_collections:
            if month and amount:
                months_data[int(month)] = float(amount)

        return jsonify({
            'months': list(months_data.keys()),
            'amounts': list(months_data.values())
        })
    except Exception as e:
        print(f"Error in api_fee_stats: {e}")
        # Return default data for current year
        return jsonify({
            'months': list(range(1, 13)),
            'amounts': [0] * 12
        })

@app.route('/api/search-students')
@login_required
def api_search_students():
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return jsonify({'success': False, 'students': []})

    try:
        # Search students by name or ID
        search_filter = or_(
            Student.first_name.ilike(f'%{query}%'),
            Student.last_name.ilike(f'%{query}%'),
            Student.student_unique_id.ilike(f'%{query}%'),
            func.concat(Student.first_name, ' ', Student.last_name).ilike(f'%{query}%')
        )

        students = Student.query.filter(search_filter).limit(10).all()

        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'student_unique_id': student.student_unique_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'current_course': student.current_course or 'No Course Assigned'
            })

        return jsonify({'success': True, 'students': students_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'students': []})

@app.route('/api/student-fee-details/<int:student_id>')
@login_required
def api_student_fee_details(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        fee_record = CollegeFees.query.filter_by(student_id=student_id).first()

        if not fee_record:
            return jsonify({
                'success': True,
                'fee_data': {
                    'total_fee': 0,
                    'paid_amount': 0,
                    'due_amount': 0,
                    'next_installment': 1
                },
                'payment_history': []
            })

        # Calculate paid amount and next installment
        installments = [
            fee_record.installment_1 or 0,
            fee_record.installment_2 or 0,
            fee_record.installment_3 or 0,
            fee_record.installment_4 or 0,
            fee_record.installment_5 or 0,
            fee_record.installment_6 or 0
        ]

        paid_amount = sum(installments)
        next_installment = 1

        # Find next available installment
        for i, amount in enumerate(installments):
            if amount == 0:
                next_installment = i + 1
                break
        else:
            next_installment = 7  # All installments paid

        total_fee = fee_record.total_fee or 0
        due_amount = total_fee - paid_amount

        # Get payment history
        invoices = Invoice.query.filter_by(student_id=student_id).order_by(Invoice.date_time.desc()).limit(5).all()
        payment_history = []
        for invoice in invoices:
            payment_history.append({
                'invoice_number': invoice.invoice_number,
                'amount': float(invoice.invoice_amount),
                'date': invoice.date_time.strftime('%Y-%m-%d'),
                'installment_number': invoice.installment_number
            })

        return jsonify({
            'success': True,
            'fee_data': {
                'total_fee': float(total_fee),
                'paid_amount': float(paid_amount),
                'due_amount': float(due_amount),
                'next_installment': next_installment,
                # New fee management fields
                'total_fees_paid': float(fee_record.total_fees_paid or 0),
                'meera_rebate_applied': fee_record.meera_rebate_applied or False,
                'meera_rebate_approved': fee_record.meera_rebate_approved or False,
                'meera_rebate_granted': fee_record.meera_rebate_granted or False,
                'meera_rebate_amount': float(fee_record.meera_rebate_amount or 0),
                'scholarship_applied': fee_record.scholarship_applied or False,
                'scholarship_approved': fee_record.scholarship_approved or False,
                'scholarship_granted': fee_record.scholarship_granted or False,
                'government_scholarship_amount': float(fee_record.government_scholarship_amount or 0),
                'total_amount_due': float(fee_record.total_amount_due or 0),
                'pending_dues_for_libraries': fee_record.pending_dues_for_libraries or False,
                'pending_dues_for_hostel': fee_record.pending_dues_for_hostel or False,
                'exam_admit_card_issued': fee_record.exam_admit_card_issued or False,
                # Existing fee structure fields
                'course_tuition_fee': float(fee_record.course_tuition_fee or 0),
                'enrollment_fee': float(fee_record.enrollment_fee or 0),
                'eligibility_certificate_fee': float(fee_record.eligibility_certificate_fee or 0),
                'university_affiliation_fee': float(fee_record.university_affiliation_fee or 0),
                'university_sports_fee': float(fee_record.university_sports_fee or 0),
                'university_development_fee': float(fee_record.university_development_fee or 0),
                'tc_cc_fee': float(fee_record.tc_cc_fee or 0),
                'miscellaneous_fee_1': float(fee_record.miscellaneous_fee_1 or 0),
                'miscellaneous_fee_2': float(fee_record.miscellaneous_fee_2 or 0),
                'miscellaneous_fee_3': float(fee_record.miscellaneous_fee_3 or 0)
            },
            'payment_history': payment_history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Subject Routes
@app.route('/courses/<int:course_id>/subjects')
@login_required
def course_subjects(course_id):
    if not can_edit_module(current_user, 'courses'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    course = Course.query.get_or_404(course_id)
    subjects = Subject.query.filter_by(course_short_name=course.course_short_name).all()
    return render_template('courses/subjects.html', course=course, subjects=subjects)

@app.route('/courses/<int:course_id>/subjects/add', methods=['GET', 'POST'])
@login_required
def add_subject(course_id):
    if not can_edit_module(current_user, 'courses'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    course = Course.query.get_or_404(course_id)
    form = SubjectForm()
    form.course_short_name.data = course.course_short_name
    form.course_short_name.choices = [(course.course_short_name, course.course_full_name)]

    if form.validate_on_submit():
        subject = Subject(
            course_short_name=form.course_short_name.data,
            subject_name=form.subject_name.data,
            subject_type=form.subject_type.data
        )

        try:
            db.session.add(subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('course_subjects', course_id=course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding subject: {str(e)}', 'error')

    return render_template('courses/subject_form.html', form=form, title='Add Subject', course=course)

@app.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if not can_edit_module(current_user, 'courses') or current_user.role.access_type != 'Edit':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    subject = Subject.query.get_or_404(subject_id)
    course = Course.query.filter_by(course_short_name=subject.course_short_name).first()
    form = SubjectForm(obj=subject)
    form.course_short_name.choices = [(course.course_short_name, course.course_full_name)]

    if form.validate_on_submit():
        form.populate_obj(subject)

        try:
            db.session.commit()
            flash('Subject updated successfully!', 'success')
            return redirect(url_for('course_subjects', course_id=course.course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating subject: {str(e)}', 'error')

    return render_template('courses/subject_form.html', form=form, title='Edit Subject', course=course, subject=subject)

@app.route('/subjects/delete/<int:subject_id>', methods=['DELETE'])
@login_required
def delete_subject(subject_id):
    if not can_edit_module(current_user, 'courses') or current_user.role.access_type != 'Edit':
        return jsonify({'error': 'Permission denied'}), 403

    subject = Subject.query.get_or_404(subject_id)

    try:
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/invoices')
@login_required
def invoices():
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = db.session.query(Invoice, Student).join(Student)

    # Search filters
    if search:
        search_filter = or_(
            Invoice.invoice_number.contains(search),
            Student.first_name.contains(search),
            Student.last_name.contains(search),
            Student.student_unique_id.contains(search)
        )
        query = query.filter(search_filter)

    # Date filters
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(func.date(Invoice.date_time) >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(func.date(Invoice.date_time) <= to_date)
        except ValueError:
            pass

    # Order by most recent first
    query = query.order_by(Invoice.date_time.desc())

    invoices = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('fees/invoices.html', invoices=invoices)

@app.route('/students/<int:student_id>')
@login_required
def view_student(student_id):
    if not can_edit_module(current_user, 'students'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    student = Student.query.get_or_404(student_id)
    return render_template('students/student_detail.html', student=student)

@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if not can_edit_module(current_user, 'students') or current_user.role.access_type != 'Edit':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    form.current_course.choices = [(cd.course_full_name, cd.course_full_name) for cd in CourseDetails.query.all()]

    subjects = Subject.query.all()
    form.subject_1_name.choices = [('', 'Select Subject')] + [(s.subject_name, s.subject_name) for s in subjects]
    form.subject_2_name.choices = [('', 'Select Subject')] + [(s.subject_name, s.subject_name) for s in subjects]
    form.subject_3_name.choices = [('', 'Select Subject')] + [(s.subject_name, s.subject_name) for s in subjects]

    if form.validate_on_submit():
        form.populate_obj(student)
        student.updated_at = datetime.utcnow()

        try:
            # Update fee record if fee data is provided
            fee_record = CollegeFees.query.filter_by(student_id=student.id).first()
            if fee_record:
                # Update existing fee record with new fee management fields
                fee_record.total_fees_paid = float(request.form.get('fee_total_fees_paid', fee_record.total_fees_paid) or 0)
                fee_record.meera_rebate_applied = request.form.get('fee_meera_rebate_applied') == 'true'
                fee_record.meera_rebate_approved = request.form.get('fee_meera_rebate_approved') == 'true'
                fee_record.meera_rebate_granted = request.form.get('fee_meera_rebate_granted') == 'true'
                fee_record.meera_rebate_amount = float(request.form.get('fee_meera_rebate_amount', fee_record.meera_rebate_amount) or 0)
                fee_record.scholarship_applied = request.form.get('fee_scholarship_applied') == 'true'
                fee_record.scholarship_approved = request.form.get('fee_scholarship_approved') == 'true'
                fee_record.scholarship_granted = request.form.get('fee_scholarship_granted') == 'true'
                fee_record.government_scholarship_amount = float(request.form.get('fee_government_scholarship_amount', fee_record.government_scholarship_amount) or 0)
                fee_record.total_amount_due = float(request.form.get('fee_total_amount_due', fee_record.total_amount_due) or 0)
                fee_record.pending_dues_for_libraries = request.form.get('fee_pending_dues_for_libraries') == 'true'
                fee_record.pending_dues_for_hostel = request.form.get('fee_pending_dues_for_hostel') == 'true'
                fee_record.exam_admit_card_issued = request.form.get('fee_exam_admit_card_issued') == 'true'

                # Update other fee fields if provided
                if request.form.get('fee_course_tuition_fee'):
                    fee_record.course_tuition_fee = float(request.form.get('fee_course_tuition_fee', 0) or 0)
                if request.form.get('fee_enrollment_fee'):
                    fee_record.enrollment_fee = float(request.form.get('fee_enrollment_fee', 0) or 0)
                if request.form.get('fee_eligibility_certificate_fee'):
                    fee_record.eligibility_certificate_fee = float(request.form.get('fee_eligibility_certificate_fee', 0) or 0)
                if request.form.get('fee_university_affiliation_fee'):
                    fee_record.university_affiliation_fee = float(request.form.get('fee_university_affiliation_fee', 0) or 0)
                if request.form.get('fee_university_sports_fee'):
                    fee_record.university_sports_fee = float(request.form.get('fee_university_sports_fee', 0) or 0)
                if request.form.get('fee_university_development_fee'):
                    fee_record.university_development_fee = float(request.form.get('fee_university_development_fee', 0) or 0)
                if request.form.get('fee_tc_cc_fee'):
                    fee_record.tc_cc_fee = float(request.form.get('fee_tc_cc_fee', 0) or 0)
                if request.form.get('fee_miscellaneous_fee_1'):
                    fee_record.miscellaneous_fee_1 = float(request.form.get('fee_miscellaneous_fee_1', 0) or 0)
                if request.form.get('fee_miscellaneous_fee_2'):
                    fee_record.miscellaneous_fee_2 = float(request.form.get('fee_miscellaneous_fee_2', 0) or 0)
                if request.form.get('fee_miscellaneous_fee_3'):
                    fee_record.miscellaneous_fee_3 = float(request.form.get('fee_miscellaneous_fee_3', 0) or 0)
                if request.form.get('fee_total_fee'):
                    fee_record.total_fee = float(request.form.get('fee_total_fee', 0) or 0)

            db.session.commit()
            flash('Student and fee details updated successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'error')

    return render_template('students/student_form.html', form=form, title='Edit Student', student=student)

@app.route('/students/delete/<int:student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    if not can_edit_module(current_user, 'students') or current_user.role.access_type != 'Edit':
        return jsonify({'error': 'Permission denied'}), 403

    student = Student.query.get_or_404(student_id)

    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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

# Fee Detail Routes
@app.route('/fees/view/<int:fee_id>')
@login_required
def view_fee_detail(fee_id):
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    fee_record = CollegeFees.query.get_or_404(fee_id)
    student = Student.query.get_or_404(fee_record.student_id)
    invoices = Invoice.query.filter_by(student_id=student.id).all()

    return render_template('fees/fee_detail.html', fee_record=fee_record, student=student, invoices=invoices)

# PDF Generation Routes
@app.route('/students/<int:student_id>/pdf')
@login_required
def student_pdf(student_id):
    if not can_edit_module(current_user, 'students'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    student = Student.query.get_or_404(student_id)
    pdf_data = generate_pdf_student_report(student)

    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=student_report_{student.student_unique_id}.pdf'

    return response

@app.route('/invoice/<int:invoice_id>/pdf')
@login_required
def invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    pdf_data = generate_pdf_invoice(invoice)

    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.pdf'

    return response

@app.route('/student/<int:student_id>/fee-statement/pdf')
@login_required
def student_fee_statement_pdf(student_id):
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    student = Student.query.get_or_404(student_id)
    fee_record = CollegeFees.query.filter_by(student_id=student_id).first()
    invoices = Invoice.query.filter_by(student_id=student_id).order_by(Invoice.date_time.desc()).all()
    
    pdf_data = generate_pdf_fee_statement(student, fee_record, invoices)

    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=fee_statement_{student.student_unique_id}.pdf'

    return response

@app.route('/student/<int:student_id>/fee-statement/print')
@login_required
def student_fee_statement_print(student_id):
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    student = Student.query.get_or_404(student_id)
    fee_record = CollegeFees.query.filter_by(student_id=student_id).first()
    
    # Generate PDF without payment history for printing
    pdf_data = generate_pdf_fee_statement_print(student, fee_record)

    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=fee_statement_print_{student.student_unique_id}.pdf'

    return response

@app.route('/api/student-latest-invoice/<int:student_id>')
@login_required
def api_student_latest_invoice(student_id):
    try:
        latest_invoice = Invoice.query.filter_by(student_id=student_id).order_by(Invoice.date_time.desc()).first()
        if latest_invoice:
            return jsonify({'success': True, 'invoice_id': latest_invoice.id})
        else:
            return jsonify({'success': False, 'message': 'No invoice found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/report-card/<int:exam_id>/pdf')
@login_required
def report_card_pdf(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    pdf_data = generate_pdf_report_card(exam)

    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=report_card_{exam.student.student_unique_id}.pdf'

    return response

# Profile Routes
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UserForm(obj=current_user)
    form.role_id.choices = [(current_user.role_id, current_user.role.role_name)]
    form.role_id.data = current_user.role_id
    form.status.data = current_user.status

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.gender = form.gender.data
        current_user.birthdate = form.birthdate.data
        current_user.street = form.street.data
        current_user.area_village = form.area_village.data
        current_user.city_tehsil = form.city_tehsil.data
        current_user.state = form.state.data
        current_user.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')

    return render_template('profile_edit.html', form=form, title='Edit Profile')

@app.route('/invoice/<int:invoice_id>/view')
@login_required
def view_invoice(invoice_id):
    if not can_edit_module(current_user, 'fees'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    invoice = Invoice.query.get_or_404(invoice_id)
    student = Student.query.get_or_404(invoice.student_id)
    fee_record = CollegeFees.query.filter_by(student_id=student.id).first()

    return render_template('fees/invoice_view.html', invoice=invoice, student=student, fee_record=fee_record)

@app.route('/invoice/<int:invoice_id>/mark-printed', methods=['POST'])
@login_required
def mark_invoice_printed(invoice_id):
    if not can_edit_module(current_user, 'fees') or current_user.role.access_type != 'Edit':
        return jsonify({'error': 'Permission denied'}), 403

    invoice = Invoice.query.get_or_404(invoice_id)
    
    try:
        invoice.original_invoice_printed = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = generate_password_hash(form.new_password.data)
            current_user.updated_at = datetime.utcnow()

            try:
                db.session.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error changing password: {str(e)}', 'error')
        else:
            flash('Current password is incorrect.', 'error')

    return render_template('change_password.html', form=form, title='Change Password')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Bulk Export Routes
@app.route('/export/<data_type>/<format>')
@login_required
def bulk_export(data_type, format):
    """Bulk export data in various formats"""
    if not can_edit_module(current_user, data_type if data_type not in ['course_details', 'invoices'] else ('courses' if data_type == 'course_details' else 'fees')):
        flash('You do not have permission to export this data.', 'error')
        return redirect(url_for('dashboard'))

    try:
        # Get data based on type
        if data_type == 'students':
            data, headers = get_students_export_data()
            filename = f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        elif data_type == 'courses':
            data, headers = get_courses_export_data()
            filename = f'courses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        elif data_type == 'course_details':
            data, headers = get_course_details_export_data()
            filename = f'course_details_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        elif data_type == 'fees':
            data, headers = get_fees_export_data()
            filename = f'fees_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        elif data_type == 'invoices':
            data, headers = get_invoices_export_data()
            filename = f'invoices_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        elif data_type == 'exams':
            data, headers = get_exams_export_data()
            filename = f'exams_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        elif data_type == 'users':
            data, headers = get_users_export_data()
            filename = f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        elif data_type == 'subjects':
            data, headers = get_subjects_export_data()
            filename = f'subjects_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        else:
            flash('Invalid data type for export.', 'error')
            return redirect(url_for('dashboard'))

        # Export in requested format
        if format == 'csv':
            return export_to_csv(data, headers, f'{filename}.csv')
        elif format == 'excel':
            return export_to_excel(data, headers, f'{filename}.xlsx')
        elif format == 'json':
            return export_to_json(data, headers, f'{filename}.json')
        else:
            flash('Invalid export format.', 'error')
            return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Bulk Import Routes
@app.route('/import/<data_type>', methods=['POST'])
@login_required
def bulk_import(data_type):
    """Bulk import data from uploaded files"""
    if not can_edit_module(current_user, data_type if data_type not in ['course_details', 'invoices'] else ('courses' if data_type == 'course_details' else 'fees')):
        flash('You do not have permission to import this data.', 'error')
        return redirect(url_for('dashboard'))

    if current_user.role.access_type != 'Edit':
        flash('You need edit permissions to import data.', 'error')
        return redirect(url_for('dashboard'))

    try:
        if 'import_file' not in request.files:
            flash('No file selected for import.', 'error')
            return redirect(request.referrer or url_for('dashboard'))

        file = request.files['import_file']
        if file.filename == '':
            flash('No file selected for import.', 'error')
            return redirect(request.referrer or url_for('dashboard'))

        # Process the import
        success, message = process_import_file(file, data_type)

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')

    except Exception as e:
        flash(f'Import failed: {str(e)}', 'error')

    return redirect(request.referrer or url_for('dashboard'))

# Template download routes
@app.route('/download-template/<data_type>')
@login_required
def download_template(data_type):
    """Download template files for bulk import"""
    try:
        if data_type == 'students':
            headers = [
                'Student ID', 'External ID', 'First Name', 'Last Name', 'Father Name', 'Mother Name',
                'Gender', 'Category', 'Email', 'Current Course', 'Subject 1', 'Subject 2', 'Subject 3',
                'Percentage', 'Street', 'Area/Village', 'City/Tehsil', 'State', 'Phone', 
                'Aadhaar Number', 'APAAR ID', 'School Name', 'Scholarship Status', 
                'Meera Rebate Status', 'Dropout Status', 'Admission Date'
            ]
            sample_data = [
                ['STU-24-001', 'EXT001', 'John', 'Doe', 'Father Name', 'Mother Name',
                 'Male', 'General', 'john@example.com', 'BA First Year', 'English', 'Hindi', 'History',
                 '85.5', 'Main Street', 'Village Name', 'City Name', 'State Name', '9876543210',
                 '123456789012', 'APAAR ID', 'School Name', 'Scholarship Status', 
                'Meera Rebate Status', 'Active', '2024-01-15']
            ]
        elif data_type == 'courses':
            headers = ['Course ID', 'Short Name', 'Full Name', 'Category', 'Duration (Years)']
            sample_data = [
                ['', 'BA', 'Bachelor of Arts', 'Undergraduate', '3']
            ]
        elif data_type == 'course_details':
            headers = [
                'ID', 'Course Full Name', 'Course Short Name', 'Year/Semester', 
                'Course Tuition Fee', 'Course Type', 'Misc Fee 1', 'Misc Fee 2', 
                'Misc Fee 3', 'Misc Fee 4', 'Misc Fee 5', 'Misc Fee 6', 'Total Course Fees'
            ]
            sample_data = [
                ['', 'Bachelor of Arts First Year', 'BA', 'First Year', '15000', 'Regular',
                 '1000', '500', '0', '0', '0', '0', '16500']
            ]
        elif data_type == 'users':
            headers = [
                'User ID', 'Username', 'First Name', 'Last Name', 'Email', 'Phone', 
                'Gender', 'Role', 'Status', 'Created Date'
            ]
            sample_data = [
                ['', 'teacher1', 'Teacher', 'Name', 'teacher@example.com', '9876543210',
                 'Male', 'Teacher', 'Active', '2024-01-01']
            ]
        elif data_type == 'invoices':
            headers = [
                'Invoice Number', 'Student ID', 'Student Name', 'Course', 'Invoice Date',
                'Amount', 'Payment Mode', 'Status', 'Academic Year', 'Installment Number'
            ]
            sample_data = [
                ['INV-2024-001', 'BA-24-001', 'Student Name', 'Bachelor of Arts First Year', '2024-01-15',
                 '5000', 'Cash', 'Paid', '2024-25', '1']
            ]
        else:
            flash('Invalid template type.', 'error')
            return redirect(url_for('dashboard'))

        return export_to_csv(sample_data, headers, f'{data_type}_template.csv')

    except Exception as e:
        flash(f'Template download failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))