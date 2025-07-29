from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import date, timedelta
from .models import Member


@shared_task
def send_welcome_email(member_id):
    """Send welcome email to new member"""
    try:
        member = Member.objects.get(id=member_id)
        
        subject = f'Welcome to Our Gym - {member.name}!'
        
        html_message = render_to_string('emails/welcome_email.html', {
            'member': member,
            'gym_name': 'The Fit Forge Gym',
            'gym_address': '123 Fitness Street, Health City',
            'gym_phone': '+91-9876543210',
            'gym_email': 'info@fitlifegym.com',
        })
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member.email],
            fail_silently=False,
        )
        
        return f"Welcome email sent to {member.email}"
        
    except Member.DoesNotExist:
        return f"Member with ID {member_id} not found"
    except Exception as e:
        return f"Error sending welcome email: {str(e)}"


@shared_task
def send_payment_reminder_email(member_id):
    """Send payment reminder email to member"""
    try:
        member = Member.objects.get(id=member_id)
        
        if not member.has_pending_payment:
            return f"No pending payment for {member.name}"
        
        subject = f'Payment Reminder - {member.name}'
        
        html_message = render_to_string('emails/payment_reminder.html', {
            'member': member,
            'gym_name': 'The Fit Forge Gym',
            'gym_phone': '+91-9876543210',
            'gym_email': 'info@fitlifegym.com',
        })
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member.email],
            fail_silently=False,
        )
        
        return f"Payment reminder sent to {member.email}"
        
    except Member.DoesNotExist:
        return f"Member with ID {member_id} not found"
    except Exception as e:
        return f"Error sending payment reminder: {str(e)}"


@shared_task
def send_weekly_payment_reminders():
    """Send payment reminders to all members with pending payments - runs weekly"""
    members_with_pending = Member.objects.filter(
        pending_amount__gt=0,
        is_active=True
    )
    
    sent_count = 0
    for member in members_with_pending:
        try:
            send_payment_reminder_email.delay(member.id)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send reminder to {member.name}: {str(e)}")
    
    return f"Weekly payment reminders queued for {sent_count} members"


@shared_task
def send_membership_expiry_reminders():
    """Send membership expiry reminders - runs daily"""
    # Members expiring in 7 days
    expiring_soon = Member.objects.filter(
        expiry_date__gte=date.today(),
        expiry_date__lte=date.today() + timedelta(days=7),
        is_active=True
    )
    
    sent_count = 0
    for member in expiring_soon:
        try:
            subject = f'Membership Expiry Reminder - {member.name}'
            
            html_message = render_to_string('emails/expiry_reminder.html', {
                'member': member,
                'gym_name': 'The Fit Forge Gym',
                'gym_phone': '+91-9876543210',
                'gym_email': 'info@fitlifegym.com',
            })
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member.email],
                fail_silently=False,
            )
            
            sent_count += 1
            
        except Exception as e:
            print(f"Failed to send expiry reminder to {member.name}: {str(e)}")
    
    return f"Expiry reminders sent to {sent_count} members" 