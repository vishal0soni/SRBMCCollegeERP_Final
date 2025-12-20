
from app import app, db
from models import Subject, Student, Exam
from sqlalchemy import text

def update_subject_name_cascade(old_name, new_name, course_short_name):
    """
    Update subject name across all related tables when changed
    
    Args:
        old_name: Previous subject name
        new_name: New subject name
        course_short_name: Course short name to limit scope
    """
    with app.app_context():
        try:
            # Update students' subject names
            students_updated = 0
            
            # Update subject_1_name
            result = db.session.execute(text("""
                UPDATE students 
                SET subject_1_name = :new_name 
                WHERE subject_1_name = :old_name 
                AND current_course LIKE :course_pattern
            """), {
                'new_name': new_name,
                'old_name': old_name,
                'course_pattern': f'%{course_short_name}%'
            })
            students_updated += result.rowcount
            
            # Update subject_2_name
            result = db.session.execute(text("""
                UPDATE students 
                SET subject_2_name = :new_name 
                WHERE subject_2_name = :old_name 
                AND current_course LIKE :course_pattern
            """), {
                'new_name': new_name,
                'old_name': old_name,
                'course_pattern': f'%{course_short_name}%'
            })
            students_updated += result.rowcount
            
            # Update subject_3_name
            result = db.session.execute(text("""
                UPDATE students 
                SET subject_3_name = :new_name 
                WHERE subject_3_name = :old_name 
                AND current_course LIKE :course_pattern
            """), {
                'new_name': new_name,
                'old_name': old_name,
                'course_pattern': f'%{course_short_name}%'
            })
            students_updated += result.rowcount
            
            # Update exam records (all 6 possible subjects)
            exams_updated = 0
            
            for i in range(1, 7):
                result = db.session.execute(text(f"""
                    UPDATE exams 
                    SET subject{i}_name = :new_name 
                    WHERE subject{i}_name = :old_name 
                    AND course_id IN (
                        SELECT course_id FROM courses WHERE course_short_name = :course_short_name
                    )
                """), {
                    'new_name': new_name,
                    'old_name': old_name,
                    'course_short_name': course_short_name
                })
                exams_updated += result.rowcount
            
            db.session.commit()
            
            print(f"✓ Updated subject name from '{old_name}' to '{new_name}'")
            print(f"  - Students updated: {students_updated} field(s)")
            print(f"  - Exam records updated: {exams_updated} field(s)")
            
            return True, students_updated, exams_updated
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error updating subject name: {str(e)}")
            return False, 0, 0

if __name__ == '__main__':
    # Example usage:
    # update_subject_name_cascade('Old Subject Name', 'New Subject Name', 'BSC')
    pass
