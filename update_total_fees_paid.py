
from app import app, db
from models import CollegeFees
from sqlalchemy import text

def update_all_total_fees_paid():
    """Update all existing CollegeFees records to calculate total_fees_paid from installments"""
    
    with app.app_context():
        try:
            print("Updating all total_fees_paid values to match installment sums...")
            
            # Get all fee records
            fee_records = CollegeFees.query.all()
            updated_count = 0
            
            for fee_record in fee_records:
                old_total = float(fee_record.total_fees_paid or 0)
                fee_record.update_total_fees_paid()
                new_total = float(fee_record.total_fees_paid or 0)
                
                if old_total != new_total:
                    updated_count += 1
                    print(f"Updated record ID {fee_record.id}: {old_total} -> {new_total}")
            
            db.session.commit()
            print(f"✓ Successfully updated {updated_count} records")
            print(f"✓ Total records processed: {len(fee_records)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during update: {str(e)}")

if __name__ == "__main__":
    update_all_total_fees_paid()
