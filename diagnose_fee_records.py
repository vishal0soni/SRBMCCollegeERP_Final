
#!/usr/bin/env python3
"""
Diagnostic script to check the actual state of students and fee records
"""

from app import app, db
from models import Student, CollegeFees
from sqlalchemy import func

def diagnose_fee_records():
    """Check the actual state of students and fee records"""
    
    with app.app_context():
        try:
            print("="*80)
            print("Fee Records Diagnostic Report")
            print("="*80)
            
            # Get total student count
            total_students = Student.query.count()
            print(f"\nTotal students in database: {total_students}")
            
            # Get total fee records count
            total_fee_records = CollegeFees.query.count()
            print(f"Total fee records in database: {total_fee_records}")
            
            # Get students without fee records
            students_with_fees = db.session.query(Student.id).join(
                CollegeFees, Student.id == CollegeFees.student_id
            ).all()
            students_with_fees_ids = {s[0] for s in students_with_fees}
            
            all_student_ids = {s.id for s in Student.query.all()}
            students_without_fees_ids = all_student_ids - students_with_fees_ids
            
            print(f"\nStudents with fee records: {len(students_with_fees_ids)}")
            print(f"Students WITHOUT fee records: {len(students_without_fees_ids)}")
            
            # Show sample students without fee records
            if students_without_fees_ids:
                print("\nSample students WITHOUT fee records (first 10):")
                print("-" * 80)
                sample_ids = list(students_without_fees_ids)[:10]
                for student_id in sample_ids:
                    student = Student.query.get(student_id)
                    print(f"  ID: {student.id:4d} | {student.student_unique_id:15s} | {student.first_name} {student.last_name:20s} | Course: {student.current_course or 'None'}")
            
            # Show all fee records
            print(f"\nAll fee records in database:")
            print("-" * 80)
            all_fees = CollegeFees.query.all()
            for fee in all_fees:
                student = Student.query.get(fee.student_id)
                print(f"  Fee ID: {fee.id:4d} | Student: {student.student_unique_id if student else 'Unknown':15s} | {student.first_name if student else 'N/A'} {student.last_name if student else 'N/A'}")
            
            print("\n" + "="*80)
            print("End of Diagnostic Report")
            print("="*80)
            
        except Exception as e:
            print(f"\n✗ Error during diagnosis: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    diagnose_fee_records()
