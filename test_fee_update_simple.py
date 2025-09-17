
from app import app, db
from models import CollegeFees

def test_fee_field_updates():
    """Test fee field updates directly"""
    with app.app_context():
        print("=== Testing Fee Field Updates ===")
        
        # Get first fee record
        fee_record = CollegeFees.query.first()
        if not fee_record:
            print("No fee records found in database")
            return
            
        print(f"Testing with fee record ID: {fee_record.id}")
        
        # Test each field
        fields = ['pending_dues_for_libraries', 'pending_dues_for_hostel', 'exam_admit_card_issued']
        
        for field in fields:
            print(f"\n--- Testing {field} ---")
            
            try:
                # Get current value
                old_value = getattr(fee_record, field)
                print(f"Current value: {old_value} (type: {type(old_value)})")
                
                # Toggle value
                new_value = not bool(old_value)
                print(f"Setting to: {new_value}")
                
                # Update
                setattr(fee_record, field, new_value)
                
                # Commit
                db.session.commit()
                print("Committed successfully")
                
                # Verify
                updated_record = CollegeFees.query.get(fee_record.id)
                actual_value = getattr(updated_record, field)
                print(f"Verified value: {actual_value} (type: {type(actual_value)})")
                
                if bool(actual_value) == bool(new_value):
                    print("✓ UPDATE SUCCESSFUL")
                else:
                    print("✗ UPDATE FAILED - Value mismatch")
                    
            except Exception as e:
                print(f"✗ ERROR: {e}")
                db.session.rollback()

if __name__ == "__main__":
    test_fee_field_updates()
