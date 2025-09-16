
#!/usr/bin/env python3

"""
Migration script to add promotion_processed column to exams table
"""

from app import app, db
from sqlalchemy import text

def add_promotion_processed_column():
    """Add promotion_processed column to exams table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'exams' 
                AND column_name = 'promotion_processed'
            """))
            
            if result.fetchone():
                print("✓ promotion_processed column already exists")
                return
            
            print("Adding promotion_processed column to exams table...")
            
            # Add the column with default value False
            db.session.execute(text("""
                ALTER TABLE exams 
                ADD COLUMN promotion_processed BOOLEAN DEFAULT FALSE
            """))
            
            # Update all existing records to have promotion_processed = FALSE
            db.session.execute(text("""
                UPDATE exams 
                SET promotion_processed = FALSE 
                WHERE promotion_processed IS NULL
            """))
            
            db.session.commit()
            print("✓ Successfully added promotion_processed column")
            
            # Verify the column was added
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'exams' 
                AND column_name = 'promotion_processed'
            """))
            
            if result.fetchone():
                print("✓ Column verified in database")
            else:
                print("✗ Column not found after creation")
                
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding promotion_processed column: {str(e)}")
            raise

if __name__ == "__main__":
    add_promotion_processed_column()
