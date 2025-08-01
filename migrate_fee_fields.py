
from app import app, db
from sqlalchemy import text

def migrate_fee_fields():
    """Add new fee management fields to college_fees table"""
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'college_fees' 
                AND column_name = 'total_fees_paid'
            """))
            
            if result.fetchone():
                print("✓ Fee management fields already exist")
                return
            
            print("Adding new fee management fields...")
            
            # Add new columns to college_fees table
            alter_statements = [
                "ALTER TABLE college_fees ADD COLUMN total_fees_paid NUMERIC(10, 2) DEFAULT 0",
                "ALTER TABLE college_fees ADD COLUMN meera_rebate_applied BOOLEAN DEFAULT FALSE",
                "ALTER TABLE college_fees ADD COLUMN meera_rebate_approved BOOLEAN DEFAULT FALSE", 
                "ALTER TABLE college_fees ADD COLUMN meera_rebate_granted BOOLEAN DEFAULT FALSE",
                "ALTER TABLE college_fees ADD COLUMN meera_rebate_amount NUMERIC(10, 2) DEFAULT 0",
                "ALTER TABLE college_fees ADD COLUMN scholarship_applied BOOLEAN DEFAULT FALSE",
                "ALTER TABLE college_fees ADD COLUMN scholarship_approved BOOLEAN DEFAULT FALSE",
                "ALTER TABLE college_fees ADD COLUMN scholarship_granted BOOLEAN DEFAULT FALSE",
                "ALTER TABLE college_fees ADD COLUMN government_scholarship_amount NUMERIC(10, 2) DEFAULT 0",
                "ALTER TABLE college_fees ADD COLUMN total_amount_due NUMERIC(10, 2) DEFAULT 0",
                "ALTER TABLE college_fees ADD COLUMN pending_dues_for_libraries BOOLEAN DEFAULT FALSE",
                "ALTER TABLE college_fees ADD COLUMN pending_dues_for_hostel BOOLEAN DEFAULT FALSE",
                "ALTER TABLE college_fees ADD COLUMN exam_admit_card_issued BOOLEAN DEFAULT FALSE"
            ]
            
            for statement in alter_statements:
                print(f"Executing: {statement}")
                db.session.execute(text(statement))
            
            db.session.commit()
            print("✓ Successfully added all fee management fields")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_fee_fields()
