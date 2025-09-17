
from app import app, db
from models import CollegeFees, Student, CourseDetails, Course
import sqlalchemy as sa

def add_course_fields_to_fees():
    """Add coursedetail_id and course_full_name columns to college_fees table"""
    
    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.connect()
            
            # Add coursedetail_id column
            try:
                result = connection.execute(sa.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='college_fees' AND column_name='coursedetail_id'
                """))
                
                if not result.fetchone():
                    connection.execute(sa.text("ALTER TABLE college_fees ADD COLUMN coursedetail_id INTEGER REFERENCES course_details(id)"))
                    print("✓ Added coursedetail_id column to college_fees table")
                else:
                    print("✓ coursedetail_id column already exists")
                    
            except Exception as e:
                print(f"Error adding coursedetail_id column: {str(e)}")
            
            # Add course_full_name column
            try:
                result = connection.execute(sa.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='college_fees' AND column_name='course_full_name'
                """))
                
                if not result.fetchone():
                    connection.execute(sa.text("ALTER TABLE college_fees ADD COLUMN course_full_name VARCHAR(200)"))
                    print("✓ Added course_full_name column to college_fees table")
                else:
                    print("✓ course_full_name column already exists")
                    
            except Exception as e:
                print(f"Error adding course_full_name column: {str(e)}")
            
            connection.commit()
            
            # Now populate existing records with course information
            print("Populating course_full_name for existing fee records...")
            fee_records = CollegeFees.query.all()
            
            for fee_record in fee_records:
                if not fee_record.course_full_name and fee_record.student:
                    student = fee_record.student
                    if student.current_course:
                        # Set course_full_name from student's current course
                        fee_record.course_full_name = student.current_course
                        
                        # Try to find and set coursedetail_id
                        course_detail = CourseDetails.query.filter_by(course_full_name=student.current_course).first()
                        if course_detail:
                            fee_record.coursedetail_id = course_detail.id
                        
                        print(f"Updated fee record for student {student.student_unique_id}")
            
            db.session.commit()
            connection.close()
            print("✓ Successfully added course fields to college_fees table")
            
        except Exception as e:
            print(f"Migration failed: {str(e)}")

if __name__ == '__main__':
    add_course_fields_to_fees()
