from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class UserRole(db.Model):
    __tablename__ = 'user_roles'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(100), nullable=False, unique=True)
    role_description = db.Column(db.Text)
    access_type = db.Column(db.String(20), nullable=False)  # 'Edit' or 'Read'
    access_level = db.Column(db.Integer, nullable=False)

    # Relationship
    users = db.relationship('UserProfile', backref='role', lazy=True)

class UserProfile(UserMixin, db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.role_id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    birthdate = db.Column(db.Date)
    street = db.Column(db.String(200))
    area_village = db.Column(db.String(100))
    city_tehsil = db.Column(db.String(100))
    state = db.Column(db.String(100))
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Course(db.Model):
    __tablename__ = 'courses'

    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_short_name = db.Column(db.String(10), nullable=False, unique=True)
    course_full_name = db.Column(db.String(200), nullable=False)
    course_category = db.Column(db.String(100))
    duration = db.Column(db.Integer)  # in years

    # Relationships
    course_details = db.relationship('CourseDetails', backref='course', lazy=True)
    subjects = db.relationship('Subject', backref='course', lazy=True)

class CourseDetails(db.Model):
    __tablename__ = 'course_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_full_name = db.Column(db.String(200), nullable=False)
    course_short_name = db.Column(db.String(10), db.ForeignKey('courses.course_short_name'), nullable=False)
    year_semester = db.Column(db.String(20), nullable=False)
    course_tuition_fee = db.Column(db.Numeric(10, 2), default=0)
    course_type = db.Column(db.String(50))
    misc_course_fees_1 = db.Column(db.Numeric(10, 2), default=0)
    misc_course_fees_2 = db.Column(db.Numeric(10, 2), default=0)
    misc_course_fees_3 = db.Column(db.Numeric(10, 2), default=0)
    misc_course_fees_4 = db.Column(db.Numeric(10, 2), default=0)
    misc_course_fees_5 = db.Column(db.Numeric(10, 2), default=0)
    misc_course_fees_6 = db.Column(db.Numeric(10, 2), default=0)
    total_course_fees = db.Column(db.Numeric(10, 2), default=0)

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_short_name = db.Column(db.String(10), db.ForeignKey('courses.course_short_name'), nullable=False)
    subject_name = db.Column(db.String(200), nullable=False)
    subject_type = db.Column(db.String(20), nullable=False)  # 'Compulsory' or 'Elective'

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_unique_id = db.Column(db.String(20), unique=True, nullable=False)
    external_id = db.Column(db.String(50))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(200))
    mother_name = db.Column(db.String(200))
    gender = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(20))  # General, SC, ST, OBC
    email = db.Column(db.String(120))
    current_course = db.Column(db.String(200))
    subject_1_name = db.Column(db.String(200))
    subject_2_name = db.Column(db.String(200))
    subject_3_name = db.Column(db.String(200))
    percentage = db.Column(db.Numeric(5, 2))
    street = db.Column(db.String(200))
    area_village = db.Column(db.String(100))
    city_tehsil = db.Column(db.String(100))
    state = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    aadhaar_card_number = db.Column(db.String(20))
    apaar_id = db.Column(db.String(20))
    school_name = db.Column(db.String(200))
    scholarship_status = db.Column(db.String(20), default='Not Applied')  # Not Applied, Applied, Approved, Rejected, Granted
    rebate_meera_scholarship_status = db.Column(db.String(20), default='Not Applied')
    student_status = db.Column(db.String(20), default='Active')  # Active, Dropout, Graduated
    admission_date = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    fees = db.relationship('CollegeFees', backref='student', lazy=True)
    exams = db.relationship('Exam', backref='student', lazy=True)
    invoices = db.relationship('Invoice', backref='student', lazy=True)

class CollegeFees(db.Model):
    __tablename__ = 'college_fees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    coursedetail_id = db.Column(db.Integer, db.ForeignKey('course_details.id'))
    course_full_name = db.Column(db.String(200))  # Snapshot of course name at time of fee record creation
    total_course_fees = db.Column(db.Numeric(10, 2), default=0)
    enrollment_fee = db.Column(db.Numeric(10, 2), default=0)
    eligibility_certificate_fee = db.Column(db.Numeric(10, 2), default=0)
    university_affiliation_fee = db.Column(db.Numeric(10, 2), default=0)
    university_sports_fee = db.Column(db.Numeric(10, 2), default=0)
    university_development_fee = db.Column(db.Numeric(10, 2), default=0)
    tc_cc_fee = db.Column(db.Numeric(10, 2), default=0)
    miscellaneous_fee_1 = db.Column(db.Numeric(10, 2), default=0)
    miscellaneous_fee_2 = db.Column(db.Numeric(10, 2), default=0)
    miscellaneous_fee_3 = db.Column(db.Numeric(10, 2), default=0)
    total_fee = db.Column(db.Numeric(10, 2), default=0)
    payment_mode = db.Column(db.String(50))

    # Installments
    installment_1 = db.Column(db.Numeric(10, 2), default=0)
    invoice1_number = db.Column(db.String(50))
    installment_2 = db.Column(db.Numeric(10, 2), default=0)
    invoice2_number = db.Column(db.String(50))
    installment_3 = db.Column(db.Numeric(10, 2), default=0)
    invoice3_number = db.Column(db.String(50))
    installment_4 = db.Column(db.Numeric(10, 2), default=0)
    invoice4_number = db.Column(db.String(50))
    installment_5 = db.Column(db.Numeric(10, 2), default=0)
    invoice5_number = db.Column(db.String(50))
    installment_6 = db.Column(db.Numeric(10, 2), default=0)
    invoice6_number = db.Column(db.String(50))

    # New fields requested by user
    total_fees_paid = db.Column(db.Numeric(10, 2), default=0)
    meera_rebate_applied = db.Column(db.Boolean, default=False)
    meera_rebate_approved = db.Column(db.Boolean, default=False)
    meera_rebate_granted = db.Column(db.Boolean, default=False)
    meera_rebate_amount = db.Column(db.Numeric(10, 2), default=0)
    scholarship_applied = db.Column(db.Boolean, default=False)
    scholarship_approved = db.Column(db.Boolean, default=False)
    scholarship_granted = db.Column(db.Boolean, default=False)
    government_scholarship_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount_due = db.Column(db.Numeric(10, 2), default=0)
    total_amount_after_rebate = db.Column(db.Numeric(10, 2), default=0)
    pending_dues_for_libraries = db.Column(db.Boolean, default=False)
    pending_dues_for_hostel = db.Column(db.Boolean, default=False)
    exam_admit_card_issued = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def calculated_total_fees_paid(self):
        """Calculate total fees paid from sum of all installments"""
        return float((self.installment_1 or 0) + (self.installment_2 or 0) + 
                    (self.installment_3 or 0) + (self.installment_4 or 0) + 
                    (self.installment_5 or 0) + (self.installment_6 or 0))

    @property
    def calculated_total_fee(self):
        """Calculate total fee from component fees including eligibility_certificate_fee"""
        return float((self.total_course_fees or 0) + (self.enrollment_fee or 0) + 
                    (self.eligibility_certificate_fee or 0) + (self.university_affiliation_fee or 0) + 
                    (self.university_sports_fee or 0) + (self.university_development_fee or 0) + 
                    (self.tc_cc_fee or 0) + (self.miscellaneous_fee_1 or 0) + 
                    (self.miscellaneous_fee_2 or 0) + (self.miscellaneous_fee_3 or 0))

    @property
    def calculated_total_amount_due(self):
        """Calculate total amount due using the formula: total_amount_after_rebate - (sum of all installments)"""
        total_paid = self.calculated_total_fees_paid
        total_after_rebate = float(self.total_amount_after_rebate or 0)
        return total_after_rebate - total_paid

    def update_total_fees_paid(self):
        """Update total_fees_paid field - now handled by database formula"""
        # The total_fees_paid is now calculated by the database formula:
        # installment_1 + installment_2 + installment_3 + installment_4 + installment_5 + installment_6
        # No need to manually calculate as the database handles this automatically
        pass

    def update_total_fee(self):
        """Update total_fee field to match sum of component fees - now handled by database formula"""
        # The total_fee is now calculated by the database formula:
        # total_course_fees + enrollment_fee + eligibility_certificate_fee + university_affiliation_fee + 
        # university_sports_fee + university_development_fee + tc_cc_fee + 
        # miscellaneous_fee_1 + miscellaneous_fee_2 + miscellaneous_fee_3
        # No need to manually calculate as the database handles this automatically
        pass

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    invoice_amount = db.Column(db.Numeric(10, 2), nullable=False)
    original_invoice_printed = db.Column(db.Boolean, default=False)
    installment_number = db.Column(db.Integer)

class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    coursedetail_id = db.Column(db.Integer, db.ForeignKey('course_details.id'))
    course_full_name = db.Column(db.String(200))  # Snapshot of course name at time of exam
    semester = db.Column(db.String(20))
    exam_name = db.Column(db.String(100), nullable=False)

    # Subject marks (up to 6 subjects)
    subject1_name = db.Column(db.String(200))
    subject1_max_marks = db.Column(db.Integer, default=100)
    subject1_obtained_marks = db.Column(db.Integer, default=0)

    subject2_name = db.Column(db.String(200))
    subject2_max_marks = db.Column(db.Integer, default=100)
    subject2_obtained_marks = db.Column(db.Integer, default=0)

    subject3_name = db.Column(db.String(200))
    subject3_max_marks = db.Column(db.Integer, default=100)
    subject3_obtained_marks = db.Column(db.Integer, default=0)

    subject4_name = db.Column(db.String(200))
    subject4_max_marks = db.Column(db.Integer, default=100)
    subject4_obtained_marks = db.Column(db.Integer, default=0)

    subject5_name = db.Column(db.String(200))
    subject5_max_marks = db.Column(db.Integer, default=100)
    subject5_obtained_marks = db.Column(db.Integer, default=0)

    subject6_name = db.Column(db.String(200))
    subject6_max_marks = db.Column(db.Integer, default=100)
    subject6_obtained_marks = db.Column(db.Integer, default=0)

    total_max_marks = db.Column(db.Integer, default=0)
    total_obtained_marks = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Numeric(5, 2), default=0)
    grade = db.Column(db.String(5))
    overall_status = db.Column(db.String(20))  # Pass/Fail
    exam_date = db.Column(db.Date)
    promotion_processed = db.Column(db.Boolean, default=False)  # Track if promotion has been processed for this exam
    created_at = db.Column(db.DateTime, default=datetime.utcnow)