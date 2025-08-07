import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/srbmc_erp")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 20,
        "pool_size": 10,
        "max_overflow": 0,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "SRBMC_ERP"
        }
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Disable caching for development
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@srbmc.edu.in')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Proxy fix for production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    with app.app_context():
        # Import models to ensure tables are created
        from models import UserProfile, UserRole, Student, Course, CourseDetails, Subject, CollegeFees, Invoice, Exam
        
        try:
            # Create database tables
            db.create_all()
            
            # Create default roles and users
            create_default_data()
        except Exception as e:
            print(f"Database initialization error: {e}")
            print("Please check your database connection and try again.")
    
    return app

def create_default_data():
    """Create default roles and users if they don't exist"""
    from models import UserRole, UserProfile
    from werkzeug.security import generate_password_hash
    
    # Create default roles
    roles_data = [
        {'role_name': 'Administrator', 'role_description': 'Full system access', 'access_type': 'Edit', 'access_level': 1},
        {'role_name': 'Admission Officer', 'role_description': 'Student admission management', 'access_type': 'Edit', 'access_level': 2},
        {'role_name': 'Accountant', 'role_description': 'Financial management', 'access_type': 'Edit', 'access_level': 3},
        {'role_name': 'Exam Controller', 'role_description': 'Examination management', 'access_type': 'Edit', 'access_level': 4},
        {'role_name': 'Admission Assistant', 'role_description': 'View admission records', 'access_type': 'Read', 'access_level': 5},
        {'role_name': 'Accountant Assistant', 'role_description': 'View financial records', 'access_type': 'Read', 'access_level': 6},
        {'role_name': 'Exam Assistant', 'role_description': 'View exam records', 'access_type': 'Read', 'access_level': 7},
    ]
    
    for role_data in roles_data:
        if not UserRole.query.filter_by(role_name=role_data['role_name']).first():
            role = UserRole(**role_data)
            db.session.add(role)
    
    db.session.commit()
    
    # Create default users
    admin_role = UserRole.query.filter_by(role_name='Administrator').first()
    
    default_users = [
        {'username': 'admin', 'password': 'admin', 'first_name': 'System', 'last_name': 'Administrator', 'email': 'admin@srbmc.edu.in'},
        {'username': 'Vishal', 'password': 'Vishal', 'first_name': 'Vishal', 'last_name': 'Kumar', 'email': 'vishal@srbmc.edu.in'},
        {'username': 'Sonali', 'password': 'Sonali', 'first_name': 'Sonali', 'last_name': 'Sharma', 'email': 'sonali@srbmc.edu.in'},
    ]
    
    for user_data in default_users:
        if not UserProfile.query.filter_by(username=user_data['username']).first():
            user = UserProfile(
                role_id=admin_role.role_id,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                username=user_data['username'],
                password_hash=generate_password_hash(user_data['password']),
                status='Active'
            )
            db.session.add(user)
    
    db.session.commit()

# Create app instance
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from models import UserProfile
    return UserProfile.query.get(int(user_id))
