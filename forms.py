from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, IntegerField, DecimalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
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
    school_name = StringField('School Name', validators=[Optional(), Length(max=200)])
    scholarship_status = SelectField('Government Scholarship', choices=[('Applied', 'Applied'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])
    rebate_meera_scholarship_status = SelectField('Meera Rebate', choices=[('Applied', 'Applied'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])
    admission_date = DateField('Admission Date', validators=[DataRequired()])
    submit = SubmitField('Save Student')

class CourseForm(FlaskForm):
    course_short_name = StringField('Course Short Name', validators=[DataRequired(), Length(max=10)])
    course_full_name = StringField('Course Full Name', validators=[DataRequired(), Length(max=200)])
    course_category = StringField('Course Category', validators=[Optional(), Length(max=100)])
    duration = IntegerField('Duration (Years)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Save Course')

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

class ExamForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    semester = StringField('Semester', validators=[DataRequired(), Length(max=20)])
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
