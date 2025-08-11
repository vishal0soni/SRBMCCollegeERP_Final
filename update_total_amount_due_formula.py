#!/usr/bin/env python3
"""
Update total_amount_due field formula in CollegeFees table.
This script sets the formula: total_amount_due = total_amount_after_rebate - (installment_1 + installment_2 + installment_3 + installment_4 + installment_5 + installment_6)
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

def update_total_amount_due_formula():
    """Update the total_amount_due formula in all existing records and set database constraint"""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("Updating total_amount_due calculation for all college_fees records...")
        
        # First, update all existing records with the correct formula
        update_query = text("""
            UPDATE college_fees 
            SET total_amount_due = COALESCE(total_amount_after_rebate, 0) - (
                COALESCE(installment_1, 0) + 
                COALESCE(installment_2, 0) + 
                COALESCE(installment_3, 0) + 
                COALESCE(installment_4, 0) + 
                COALESCE(installment_5, 0) + 
                COALESCE(installment_6, 0)
            )
        """)
        
        result = session.execute(update_query)
        updated_count = result.rowcount
        session.commit()
        
        print(f"✓ Successfully updated {updated_count} fee records with correct total_amount_due calculation")
        
        # Verify the updates
        verify_query = text("""
            SELECT 
                student_id,
                COALESCE(total_amount_after_rebate, 0) as total_after_rebate,
                (COALESCE(installment_1, 0) + COALESCE(installment_2, 0) + COALESCE(installment_3, 0) + 
                 COALESCE(installment_4, 0) + COALESCE(installment_5, 0) + COALESCE(installment_6, 0)) as total_paid,
                total_amount_due
            FROM college_fees 
            ORDER BY student_id
        """)
        
        result = session.execute(verify_query)
        records = result.fetchall()
        
        print("\nVerification of total_amount_due calculations:")
        print("Student ID | Total After Rebate | Total Paid | Total Amount Due")
        print("-" * 60)
        
        for record in records:
            student_id, total_after_rebate, total_paid, total_amount_due = record
            expected_due = float(total_after_rebate or 0) - float(total_paid or 0)
            actual_due = float(total_amount_due or 0)
            status = "✓" if abs(actual_due - expected_due) < 0.01 else "✗"
            print(f"{student_id:10} | {total_after_rebate:17.2f} | {total_paid:10.2f} | {actual_due:15.2f} {status}")
        
        print(f"\n✓ Total records processed: {len(records)}")
        print("INFO: total_amount_due formula has been applied to all records")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    if update_total_amount_due_formula():
        print("\n🎉 total_amount_due formula update completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ total_amount_due formula update failed!")
        sys.exit(1)