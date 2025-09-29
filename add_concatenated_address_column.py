
from app import app, db
from models import Student
from sqlalchemy import text

def add_concatenated_address_column():
    """Add concatenated_address column to students table and populate it"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'students' 
                AND column_name = 'concatenated_address'
            """))
            
            if result.fetchone():
                print("✓ concatenated_address column already exists")
            else:
                # Add the column
                db.session.execute(text("""
                    ALTER TABLE students 
                    ADD COLUMN concatenated_address TEXT
                """))
                db.session.commit()
                print("✓ Added concatenated_address column to students table")

            # Update existing records
            students = Student.query.all()
            updated_count = 0
            
            for student in students:
                student.update_concatenated_address()
                updated_count += 1

            db.session.commit()
            print(f"✓ Updated concatenated_address for {updated_count} students")
            
            # Verify the column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'students' 
                AND column_name = 'concatenated_address'
            """))
            
            if result.fetchone():
                print("✓ Column verified in database")
            else:
                print("✗ Column not found after creation")
                
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    add_concatenated_address_column()
