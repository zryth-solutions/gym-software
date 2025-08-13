from django.db import models
from django.core.validators import RegexValidator
from datetime import date, timedelta
from django.utils import timezone


class Member(models.Model):
    MEMBERSHIP_TYPES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]
    
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('cheque', 'Cheque'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Personal Information
    name = models.CharField(max_length=100, help_text="Full name of the member")
    email = models.EmailField(unique=True, blank=True, null=True, help_text="Email address for communication (optional)")
    mobile_phone = models.CharField(
        max_length=15,
        help_text="Contact number"
    )
    date_of_birth = models.DateField(blank=True, null=True, help_text="Date of birth (optional)")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    address = models.TextField(blank=True, help_text="Complete address (optional)")
    
    # Membership Information
    member_since = models.DateField(default=date.today, help_text="Date when member joined")
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES, default='monthly')
    expiry_date = models.DateField(blank=True, null=True, help_text="Membership expiry date (auto-calculated if not provided)")
    
    # Payment Information
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total membership fee")
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Amount pending")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='cash')
    
    # Status and metadata
    is_active = models.BooleanField(default=True, help_text="Is membership active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Profile picture (optional)
    profile_picture = models.ImageField(upload_to='member_photos/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Gym Member"
        verbose_name_plural = "Gym Members"
    
    def __str__(self):
        return f"{self.name} - {self.membership_type.capitalize()}"
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def is_membership_expired(self):
        """Check if membership has expired"""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date
    
    @property
    def days_until_expiry(self):
        """Calculate days until membership expires"""
        if not self.expiry_date:
            return 0
        return (self.expiry_date - date.today()).days
    
    @property
    def has_pending_payment(self):
        """Check if member has pending payment"""
        return self.pending_amount > 0
    
    def save(self, *args, **kwargs):
        # Set member_since to today if not provided
        if not self.member_since:
            self.member_since = date.today()
        
        # Auto-calculate expiry date based on membership type if not provided
        if not self.expiry_date:
            if self.membership_type == 'weekly':
                self.expiry_date = self.member_since + timedelta(weeks=1)
            elif self.membership_type == 'monthly':
                self.expiry_date = self.member_since + timedelta(days=30)
            elif self.membership_type == 'quarterly':
                self.expiry_date = self.member_since + timedelta(days=90)
            elif self.membership_type == 'annual':
                self.expiry_date = self.member_since + timedelta(days=365)
            else:
                # Default to monthly if membership type is not recognized
                self.expiry_date = self.member_since + timedelta(days=30)
        
        super().save(*args, **kwargs)


class PaymentHistory(models.Model):
    """Track payment history for each member"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payment_history')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_type = models.CharField(max_length=20, choices=Member.PAYMENT_TYPES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Payment History"
        verbose_name_plural = "Payment Histories"
    
    def __str__(self):
        return f"{self.member.name} - ₹{self.amount} - {self.payment_date.strftime('%Y-%m-%d')}"


class Lead(models.Model):
    """Lead model for potential gym members - visitor funnel management"""
    
    STATUS_CHOICES = [
        ('new', 'New Lead'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('converted', 'Converted'),
        ('not_interested', 'Not Interested'),
    ]
    
    SOURCE_CHOICES = [
        ('walk_in', 'Walk-in'),
        ('referral', 'Referral'),
        ('online', 'Online'),
        ('advertisement', 'Advertisement'),
        ('social_media', 'Social Media'),
        ('other', 'Other'),
    ]
    
    # Basic contact information
    name = models.CharField(max_length=100, help_text="Full name of the visitor")
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        help_text="Contact number"
    )
    email = models.EmailField(blank=True, null=True, help_text="Email address (optional)")
    
    # Lead information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='walk_in')
    interest_level = models.IntegerField(
        default=5,
        help_text="Interest level from 1-10 (10 being highest)"
    )
    
    # Follow-up and notes
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the lead")
    last_contacted = models.DateTimeField(blank=True, null=True)
    next_follow_up = models.DateField(blank=True, null=True, help_text="Next follow-up date")
    
    # Conversion tracking
    converted_member = models.ForeignKey(
        Member, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        help_text="If converted, link to the member record"
    )
    conversion_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    @property
    def is_converted(self):
        """Check if lead has been converted to member"""
        return self.status == 'converted' and self.converted_member is not None
    
    @property
    def days_since_created(self):
        """Calculate days since lead was created"""
        return (timezone.now() - self.created_at).days
    
    @property
    def is_overdue_follow_up(self):
        """Check if follow-up is overdue"""
        if not self.next_follow_up:
            return False
        return date.today() > self.next_follow_up
    
    def mark_converted(self, member):
        """Mark lead as converted and link to member"""
        self.status = 'converted'
        self.converted_member = member
        self.conversion_date = timezone.now()
        self.save()
