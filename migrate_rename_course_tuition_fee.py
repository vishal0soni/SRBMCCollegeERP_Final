
from app import app, db
from sqlalchemy import text

def migrate_rename_course_tuition_fee():
    """Rename course_tuition_fee column to total_course_fees in college_fees table"""
    
    with app.app_context():
        try:
            # Check if the old column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'college_fees' 
                AND column_name = 'course_tuition_fee'
            """))
            
            if not result.fetchone():
                print("✓ Column course_tuition_fee does not exist or already renamed")
                return
            
            print("Renaming course_tuition_fee to total_course_fees...")
            
            # Rename the column
            db.session.execute(text("""
                ALTER TABLE college_fees 
                RENAME COLUMN course_tuition_fee TO total_course_fees
            """))
            
            db.session.commit()
            print("✓ Successfully renamed course_tuition_fee to total_course_fees")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during migration: {str(e)}")

if __name__ == "__main__":
    migrate_rename_course_tuition_fee()
