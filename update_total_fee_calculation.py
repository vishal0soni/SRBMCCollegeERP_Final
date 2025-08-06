
from app import app, db
from models import CollegeFees

def update_all_total_fee_calculations():
    """Update all existing CollegeFees records to calculate total_fee from component fees"""
    
    with app.app_context():
        try:
            print("Updating all total_fee values to match component fee sums...")
            
            # Get all fee records
            fee_records = CollegeFees.query.all()
            updated_count = 0
            
            for fee_record in fee_records:
                old_total = float(fee_record.total_fee or 0)
                fee_record.update_total_fee()
                new_total = float(fee_record.total_fee or 0)
                
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
    update_all_total_fee_calculations()
