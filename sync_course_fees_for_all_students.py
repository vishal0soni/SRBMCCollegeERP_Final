
from app import app, db
from models import CollegeFees, Student, CourseDetails

def sync_course_fees_for_all_students():
    """Sync total_course_fees from course_details for all students"""
    
    with app.app_context():
        try:
            print("Syncing total_course_fees from course_details for all students...")
            
            # Get all fee records with associated students
            fee_records = db.session.query(CollegeFees, Student).join(Student).all()
            updated_count = 0
            
            for fee_record, student in fee_records:
                if student.current_course:
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
                            print(f"Updated student {student.student_unique_id} ({student.first_name} {student.last_name}): {old_value} -> {new_value}")
                    else:
                        print(f"No course details found for student {student.student_unique_id} with course: {student.current_course}")
                else:
                    print(f"Student {student.student_unique_id} has no current_course assigned")
            
            db.session.commit()
            print(f"✓ Successfully synced {updated_count} records")
            print(f"✓ Total records processed: {len(fee_records)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during sync: {str(e)}")

if __name__ == "__main__":
    sync_course_fees_for_all_students()
