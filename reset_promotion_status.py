
#!/usr/bin/env python3

"""
Script to reset promotion_processed status for specific students
"""

from app import app, db
from models import Exam, Student
from sqlalchemy import text

def reset_promotion_status(student_unique_id=None):
    """Reset promotion_processed status for a student or all students"""
    with app.app_context():
        try:
            if student_unique_id:
                # Reset for specific student
                student = Student.query.filter_by(student_unique_id=student_unique_id).first()
                if not student:
                    print(f"❌ Student {student_unique_id} not found")
                    return
                
                exams = Exam.query.filter_by(student_id=student.id).all()
                count = 0
                for exam in exams:
                    if exam.promotion_processed:
                        exam.promotion_processed = False
                        count += 1
                
                db.session.commit()
                print(f"✓ Reset promotion status for {count} exam(s) of student {student_unique_id}")
            else:
                # Reset for all students
                result = db.session.execute(text("""
                    UPDATE exams 
                    SET promotion_processed = FALSE 
                    WHERE promotion_processed = TRUE
                """))
                db.session.commit()
                print(f"✓ Reset promotion status for {result.rowcount} exam(s)")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        student_id = sys.argv[1]
        print(f"Resetting promotion status for student: {student_id}")
        reset_promotion_status(student_id)
    else:
        print("Usage:")
        print("  python reset_promotion_status.py BSC-25-001  # Reset specific student")
        print("  python reset_promotion_status.py all         # Reset all students")
        print()
        response = input("Reset promotion status for ALL students? (yes/no): ")
        if response.lower() == 'yes':
            reset_promotion_status()
        else:
            print("Operation cancelled")
