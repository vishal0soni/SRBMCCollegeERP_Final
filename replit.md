# SRBMC College Management ERP System

## Overview

The SRBMC College Management ERP System is a comprehensive web-based application designed for Shri Raghunath Bishnoi Memorial College (SRBMC), Raniwara. The system provides a complete solution for managing college operations including student admissions, course management, fee collection, examinations, and administrative tasks. Built with Flask and PostgreSQL, it features a clean, Bootstrap-based interface with role-based access control.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional web application architecture with the following components:

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form handling and validation
- **Email**: Flask-Mail for email notifications
- **PDF Generation**: ReportLab for generating invoices and report cards

### Frontend Architecture
- **Templates**: Jinja2 templating engine
- **CSS Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.0.0 for UI icons
- **Charts**: Chart.js for analytics dashboards
- **JavaScript**: Vanilla JavaScript for interactive features

### Database Design
- **Primary Database**: PostgreSQL
- **ORM**: SQLAlchemy with declarative base model
- **Connection Pooling**: Configured with pool_recycle and pool_pre_ping for reliability

## Key Components

### Authentication & Authorization
- Role-based access control with UserRole and UserProfile models
- Password hashing using Werkzeug security utilities
- Session-based authentication with Flask-Login
- Default users: admin/admin, Vishal/Vishal, Sonali/Sonali
- Access levels: Edit (full access) vs Read (view-only access)

### Core Modules
1. **User Administration**: Complete user management with role assignment
2. **Student Management**: Student admission, profile management, and tracking
3. **Course Management**: Course and subject administration
4. **Fee Management**: Payment processing, invoice generation, and tracking
5. **Examination System**: Exam result management and report card generation
6. **Analytics Dashboard**: Comprehensive reporting and data visualization

### Data Models
- **UserProfile & UserRole**: User management and permissions
- **Student**: Student information and academic records
- **Course & CourseDetails**: Course structure and curriculum
- **Subject**: Subject management per course
- **CollegeFees & Invoice**: Fee structure and payment tracking
- **Exam**: Examination results and grading

## Data Flow

### User Authentication Flow
1. User submits login credentials via LoginForm
2. System validates against UserProfile table with password hash verification
3. Flask-Login manages session state and user context
4. Role-based permissions control access to different modules

### Student Management Flow
1. Admission officers input student data via StudentForm
2. System generates unique student IDs using course and year pattern
3. Student records stored with complete academic and personal information
4. Integration with course and subject selections

### Fee Processing Flow
1. Payment data entered through payment forms
2. System generates unique invoice numbers with date-based pattern
3. PDF invoices generated using ReportLab
4. Email notifications sent for payment confirmations

## External Dependencies

### Python Packages
- **Flask**: Web framework and core functionality
- **SQLAlchemy**: Database ORM and query builder
- **WTForms**: Form validation and rendering
- **ReportLab**: PDF generation for invoices and reports
- **Flask-Mail**: Email service integration
- **Werkzeug**: Security utilities and WSGI support

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework via CDN
- **Font Awesome 6.0.0**: Icon library via CDN
- **Chart.js**: Data visualization via CDN

### Email Configuration
- SMTP integration with configurable mail server settings
- Support for Gmail SMTP (default configuration)
- Environment variable based configuration for security

## Deployment Strategy

### Environment Configuration
- Environment variables for sensitive data (database URL, email credentials)
- Production-ready configuration with ProxyFix middleware
- Database connection pooling for scalability
- Session secret key management

### Database Setup
- PostgreSQL as primary database
- SQLAlchemy migrations for schema management
- Connection string: `postgresql://localhost/srbmc_erp` (configurable via DATABASE_URL)

### Static Assets
- CSS and JavaScript files served from static directory
- CDN integration for external libraries
- Image assets including college logo and branding

### Security Features
- Password hashing with Werkzeug security
- CSRF protection via Flask-WTF
- Session-based authentication
- Role-based access control
- SQL injection protection through SQLAlchemy ORM

The system is designed to be hosted on Replit with all dependencies configured for cloud deployment. The modular architecture allows for easy maintenance and feature expansion while maintaining data integrity and user security.