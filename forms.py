from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, IntegerField, DecimalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserForm(FlaskForm):
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    birthdate = DateField('Birth Date', validators=[Optional()])
    street = StringField('Street Address', validators=[Optional(), Length(max=200)])
    area_village = StringField('Area/Village', validators=[Optional(), Length(max=100)])
    city_tehsil = StringField('City/Tehsil', validators=[Optional(), Length(max=100)])
    state = StringField('State', validators=[Optional(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[Optional(), Length(min=4, max=128)])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    submit = SubmitField('Save User')

class StudentForm(FlaskForm):
    external_id = StringField('External ID', validators=[Optional(), Length(max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    father_name = StringField('Father Name', validators=[Optional(), Length(max=200)])
    mother_name = StringField('Mother Name', validators=[Optional(), Length(max=200)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    category = SelectField('Category', choices=[('General', 'General'), ('SC', 'SC'), ('ST', 'ST'), ('OBC', 'OBC')])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    current_course = SelectField('Current Course', validators=[DataRequired()])
    subject_1_name = SelectField('Subject 1', validators=[Optional()])
    subject_2_name = SelectField('Subject 2', validators=[Optional()])
    subject_3_name = SelectField('Subject 3', validators=[Optional()])
    percentage = DecimalField('Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    street = StringField('Street Address', validators=[Optional(), Length(max=200)])
    area_village = StringField('Area/Village', validators=[Optional(), Length(max=100)])
    city_tehsil = StringField('City/Tehsil', validators=[Optional(), Length(max=100)])
    state = StringField('State', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    aadhaar_card_number = StringField('Aadhaar Number', validators=[Optional(), Length(max=20)])
    apaar_id = StringField('APAAR ID', validators=[Optional(), Length(max=20)])
    school_name = StringField('School Name', validators=[Optional(), Length(max=200)])
    scholarship_status = SelectField('Government Scholarship', choices=[('Not Applied', 'Not Applied'), ('Applied', 'Applied'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Granted', 'Granted')])
    rebate_meera_scholarship_status = SelectField('Meera Rebate', choices=[('Not Applied', 'Not Applied'), ('Applied', 'Applied'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Granted', 'Granted')])
    admission_date = DateField('Admission Date', validators=[DataRequired()])
    student_status = SelectField('Student Status', choices=[('Active', 'Active'), ('Dropout', 'Dropout'), ('Graduated', 'Graduated')], default='Active')
    submit = SubmitField('Save Student')

class CourseForm(FlaskForm):
    course_short_name = StringField('Course Short Name', validators=[DataRequired(), Length(max=10)])
    course_full_name = StringField('Course Full Name', validators=[DataRequired(), Length(max=200)])
    course_category = SelectField('Course Category', choices=[
        ('', 'Select Category'),
        ('Undergraduate', 'Undergraduate'),
        ('Postgraduate', 'Postgraduate'),
        ('Diploma', 'Diploma'),
        ('Certificate', 'Certificate')
    ], validators=[DataRequired()])
    duration = SelectField('Duration (Years)', choices=[
        ('', 'Select Duration'),
        ('1', '1 Year'),
        ('2', '2 Years'),
        ('3', '3 Years'),
        ('4', '4 Years'),
        ('5', '5 Years')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Course')

class CourseDetailsForm(FlaskForm):
    course_full_name = StringField('Course Full Name', validators=[DataRequired(), Length(max=200)])
    course_short_name = SelectField('Course Short Name', coerce=str, validators=[DataRequired()])
    year_semester = StringField('Year/Semester', validators=[DataRequired(), Length(max=20)])
    course_tuition_fee = DecimalField('Course Tuition Fee', validators=[Optional()], default=0)
    course_type = SelectField('Course Type', choices=[
        ('', 'Select Course Type'),
        ('Regular', 'Regular'),
        ('Integrated', 'Integrated')
    ], validators=[Optional()])
    misc_course_fees_1 = DecimalField('Misc Fee 1', validators=[Optional()], default=0)
    misc_course_fees_2 = DecimalField('Misc Fee 2', validators=[Optional()], default=0)
    misc_course_fees_3 = DecimalField('Misc Fee 3', validators=[Optional()], default=0)
    misc_course_fees_4 = DecimalField('Misc Fee 4', validators=[Optional()], default=0)
    misc_course_fees_5 = DecimalField('Misc Fee 5', validators=[Optional()], default=0)
    misc_course_fees_6 = DecimalField('Misc Fee 6', validators=[Optional()], default=0)
    submit = SubmitField('Save Course Details')

class SubjectForm(FlaskForm):
    course_short_name = SelectField('Course', validators=[DataRequired()])
    subject_name = StringField('Subject Name', validators=[DataRequired(), Length(max=200)])
    subject_type = SelectField('Subject Type', choices=[('Compulsory', 'Compulsory'), ('Elective', 'Elective')], validators=[DataRequired()])
    submit = SubmitField('Save Subject')

class PaymentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    payment_mode = SelectField('Payment Mode', choices=[('Cash', 'Cash'), ('Online', 'Online'), ('Cheque', 'Cheque'), ('DD', 'DD')])
    submit = SubmitField('Process Payment')

class FeeManagementForm(FlaskForm):
    # Basic fee fields
    course_tuition_fee = DecimalField('Course Tuition Fee', validators=[Optional()], default=0)
    enrollment_fee = DecimalField('Enrollment Fee', validators=[Optional()], default=0)
    eligibility_certificate_fee = DecimalField('Eligibility Certificate Fee', validators=[Optional()], default=0)
    university_affiliation_fee = DecimalField('University Affiliation Fee', validators=[Optional()], default=0)
    university_sports_fee = DecimalField('University Sports Fee', validators=[Optional()], default=0)
    university_development_fee = DecimalField('University Development Fee', validators=[Optional()], default=0)
    tc_cc_fee = DecimalField('TC/CC Fee', validators=[Optional()], default=0)
    miscellaneous_fee_1 = DecimalField('Miscellaneous Fee 1', validators=[Optional()], default=0)
    miscellaneous_fee_2 = DecimalField('Miscellaneous Fee 2', validators=[Optional()], default=0)
    miscellaneous_fee_3 = DecimalField('Miscellaneous Fee 3', validators=[Optional()], default=0)

    # New fields requested by user
    total_fees_paid = DecimalField('Total Fees Paid', validators=[Optional()], default=0)
    meera_rebate_applied = BooleanField('Meera Rebate Applied')
    meera_rebate_approved = BooleanField('Meera Rebate Approved')
    meera_rebate_granted = BooleanField('Meera Rebate Granted')
    meera_rebate_amount = DecimalField('Meera Rebate Amount', validators=[Optional()], default=0)
    scholarship_applied = BooleanField('Government Scholarship Applied')
    scholarship_approved = BooleanField('Government Scholarship Approved')
    scholarship_granted = BooleanField('Government Scholarship Granted')
    government_scholarship_amount = DecimalField('Government Scholarship Amount', validators=[Optional()], default=0)
    total_amount_due = DecimalField('Total Amount Due', validators=[Optional()], default=0)
    total_amount_after_rebate = DecimalField('Total Amount after rebate', validators=[Optional()], default=0)
    pending_dues_for_libraries = BooleanField('Pending Dues for Libraries')
    pending_dues_for_hostel = BooleanField('Pending Dues for Hostel')
    exam_admit_card_issued = BooleanField('Exam Admit Card Issued')

    # Installments
    installment_1 = DecimalField('Installment 1', validators=[Optional()], default=0)
    installment_2 = DecimalField('Installment 2', validators=[Optional()], default=0)
    installment_3 = DecimalField('Installment 3', validators=[Optional()], default=0)
    installment_4 = DecimalField('Installment 4', validators=[Optional()], default=0)
    installment_5 = DecimalField('Installment 5', validators=[Optional()], default=0)
    installment_6 = DecimalField('Installment 6', validators=[Optional()], default=0)

    payment_mode = SelectField('Payment Mode', choices=[('Cash', 'Cash'), ('Online', 'Online'), ('Cheque', 'Cheque'), ('DD', 'DD')])
    submit = SubmitField('Save Fee Details')

class ExamForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[Optional()])
    exam_name = StringField('Exam Name', validators=[DataRequired(), Length(max=100)])
    exam_date = DateField('Exam Date', validators=[DataRequired()])

    # Subject marks
    subject1_name = StringField('Subject 1 Name')
    subject1_max_marks = IntegerField('Max Marks', default=100)
    subject1_obtained_marks = IntegerField('Obtained Marks', default=0)

    subject2_name = StringField('Subject 2 Name')
    subject2_max_marks = IntegerField('Max Marks', default=100)
    subject2_obtained_marks = IntegerField('Obtained Marks', default=0)

    subject3_name = StringField('Subject 3 Name')
    subject3_max_marks = IntegerField('Max Marks', default=100)
    subject3_obtained_marks = IntegerField('Obtained Marks', default=0)

    submit = SubmitField('Save Exam Results')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=4, max=128)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError('New passwords must match.')