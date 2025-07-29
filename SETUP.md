# The Fit Forge Gym Management System - Quick Setup Guide

## 🚀 Quick Start (System is Already Running!)

Your gym management system is ready to use! Here are the login details:

- **URL**: http://127.0.0.1:8000/
- **Username**: `admin`
- **Password**: `admin123`

## 🎯 Key Features

### ✅ Ready to Use:
- 📊 **Dashboard**: Real-time statistics and insights
- 👥 **Member Management**: Enroll, edit, and track members
- 💰 **Payment Tracking**: Record payments and track dues
- 📧 **Email System**: Welcome emails and payment reminders
- 📈 **Reports**: Revenue analytics and member insights
- ⚡ **Quick Actions**: Fast access to common tasks

### 🎨 User-Friendly Interface:
- Clean, modern card-based design
- Mobile-responsive layout
- Intuitive navigation
- Visual status indicators
- Easy-to-use forms

## 📱 How to Use

### 1. Login
- Go to http://127.0.0.1:8000/
- Click "Staff Login"
- Use: `admin` / `admin123`

### 2. Dashboard Overview
- View member statistics
- Check pending payments
- Monitor expiring memberships
- Quick action buttons

### 3. Member Management
- **Enroll New Member**: Simple form with auto-calculations
- **View Members**: Card view with search and filters
- **Member Details**: Complete profile with payment history
- **Edit Members**: Update information easily

### 4. Quick Actions
- Fast member search
- Process payments quickly
- View expired/expiring memberships
- Generate reports

### 5. Reports
- Member analytics
- Revenue tracking
- Payment summaries
- Export options

## ⚙️ Optional Configuration

### Email Setup (For Production)
To enable real email sending, update `gym_management/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'your-gmail@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Automated Email Reminders
To enable automated emails, install Redis and run Celery:

```bash
# Install Redis (macOS)
brew install redis

# Start Redis
redis-server

# In another terminal, start Celery worker
celery -A gym_management worker --loglevel=info

# In another terminal, start Celery beat (for scheduled emails)
celery -A gym_management beat --loglevel=info
```

## 🔧 System Architecture

- **Backend**: Django 4.2.7
- **Database**: SQLite (included)
- **Frontend**: Bootstrap 5 + Custom CSS
- **Task Queue**: Celery + Redis (optional)
- **Email**: Django email backend

## 📊 Member Fields

The system tracks:
- Personal info (name, email, phone, DOB, address)
- Membership details (type, expiry, status)
- Payment information (amount, pending, history)
- Profile photos
- Automated expiry calculations

## 🎯 Quick Navigation

- **Dashboard**: Overview and statistics
- **Members**: List all members with filters
- **Enroll**: Add new members
- **Quick Actions**: Common tasks
- **Reports**: Analytics and insights

## 🆘 Troubleshooting

### If the server stops:
```bash
cd /Users/kushagraagarwal/Documents/gym
python3 manage.py runserver
```

### To create a new admin user:
```bash
python3 manage.py createsuperuser
```

### To reset the database:
```bash
python3 manage.py migrate --run-syncdb
```

## 🔐 Default Admin Access

The Django admin panel is still available at:
- **URL**: http://127.0.0.1:8000/admin/
- **Username**: `admin`
- **Password**: `admin123`

Use this for advanced configuration and data management.

---

**Your gym management system is ready! Start by enrolling your first member.** 🎉 