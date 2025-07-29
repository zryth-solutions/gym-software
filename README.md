# The Fit Forge Gym Management System

A comprehensive Django-based gym management system for managing members, payments, and operations.

## Features

### 📋 Core Features
- **Member Enrollment**: Register new gym members with complete personal and membership details
- **Member Management**: View, edit, and manage all gym members with advanced filtering
- **Payment Tracking**: Track payments, pending amounts, and payment history
- **Admin Interface**: Full Django admin panel for comprehensive management
- **Email Notifications**: Automated welcome emails and payment reminders
- **Reports & Analytics**: Member statistics and revenue reports

### 🔐 Authentication & Security
- Django admin login system
- Role-based access control
- Secure member data handling

### 📧 Email Features
- Welcome emails for new members with gym information and services
- Weekly payment reminders for pending payments
- Membership expiry notifications
- Customizable email templates

### 📊 Reporting & Analytics
- Member statistics dashboard
- Payment tracking and revenue reports
- Membership type distribution
- Expiring memberships alerts

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (default, configurable)
- **Task Queue**: Celery with Redis
- **Email**: Django email backend (console for development)
- **Frontend**: Bootstrap 5 with responsive design
- **Icons**: Font Awesome

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**
   - Main Application: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

### Email Configuration (Optional)

For production email sending, update `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Celery Setup (Optional)

For automated email reminders:

1. **Install Redis** (for task queue)
2. **Start Celery Worker**
   ```bash
   celery -A gym_management worker --loglevel=info
   ```
3. **Start Celery Beat** (for scheduled tasks)
   ```bash
   celery -A gym_management beat --loglevel=info
   ```

## Usage

### Default Login Credentials
- **Username**: admin
- **Password**: admin123

### Member Management

1. **Enroll New Member**
   - Navigate to "Enroll Member"
   - Fill in personal and membership details
   - System auto-calculates expiry dates based on membership type

2. **View Members**
   - Access comprehensive member listing
   - Use filters for membership type, status, payment status
   - Pagination for large member lists

3. **Payment Management**
   - Track pending payments
   - Add payment records
   - View payment history

### Email Features

- **Welcome Emails**: Automatically sent when new members are enrolled
- **Payment Reminders**: Weekly automated reminders for pending payments
- **Expiry Alerts**: Daily notifications for expiring memberships

## Database Schema

### Member Model
- Personal information (name, email, phone, DOB, address)
- Membership details (type, expiry, payment info)
- Status tracking (active, expired, pending payments)

### Payment History Model
- Payment tracking per member
- Transaction details and notes
- Payment method records

## File Structure

```
gym/
├── gym_management/          # Django project
├── members/                 # Main app
│   ├── models.py           # Member and PaymentHistory models
│   ├── views.py            # Views for enrollment, listing, dashboard
│   ├── forms.py            # Forms for member management
│   ├── admin.py            # Admin configuration
│   ├── tasks.py            # Celery tasks for emails
│   └── urls.py             # URL patterns
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── members/            # Member-specific templates
│   └── emails/             # Email templates
├── static/                 # Static files (CSS, JS)
├── media/                  # User uploads (profile pictures)
└── requirements.txt        # Dependencies
```

## API Documentation

The system provides a web interface. For programmatic access, Django REST Framework can be added.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For questions or issues:
- Check the Django documentation
- Review the admin interface for member management
- Check email templates in `templates/emails/`

## License

This project is built with Django and follows standard Django practices for gym management operations. 