
#!/usr/bin/env python3
"""
Script to create missing fee records for students who don't have them
"""

from app import app, db
from models import Student, CollegeFees, Course, CourseDetails

def create_missing_fee_records():
    """Create fee records for all students who don't have one"""
    
    with app.app_context():
        try:
            print("Creating missing fee records for students...")
            
            # Get all students
            all_students = Student.query.all()
            created_count = 0
            skipped_count = 0
            error_count = 0
            
            for student in all_students:
                # Check if fee record already exists
                existing_fee = CollegeFees.query.filter_by(student_id=student.id).first()
                
                if existing_fee:
                    skipped_count += 1
                    continue
                
                # Get course information
                if not student.current_course:
                    print(f"Skipping student {student.student_unique_id} - no course assigned")
                    skipped_count += 1
                    continue
                
                # Find course details
                course_detail = CourseDetails.query.filter_by(
                    course_full_name=student.current_course
                ).first()
                
                if not course_detail:
                    print(f"Warning: No course details found for {student.current_course}")
                    # Try to find by partial match
                    course_short = student.current_course.split()[0] if student.current_course else None
                    if course_short:
                        course_detail = CourseDetails.query.filter(
                            CourseDetails.course_full_name.like(f"{course_short}%")
                        ).first()
                
                # Find course
                course = None
                if course_detail:
                    course = Course.query.filter_by(
                        course_short_name=course_detail.course_short_name
                    ).first()
                
                # Set default fee values
                total_course_fees = float(course_detail.total_course_fees) if course_detail else 15000
                
                # Create fee record
                fee_record = CollegeFees(
                    student_id=student.id,
                    course_id=course.course_id if course else None,
                    coursedetail_id=course_detail.id if course_detail else None,
                    course_full_name=student.current_course,
                    total_course_fees=total_course_fees,
                    enrollment_fee=500,
                    eligibility_certificate_fee=200,
                    university_affiliation_fee=300,
                    university_sports_fee=100,
                    university_development_fee=400,
                    tc_cc_fee=50,
                    miscellaneous_fee_1=200,
                    miscellaneous_fee_2=150,
                    miscellaneous_fee_3=100,
                    installment_1=0,
                    installment_2=0,
                    installment_3=0,
                    installment_4=0,
                    installment_5=0,
                    installment_6=0,
                    meera_rebate_applied=(student.rebate_meera_scholarship_status == 'Applied'),
                    meera_rebate_approved=(student.rebate_meera_scholarship_status == 'Approved'),
                    meera_rebate_granted=(student.rebate_meera_scholarship_status == 'Granted'),
                    meera_rebate_amount=0,
                    scholarship_applied=(student.scholarship_status == 'Applied'),
                    scholarship_approved=(student.scholarship_status == 'Approved'),
                    scholarship_granted=(student.scholarship_status == 'Granted'),
                    government_scholarship_amount=0,
                    total_amount_due=0,
                    total_amount_after_rebate=0,
                    pending_dues_for_libraries=False,
                    pending_dues_for_hostel=False,
                    exam_admit_card_issued=False
                )
                
                try:
                    db.session.add(fee_record)
                    created_count += 1
                    
                    if created_count % 50 == 0:
                        db.session.commit()
                        print(f"Created {created_count} fee records so far...")
                        
                except Exception as e:
                    print(f"Error creating fee record for student {student.student_unique_id}: {str(e)}")
                    error_count += 1
                    db.session.rollback()
                    continue
            
            # Final commit
            db.session.commit()
            
            print("\n" + "="*60)
            print("Fee Record Creation Summary:")
            print("="*60)
            print(f"Total students: {len(all_students)}")
            print(f"Fee records created: {created_count}")
            print(f"Skipped (already have fee records): {skipped_count}")
            print(f"Errors: {error_count}")
            print("="*60)
            
            # Verify final count
            total_fee_records = CollegeFees.query.count()
            print(f"\nTotal fee records in database now: {total_fee_records}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during fee record creation: {str(e)}")

if __name__ == "__main__":
    create_missing_fee_records()
