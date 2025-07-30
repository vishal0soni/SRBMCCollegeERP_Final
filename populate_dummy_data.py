liation_fee': 300,
            'university_sports_fee': 100,
            'university_development_fee': 400,
            'tc_cc_fee': 50,
            'miscellaneous_fee_1': 200,
            'miscellaneous_fee_2': 150,
            'miscellaneous_fee_3': 100,
            'total_fee': total_fee,
            'payment_mode': random.choice(payment_modes),
            'installment_1': round(installments[0], 2) if len(installments) > 0 else 0,
            'installment_2': round(installments[1], 2) if len(installments) > 1 else 0,
            'installment_3': round(installments[2], 2) if len(installments) > 2 else 0,
            'installment_4': round(installments[3], 2) if len(installments) > 3 else 0,
            'installment_5': 0,
            'installment_6': 0
        }
        
        college_fee = CollegeFees(**fee_data)
        db.session.add(college_fee)
        db.session.flush()  # Get the fee ID
        
        # Create invoices for paid installments (80% of students have paid at least 1 installment)
        if random.random() < 0.8:
            num_paid = random.randint(1, num_installments)
            
            for installment_num in range(1, num_paid + 1):
                invoice_number = generate_invoice_number()
                while Invoice.query.filter_by(invoice_number=invoice_number).first():
                    invoice_number = generate_invoice_number()
                
                installment_amount = getattr(college_fee, f'installment_{installment_num}')
                
                if installment_amount > 0:
                    invoice_data = {
                        'student_id': student.id,
                        'course_id': course.course_id,
                        'invoice_number': invoice_number,
                        'date_time': datetime.now() - timedelta(days=random.randint(1, 180)),
                        'invoice_amount': installment_amount,
                        'original_invoice_printed': random.choice([True, False]),
                        'installment_number': installment_num
                    }
                    
                    invoice = Invoice(**invoice_data)
                    db.session.add(invoice)
                    
                    # Update fee record with invoice number
                    setattr(college_fee, f'invoice{installment_num}_number', invoice_number)
    
    db.session.commit()
    print("✓ Fees and invoices created")


def create_exams():
    """Create exam records for students"""
    print("Creating exam records...")
    
    students = Student.query.all()
    courses = Course.query.all()
    
    exam_names = [
        'First Semester Examination',
        'Second Semester Examination', 
        'Third Semester Examination',
        'Fourth Semester Examination',
        'Fifth Semester Examination',
        'Sixth Semester Examination',
        'Annual Examination',
        'Supplementary Examination'
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
            subjects = [student.subject_1_name, student.subject_2_name, student.subject_3_name]
            subjects = [s for s in subjects if s]  # Remove None values
            
            # Generate marks for each subject
            subject_marks = []
            total_max = 0
            total_obtained = 0
            
            for i, subject in enumerate(subjects[:6]):  # Max 6 subjects
                if subject:
                    max_marks = 100
                    # Generate realistic marks (60-95% of max marks)
                    obtained_marks = random.randint(int(max_marks * 0.6), int(max_marks * 0.95))
                    
                    subject_marks.append({
                        'name': subject,
                        'max': max_marks,
                        'obtained': obtained_marks
                    })
                    
                    total_max += max_marks
                    total_obtained += obtained_marks
            
            # Calculate percentage and grade
            percentage = (total_obtained / total_max * 100) if total_max > 0 else 0
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
                'exam_date': date.today() - timedelta(days=random.randint(30, 365))
            }
            
            # Add subject-wise marks
            for i, marks in enumerate(subject_marks):
                if i < 6:  # Database supports up to 6 subjects
                    exam_data[f'subject{i+1}_name'] = marks['name']
                    exam_data[f'subject{i+1}_max_marks'] = marks['max']
                    exam_data[f'subject{i+1}_obtained_marks'] = marks['obtained']
            
            exam = Exam(**exam_data)
            db.session.add(exam)
    
    db.session.commit()
    print("✓ Exam records created")


def create_additional_users():
    """Create additional users for different roles"""
    print("Creating additional users...")
    
    # Get roles
    roles = {role.role_name: role for role in UserRole.query.all()}
    
    additional_users = [
        {
            'username': 'admission_officer',
            'password': 'admission123',
            'first_name': 'Rajesh',
            'last_name': 'Kumar',
            'email': 'admission@srbmc.edu.in',
            'role': 'Admission Officer',
            'phone': '9876543210'
        },
        {
            'username': 'accountant',
            'password': 'account123',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'email': 'accounts@srbmc.edu.in',
            'role': 'Accountant',
            'phone': '9876543211'
        },
        {
            'username': 'exam_controller',
            'password': 'exam123',
            'first_name': 'Suresh',
            'last_name': 'Gupta',
            'email': 'exams@srbmc.edu.in',
            'role': 'Exam Controller',
            'phone': '9876543212'
        },
        {
            'username': 'admission_assistant',
            'password': 'assist123',
            'first_name': 'Neha',
            'last_name': 'Jain',
            'email': 'assist.admission@srbmc.edu.in',
            'role': 'Admission Assistant',
            'phone': '9876543213'
        }
    ]
    
    for user_data in additional_users:
        if not UserProfile.query.filter_by(username=user_data['username']).first():
            role = roles.get(user_data['role'])
            if role:
                user = UserProfile(
                    role_id=role.role_id,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    username=user_data['username'],
                    password_hash=generate_password_hash(user_data['password']),
                    status='Active',
                    gender='Male' if user_data['first_name'] in ['Rajesh', 'Suresh'] else 'Female',
                    city_tehsil='Raniwara',
                    state='Rajasthan'
                )
                db.session.add(user)
    
    db.session.commit()
    print("✓ Additional users created")


def print_summary():
    """Print summary of created data"""
    print("\n" + "="*50)
    print("DUMMY DATA CREATION SUMMARY")
    print("="*50)
    
    print(f"User Roles: {UserRole.query.count()}")
    print(f"User Profiles: {UserProfile.query.count()}")
    print(f"Courses: {Course.query.count()}")
    print(f"Course Details: {CourseDetails.query.count()}")
    print(f"Subjects: {Subject.query.count()}")
    print(f"Students: {Student.query.count()}")
    print(f"Fee Records: {CollegeFees.query.count()}")
    print(f"Invoices: {Invoice.query.count()}")
    print(f"Exam Records: {Exam.query.count()}")
    
    print("\n" + "="*50)
    print("DEFAULT LOGIN CREDENTIALS")
    print("="*50)
    print("Administrator: admin/admin")
    print("User 1: Vishal/Vishal")
    print("User 2: Sonali/Sonali")
    print("Admission Officer: admission_officer/admission123")
    print("Accountant: accountant/account123")
    print("Exam Controller: exam_controller/exam123")
    print("Admission Assistant: admission_assistant/assist123")
    print("="*50)


def main():
    """Main function to populate dummy data"""
    with app.app_context():
        print("Starting SRBMC ERP Dummy Data Population...")
        print("="*50)
        
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
        print("You can now log in to the system and explore all features with realistic data.")


if __name__ == "__main__":
    main()