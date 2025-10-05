
#!/usr/bin/env python3
"""
Script to create missing fee record for student Zoya
"""

from app import app, db
from models import Student, CollegeFees, CourseDetails

def fix_zoya_fee_record():
    with app.app_context():
        # Find Zoya's student record
        zoya = Student.query.filter(
            (Student.first_name.ilike('%zoya%')) | 
            (Student.last_name.ilike('%zoya%'))
        ).first()
        
        if not zoya:
            print("Student Zoya not found")
            return
        
        print(f"Found student: {zoya.first_name} {zoya.last_name} (ID: {zoya.student_unique_id})")
        
        # Check if fee record exists
        existing_fee = CollegeFees.query.filter_by(student_id=zoya.id).first()
        
        if existing_fee:
            print(f"Fee record already exists for Zoya (ID: {existing_fee.id})")
            # Update course_full_name if missing
            if not existing_fee.course_full_name and zoya.current_course:
                existing_fee.course_full_name = zoya.current_course
                db.session.commit()
                print(f"Updated course_full_name to: {zoya.current_course}")
            return
        
        # Create fee record
        print("Creating fee record for Zoya...")
        
        course_detail = None
        if zoya.current_course:
            course_detail = CourseDetails.query.filter_by(
                course_full_name=zoya.current_course
            ).first()
        
        fee_record = CollegeFees(
            student_id=zoya.id,
            course_full_name=zoya.current_course,
            coursedetail_id=course_detail.id if course_detail else None,
            total_course_fees=course_detail.total_course_fees if course_detail else 0,
            installment_1=0,
            installment_2=0,
            installment_3=0,
            installment_4=0,
            installment_5=0,
            installment_6=0
        )
        
        db.session.add(fee_record)
        db.session.commit()
        
        print(f"✓ Created fee record for Zoya (Fee ID: {fee_record.id})")
        print(f"  Course: {fee_record.course_full_name}")
        print(f"  Total Fees: {fee_record.total_fee}")

if __name__ == '__main__':
    fix_zoya_fee_record()
