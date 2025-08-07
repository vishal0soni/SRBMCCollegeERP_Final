
from app import app, db
from models import CollegeFees

def fix_total_fee_calculation():
    """Fix total_fee calculation for all existing CollegeFees records"""
    
    with app.app_context():
        try:
            print("Fixing total_fee calculation for all college_fees records...")
            
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
                
                # Update the total_fee field
                fee_record.total_fee = new_total
                
                if old_total != new_total:
                    updated_count += 1
                    print(f"Updated student ID {fee_record.student_id}: {old_total} -> {new_total}")
            
            db.session.commit()
            print(f"✓ Successfully updated {updated_count} records")
            print(f"✓ Total records processed: {len(fee_records)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during update: {str(e)}")

if __name__ == "__main__":
    fix_total_fee_calculation()
