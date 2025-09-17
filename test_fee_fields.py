
#!/usr/bin/env python3

from app import app, db
from models import CollegeFees, Student
from sqlalchemy import inspect

def test_fee_fields():
    """Test fee field database operations"""
    with app.app_context():
        try:
            # Check if columns exist
            inspector = inspect(db.engine)
            columns = inspector.get_columns('college_fees')
            column_names = [col['name'] for col in columns]
            
            required_fields = ['pending_dues_for_libraries', 'pending_dues_for_hostel', 'exam_admit_card_issued']
            
            print("=== Column Check ===")
            for field in required_fields:
                exists = field in column_names
                print(f"{field}: {'EXISTS' if exists else 'MISSING'}")
                
                if exists:
                    # Get column info
                    col_info = next((col for col in columns if col['name'] == field), None)
                    if col_info:
                        print(f"  Type: {col_info['type']}")
                        print(f"  Nullable: {col_info.get('nullable', 'Unknown')}")
                        print(f"  Default: {col_info.get('default', 'None')}")
            
            # Test with actual data
            print("\n=== Data Test ===")
            fee_record = CollegeFees.query.first()
            if fee_record:
                print(f"Testing with fee record ID: {fee_record.id}")
                
                for field in required_fields:
                    try:
                        old_value = getattr(fee_record, field)
                        print(f"{field}: Current value = {old_value} (type: {type(old_value)})")
                        
                        # Test update
                        new_value = not bool(old_value)
                        setattr(fee_record, field, new_value)
                        print(f"{field}: Set to {new_value}")
                        
                    except AttributeError as e:
                        print(f"{field}: ERROR - {e}")
                    except Exception as e:
                        print(f"{field}: UNEXPECTED ERROR - {e}")
                
                # Commit changes
                try:
                    db.session.commit()
                    print("\nCommit: SUCCESS")
                    
                    # Verify changes
                    updated_record = CollegeFees.query.get(fee_record.id)
                    for field in required_fields:
                        try:
                            actual_value = getattr(updated_record, field)
                            print(f"{field}: Verified value = {actual_value} (type: {type(actual_value)})")
                        except Exception as e:
                            print(f"{field}: Verification ERROR - {e}")
                            
                except Exception as e:
                    db.session.rollback()
                    print(f"Commit: FAILED - {e}")
            else:
                print("No fee records found in database")
                
        except Exception as e:
            print(f"Test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_fee_fields()
