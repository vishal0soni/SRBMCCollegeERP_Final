
from app import app, db
from models import CollegeFees
import sqlalchemy as sa

def add_fee_management_columns():
    """Add missing fee management columns to college_fees table"""
    
    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.connect()
            
            # List of columns to add with their types
            columns_to_add = [
                ('total_fees_paid', 'NUMERIC(10, 2) DEFAULT 0'),
                ('meera_rebate_applied', 'BOOLEAN DEFAULT FALSE'),
                ('meera_rebate_approved', 'BOOLEAN DEFAULT FALSE'),
                ('meera_rebate_granted', 'BOOLEAN DEFAULT FALSE'),
                ('meera_rebate_amount', 'NUMERIC(10, 2) DEFAULT 0'),
                ('scholarship_applied', 'BOOLEAN DEFAULT FALSE'),
                ('scholarship_approved', 'BOOLEAN DEFAULT FALSE'),
                ('scholarship_granted', 'BOOLEAN DEFAULT FALSE'),
                ('government_scholarship_amount', 'NUMERIC(10, 2) DEFAULT 0'),
                ('total_amount_due', 'NUMERIC(10, 2) DEFAULT 0'),
                ('pending_dues_for_libraries', 'BOOLEAN DEFAULT FALSE'),
                ('pending_dues_for_hostel', 'BOOLEAN DEFAULT FALSE'),
                ('exam_admit_card_issued', 'BOOLEAN DEFAULT FALSE')
            ]
            
            # Add each column if it doesn't exist
            for column_name, column_type in columns_to_add:
                try:
                    # Check if column exists
                    result = connection.execute(sa.text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='college_fees' AND column_name='{column_name}'
                    """))
                    
                    if not result.fetchone():
                        # Add the column
                        connection.execute(sa.text(f"ALTER TABLE college_fees ADD COLUMN {column_name} {column_type}"))
                        print(f"Added column: {column_name}")
                    else:
                        print(f"Column {column_name} already exists")
                        
                except Exception as e:
                    print(f"Error adding column {column_name}: {str(e)}")
            
            connection.commit()
            connection.close()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Migration failed: {str(e)}")

if __name__ == '__main__':
    add_fee_management_columns()
