import os
from app import app

def check_database_connection():
    """Quick database connection check"""
    try:
        from app import db
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(db.text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Please enable your database in the Database tab and try again.")
        return False

# Import routes after app creation to avoid circular imports - Testing 123
with app.app_context():
    import routes  # noqa: F401

if __name__ == "__main__":
    if check_database_connection():
        print("Starting Flask application...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("Cannot start application due to database connection issues.")
