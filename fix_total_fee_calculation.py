
def fix_total_fee_calculation():
    """Fix total_fee calculation for all existing CollegeFees records"""
    try:
        # Import here to avoid circular imports when called from routes
        from app import app, db
        from models import CollegeFees
        
        # Don't create new app context if we're already in one
        if hasattr(app, '_get_current_object'):
            # We're likely already in an app context
            _fix_total_fee_calculation_logic(db, CollegeFees)
        else:
            # We need to create an app context
            with app.app_context():
                _fix_total_fee_calculation_logic(db, CollegeFees)
                
    except Exception as e:
        print(f"✗ Error during fee calculation update: {str(e)}")
        # Log but don't raise to avoid breaking the main application flow

def _fix_total_fee_calculation_logic(db, CollegeFees):
    """Internal logic for fixing fee calculations"""
    try:
        print("Syncing total_fee calculation for all college_fees records...")
        
        # Get all fee records
        fee_records = CollegeFees.query.all()
        updated_count = 0
        
        for fee_record in fee_records:
            # Calculate total_fee manually using the same formula as frontend
            old_total = float(fee_record.total_fee or 0)
            
            # Calculate new total using all fee components
            new_total = (
                float(fee_record.total_course_fees or 0) +
                float(fee_record.enrollment_fee or 0) +
                float(fee_record.university_affiliation_fee or 0) +
                float(fee_record.university_sports_fee or 0) +
                float(fee_record.university_development_fee or 0) +
                float(fee_record.tc_cc_fee or 0) +
                float(fee_record.miscellaneous_fee_1 or 0) +
                float(fee_record.miscellaneous_fee_2 or 0) +
                float(fee_record.miscellaneous_fee_3 or 0)
            )
            
            # Update the total_fee field and ensure total_fees_paid is current
            fee_record.total_fee = new_total
            
            # Also update total_fees_paid using the calculated property
            current_paid = fee_record.calculated_total_fees_paid
            if fee_record.total_fees_paid != current_paid:
                fee_record.total_fees_paid = current_paid
            
            if old_total != new_total:
                updated_count += 1
                print(f"Updated student ID {fee_record.student_id}: total_fee {old_total} -> {new_total}")
        
        db.session.commit()
        print(f"✓ Successfully synced {updated_count} fee records")
        print(f"✓ Total records processed: {len(fee_records)}")
        
    except Exception as e:
        db.session.rollback()
        raise e

if __name__ == "__main__":
    fix_total_fee_calculation()
