
#!/usr/bin/env python3
"""
Migration script to add apaar_id column to students table
"""

from app import app, db
from sqlalchemy import text

def add_apaar_id_column():
    """Add apaar_id column to students table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='students' AND column_name='apaar_id'
            """))
            
            if result.fetchone() is None:
                # Add the column
                db.session.execute(text("""
                    ALTER TABLE students 
                    ADD COLUMN apaar_id VARCHAR(20)
                """))
                db.session.commit()
                print("Successfully added apaar_id column to students table")
            else:
                print("apaar_id column already exists in students table")
                
        except Exception as e:
            print(f"Error adding apaar_id column: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    add_apaar_id_column()
