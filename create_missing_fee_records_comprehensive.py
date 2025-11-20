
#!/usr/bin/env python3
"""
Comprehensive script to create fee records for students who don't have them.
Follows all system conditions and restrictions.
"""

from app import app, db
from models import Student, CollegeFees, Course, CourseDetails
from datetime import datetime

def create_missing_fee_records_comprehensive():
    """Create fee records for all students who don't have one, following all system rules"""
    
    with app.app_context():
        try:
            print("="*80)
            print("Creating Missing Fee Records - Comprehensive")
            print("="*80)
            
            # Get all students
            all_students = Student.query.all()
            print(f"\nTotal students in database: {len(all_students)}")
            
            # Get students without fee records
            students_without_fees = []
            for student in all_students:
                existing_fee = CollegeFees.query.filter_by(student_id=student.id).first()
                if not existing_fee:
                    students_without_fees.append(student)
            
            print(f"Students without fee records: {len(students_without_fees)}")
            
            if len(students_without_fees) == 0:
                print("\nAll students already have fee records!")
                return
            
            created_count = 0
            skipped_count = 0
            error_count = 0
            
            print("\nProcessing students...")
            print("-" * 80)
            
            for student in students_without_fees:
                try:
                    # Skip if no course assigned
                    if not student.current_course or student.current_course.strip() == '':
                        print(f"⚠ Skipping {student.student_unique_id} - No course assigned")
                        skipped_count += 1
                        continue
                    
                    # Find course details for the student's current course
                    course_detail = CourseDetails.query.filter_by(
                        course_full_name=student.current_course
                    ).first()
                    
                    # If not found, try partial match
                    if not course_detail:
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
                    
                    # Set fee values from course details or defaults
                    total_course_fees = float(course_detail.total_course_fees) if course_detail else 0
                    
                    # Sync scholarship statuses from student record
                    meera_rebate_applied = (student.rebate_meera_scholarship_status == 'Applied')
                    meera_rebate_approved = (student.rebate_meera_scholarship_status == 'Approved')
                    meera_rebate_granted = (student.rebate_meera_scholarship_status == 'Granted')
                    
                    scholarship_applied = (student.scholarship_status == 'Applied')
                    scholarship_approved = (student.scholarship_status == 'Approved')
                    scholarship_granted = (student.scholarship_status == 'Granted')
                    
                    # Create fee record with proper initialization
                    fee_record = CollegeFees(
                        student_id=student.id,
                        course_id=course.course_id if course else None,
                        coursedetail_id=course_detail.id if course_detail else None,
                        course_full_name=student.current_course,
                        total_course_fees=total_course_fees,
                        enrollment_fee=0,
                        eligibility_certificate_fee=0,
                        university_affiliation_fee=0,
                        university_sports_fee=0,
                        university_development_fee=0,
                        tc_cc_fee=0,
                        miscellaneous_fee_1=0,
                        miscellaneous_fee_2=0,
                        miscellaneous_fee_3=0,
                        # Database will auto-calculate total_fee from formula
                        installment_1=0,
                        installment_2=0,
                        installment_3=0,
                        installment_4=0,
                        installment_5=0,
                        installment_6=0,
                        # Database will auto-calculate total_fees_paid from formula
                        meera_rebate_applied=meera_rebate_applied,
                        meera_rebate_approved=meera_rebate_approved,
                        meera_rebate_granted=meera_rebate_granted,
                        meera_rebate_amount=0,
                        scholarship_applied=scholarship_applied,
                        scholarship_approved=scholarship_approved,
                        scholarship_granted=scholarship_granted,
                        government_scholarship_amount=0,
                        total_amount_due=0,
                        total_amount_after_rebate=0,
                        pending_dues_for_libraries=False,
                        pending_dues_for_hostel=False,
                        exam_admit_card_issued=False
                    )
                    
                    db.session.add(fee_record)
                    created_count += 1
                    
                    print(f"✓ Created fee record for {student.student_unique_id} - {student.first_name} {student.last_name} ({student.current_course})")
                    
                    # Commit in batches of 50
                    if created_count % 50 == 0:
                        db.session.commit()
                        print(f"\n  → Committed {created_count} records...")
                        
                except Exception as e:
                    print(f"✗ Error creating fee record for {student.student_unique_id}: {str(e)}")
                    error_count += 1
                    db.session.rollback()
                    continue
            
            # Final commit
            db.session.commit()
            
            # Print summary
            print("\n" + "="*80)
            print("Fee Record Creation Summary")
            print("="*80)
            print(f"Total students in database:        {len(all_students)}")
            print(f"Students without fee records:      {len(students_without_fees)}")
            print(f"Fee records created:               {created_count}")
            print(f"Skipped (no course assigned):      {skipped_count}")
            print(f"Errors:                            {error_count}")
            print("="*80)
            
            # Verify final count
            total_fee_records = CollegeFees.query.count()
            total_students = Student.query.count()
            print(f"\nFinal Verification:")
            print(f"  Total students:      {total_students}")
            print(f"  Total fee records:   {total_fee_records}")
            print(f"  Coverage:            {(total_fee_records/total_students*100):.1f}%")
            print("="*80)
            
            if created_count > 0:
                print("\n✓ Fee records created successfully!")
            else:
                print("\n⚠ No new fee records were created.")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Critical error during fee record creation: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_missing_fee_records_comprehensive()
