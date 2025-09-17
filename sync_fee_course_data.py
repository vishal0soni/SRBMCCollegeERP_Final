
#!/usr/bin/env python3

from app import app, db
from models import CollegeFees, Student, Course, CourseDetails

def sync_fee_course_data():
    """Sync course data for all existing fee records"""
    with app.app_context():
        print("Starting fee course data synchronization...")
        
        # Get all fee records that don't have course information
        fee_records = CollegeFees.query.all()
        updated_count = 0
        
        for fee_record in fee_records:
            student = Student.query.get(fee_record.student_id)
            if not student:
                continue
                
            needs_update = False
            
            # Update course_full_name if missing or different from student's current course
            if not fee_record.course_full_name and student.current_course:
                fee_record.course_full_name = student.current_course
                needs_update = True
                print(f"Updated course_full_name for student {student.student_unique_id}: {student.current_course}")
            
            # Update coursedetail_id and course_id if missing
            if student.current_course and (not fee_record.coursedetail_id or not fee_record.course_id):
                # Find course detail by exact match
                course_detail = CourseDetails.query.filter_by(course_full_name=student.current_course).first()
                
                if course_detail:
                    if not fee_record.coursedetail_id:
                        fee_record.coursedetail_id = course_detail.id
                        needs_update = True
                        print(f"Updated coursedetail_id for student {student.student_unique_id}: {course_detail.id}")
                    
                    # Get course from course_detail
                    course = Course.query.filter_by(course_short_name=course_detail.course_short_name).first()
                    if course and not fee_record.course_id:
                        fee_record.course_id = course.course_id
                        needs_update = True
                        print(f"Updated course_id for student {student.student_unique_id}: {course.course_id}")
                
                # If no exact match, try to find by course short name pattern
                elif not course_detail and student.current_course:
                    course_parts = student.current_course.split(' ')
                    if course_parts:
                        potential_short_name = course_parts[0]
                        course = Course.query.filter_by(course_short_name=potential_short_name).first()
                        if course and not fee_record.course_id:
                            fee_record.course_id = course.course_id
                            needs_update = True
                            print(f"Updated course_id (by pattern) for student {student.student_unique_id}: {course.course_id}")
                            
                            # Try to find matching course detail
                            course_detail = CourseDetails.query.filter_by(course_short_name=potential_short_name).first()
                            if course_detail and not fee_record.coursedetail_id:
                                fee_record.coursedetail_id = course_detail.id
                                needs_update = True
                                print(f"Updated coursedetail_id (by pattern) for student {student.student_unique_id}: {course_detail.id}")
            
            if needs_update:
                updated_count += 1
        
        # Commit all changes
        if updated_count > 0:
            db.session.commit()
            print(f"✓ Successfully updated course data for {updated_count} fee records")
        else:
            print("✓ No fee records needed course data updates")
        
        print("Fee course data synchronization completed!")

if __name__ == "__main__":
    sync_fee_course_data()
