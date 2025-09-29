
from app import app, db
from models import Student

def update_concatenated_address_format():
    """Update all existing concatenated_address fields to use comma separator and exclude NaN values"""
    
    with app.app_context():
        try:
            print("Updating concatenated_address format for all students...")
            
            students = Student.query.all()
            updated_count = 0
            
            for student in students:
                old_address = student.concatenated_address
                
                # Update using the new format
                student.update_concatenated_address()
                
                if old_address != student.concatenated_address:
                    updated_count += 1
                    print(f"Updated student {student.student_unique_id}: '{old_address}' -> '{student.concatenated_address}'")
            
            db.session.commit()
            print(f"✓ Successfully updated {updated_count} student records")
            print(f"✓ Total students processed: {len(students)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error updating concatenated addresses: {str(e)}")

if __name__ == "__main__":
    update_concatenated_address_format()
