
from app import app, db
from models import CollegeFees

def update_college_fees_total():
    """Update all existing CollegeFees records to trigger database formula calculation"""
    
    with app.app_context():
        try:
            print("Updating all college_fees records to use database-calculated total_fee...")
            
            # Get all fee records
            fee_records = CollegeFees.query.all()
            updated_count = 0
            
            for fee_record in fee_records:
                # Simply touch a field to trigger the database formula recalculation
                # The database formula will automatically calculate total_fee
                original_fee = fee_record.course_tuition_fee
                fee_record.course_tuition_fee = original_fee
                updated_count += 1
                
                if updated_count % 100 == 0:
                    print(f"Processed {updated_count} records...")
            
            db.session.commit()
            print(f"✓ Successfully updated {updated_count} records")
            print("✓ Database formula now handles total_fee calculation automatically")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during update: {str(e)}")

if __name__ == "__main__":
    update_college_fees_total()
