
#!/usr/bin/env python3
"""
Migration script to rename dropout_status column to student_status in students table
and update the values to include 'Graduated'
"""

from app import app, db
from sqlalchemy import text

def migrate_rename_dropout_status():
    """Rename dropout_status column to student_status in students table"""
    with app.app_context():
        try:
            # Check if the old column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'students' 
                AND column_name = 'dropout_status'
            """))
            
            if not result.fetchone():
                print("✓ Column dropout_status does not exist or already renamed")
                return
            
            print("Renaming dropout_status to student_status...")
            
            # Rename the column
            db.session.execute(text("""
                ALTER TABLE students 
                RENAME COLUMN dropout_status TO student_status
            """))
            
            # Update the default value from 'Active' to 'Active' (keeping the same)
            # The new possible values will be: 'Active', 'Dropout', 'Graduated'
            
            db.session.commit()
            print("✓ Successfully renamed dropout_status to student_status")
            
            # Show current status distribution
            result = db.session.execute(text("""
                SELECT student_status, COUNT(*) as count
                FROM students 
                GROUP BY student_status
            """))
            
            print("\nCurrent student status distribution:")
            for row in result:
                print(f"  {row[0]}: {row[1]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during migration: {str(e)}")

if __name__ == "__main__":
    migrate_rename_dropout_status()
