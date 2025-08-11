#!/usr/bin/env python3
"""
Add total_amount_after_rebate column to college_fees table
This script adds the new total_amount_after_rebate column to existing database records.
"""

import os
import sys
from sqlalchemy import text

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

from app import app, db
from models import CollegeFees

def add_total_amount_after_rebate_column():
    """Add total_amount_after_rebate column to college_fees table."""
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'college_fees' 
                AND column_name = 'total_amount_after_rebate'
            """))
            
            if result.fetchone():
                print("Column 'total_amount_after_rebate' already exists in college_fees table.")
                return
            
            # Add the new column
            print("Adding 'total_amount_after_rebate' column to college_fees table...")
            db.session.execute(text("""
                ALTER TABLE college_fees 
                ADD COLUMN total_amount_after_rebate NUMERIC(10, 2) DEFAULT 0
            """))
            
            # Update existing records to calculate total_amount_after_rebate
            print("Updating existing records to calculate total_amount_after_rebate...")
            db.session.execute(text("""
                UPDATE college_fees 
                SET total_amount_after_rebate = CASE 
                    WHEN meera_rebate_granted = true AND meera_rebate_amount > 0 
                    THEN total_fee - meera_rebate_amount 
                    ELSE total_fee 
                END
            """))
            
            db.session.commit()
            print("Successfully added total_amount_after_rebate column and updated existing records.")
            
            # Verify the update
            count = db.session.execute(text("SELECT COUNT(*) FROM college_fees")).fetchone()[0]
            print(f"Updated {count} college_fees records.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding total_amount_after_rebate column: {str(e)}")
            raise

if __name__ == "__main__":
    add_total_amount_after_rebate_column()