
from app import app, db
from models import CollegeFees, CourseDetails, Course, Student

def sync_total_course_fees():
    """Sync total_course_fees in college_fees from course_details.total_course_fees"""
    
    with app.app_context():
        try:
            print("Syncing total_course_fees from course_details...")
            
            # Get all fee records
            fee_records = CollegeFees.query.all()
            updated_count = 0
            
            for fee_record in fee_records:
                # Get student to find current course
                student = Student.query.get(fee_record.student_id)
                if not student or not student.current_course:
                    continue
                
                # Find corresponding course_details record
                course_detail = CourseDetails.query.filter_by(
                    course_full_name=student.current_course
                ).first()
                
                if course_detail and course_detail.total_course_fees:
                    old_value = float(fee_record.total_course_fees or 0)
                    new_value = float(course_detail.total_course_fees)
                    
                    if old_value != new_value:
                        fee_record.total_course_fees = new_value
                        updated_count += 1
                        print(f"Updated student {student.student_unique_id}: {old_value} -> {new_value}")
            
            db.session.commit()
            print(f"✓ Successfully synced {updated_count} records")
            print(f"✓ Total records processed: {len(fee_records)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during sync: {str(e)}")

if __name__ == "__main__":
    sync_total_course_fees()
