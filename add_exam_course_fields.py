
from app import app, db
from sqlalchemy import text

def add_exam_course_fields():
    """Add coursedetail_id and course_full_name fields to exams table"""
    
    with app.app_context():
        try:
            # Add coursedetail_id column
            db.session.execute(text("""
                ALTER TABLE exams 
                ADD COLUMN coursedetail_id INTEGER 
                REFERENCES course_details(id)
            """))
            print("✓ Added coursedetail_id column to exams table")
            
            # Add course_full_name column
            db.session.execute(text("""
                ALTER TABLE exams 
                ADD COLUMN course_full_name VARCHAR(200)
            """))
            print("✓ Added course_full_name column to exams table")
            
            # Populate existing records with course_full_name from student's current course
            db.session.execute(text("""
                UPDATE exams 
                SET course_full_name = (
                    SELECT students.current_course 
                    FROM students 
                    WHERE students.id = exams.student_id
                )
                WHERE course_full_name IS NULL
            """))
            print("✓ Populated course_full_name for existing exam records")
            
            # Try to populate coursedetail_id by matching course_full_name
            db.session.execute(text("""
                UPDATE exams 
                SET coursedetail_id = (
                    SELECT cd.id 
                    FROM course_details cd 
                    WHERE cd.course_full_name = exams.course_full_name
                    LIMIT 1
                )
                WHERE coursedetail_id IS NULL AND course_full_name IS NOT NULL
            """))
            print("✓ Populated coursedetail_id for existing exam records where possible")
            
            db.session.commit()
            print("✓ Successfully added course fields to exams table")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding course fields to exams table: {str(e)}")
            raise

if __name__ == '__main__':
    add_exam_course_fields()
