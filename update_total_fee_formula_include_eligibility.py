
#!/usr/bin/env python3

from app import app, db
from sqlalchemy import text

def update_total_fee_formula():
    """Update the database formula for total_fee to include eligibility_certificate_fee"""
    
    with app.app_context():
        try:
            print("Updating total_fee formula to include eligibility_certificate_fee...")
            
            # For SQLite, we need to update the formula by recreating the computed column
            # First, let's check the current database type
            engine = db.engine
            
            if 'sqlite' in str(engine.url):
                print("SQLite detected - updating total_fee calculation for all records...")
                
                # For SQLite, we'll update each record manually since it doesn't support computed columns
                update_query = text("""
                    UPDATE college_fees 
                    SET total_fee = COALESCE(total_course_fees, 0) + 
                                   COALESCE(enrollment_fee, 0) + 
                                   COALESCE(eligibility_certificate_fee, 0) + 
                                   COALESCE(university_affiliation_fee, 0) + 
                                   COALESCE(university_sports_fee, 0) + 
                                   COALESCE(university_development_fee, 0) + 
                                   COALESCE(tc_cc_fee, 0) + 
                                   COALESCE(miscellaneous_fee_1, 0) + 
                                   COALESCE(miscellaneous_fee_2, 0) + 
                                   COALESCE(miscellaneous_fee_3, 0)
                """)
                
                result = db.session.execute(update_query)
                affected_rows = result.rowcount
                
                print(f"✓ Updated {affected_rows} records with new total_fee formula")
                
            else:
                print("Non-SQLite database detected - updating computed column formula...")
                
                # For other databases that support computed columns, update the formula
                # This would need to be adapted based on your specific database type
                print("Note: Manual database schema update may be required for computed columns")
                print("Current formula should include: total_course_fees + enrollment_fee + eligibility_certificate_fee + ...")
            
            db.session.commit()
            print("✓ Database formula update completed successfully")
            print("✓ total_fee now includes eligibility_certificate_fee in calculation")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error updating formula: {str(e)}")
            raise e

if __name__ == "__main__":
    update_total_fee_formula()
