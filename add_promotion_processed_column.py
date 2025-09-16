
#!/usr/bin/env python3

"""
Migration script to add promotion_processed column to exam table
"""

from app import app, db
from models import Exam

def add_promotion_processed_column():
    """Add promotion_processed column to exam table"""
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('exams')]
            
            if 'promotion_processed' not in columns:
                print("Adding promotion_processed column to exams table...")
                
                # Add the column with default value False
                db.engine.execute('ALTER TABLE exams ADD COLUMN promotion_processed BOOLEAN DEFAULT FALSE')
                
                # Update all existing records to have promotion_processed = False
                db.engine.execute('UPDATE exams SET promotion_processed = FALSE WHERE promotion_processed IS NULL')
                
                print("✓ Successfully added promotion_processed column")
            else:
                print("✓ promotion_processed column already exists")
                
        except Exception as e:
            print(f"✗ Error adding promotion_processed column: {str(e)}")
            raise

if __name__ == "__main__":
    add_promotion_processed_column()
