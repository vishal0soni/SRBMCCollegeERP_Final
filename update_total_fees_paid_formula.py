
from app import app, db
from models import CollegeFees

def update_total_fees_paid_formula():
    """Update all existing CollegeFees records to trigger database formula calculation for total_fees_paid"""
    
    with app.app_context():
        try:
            print("Updating all college_fees records to use database-calculated total_fees_paid...")
            
            # Get all fee records
            fee_records = CollegeFees.query.all()
            updated_count = 0
            
            for fee_record in fee_records:
                # Simply touch a field to trigger the database formula recalculation
                # The database formula will automatically calculate total_fees_paid
                original_installment = fee_record.installment_1
                fee_record.installment_1 = original_installment
                updated_count += 1
                
                if updated_count % 100 == 0:
                    print(f"Processed {updated_count} records...")
            
            db.session.commit()
            print(f"✓ Successfully updated {updated_count} records")
            print("✓ Database formula now handles total_fees_paid calculation automatically")
            print("✓ total_fees_paid = installment_1 + installment_2 + installment_3 + installment_4 + installment_5 + installment_6")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during update: {str(e)}")

if __name__ == "__main__":
    update_total_fees_paid_formula()
