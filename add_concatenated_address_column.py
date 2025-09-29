
from app import app, db
from models import Student

def add_concatenated_address_column():
    """Add concatenated_address column to students table and populate it"""
    with app.app_context():
        try:
            # Add the column if it doesn't exist
            try:
                db.engine.execute('ALTER TABLE students ADD COLUMN concatenated_address TEXT')
                print("✓ Added concatenated_address column to students table")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("✓ concatenated_address column already exists")
                else:
                    print(f"Error adding column: {e}")
                    return

            # Update existing records
            students = Student.query.all()
            updated_count = 0
            
            for student in students:
                student.update_concatenated_address()
                updated_count += 1

            db.session.commit()
            print(f"✓ Updated concatenated_address for {updated_count} students")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    add_concatenated_address_column()
