from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Member


class MemberForm(forms.ModelForm):
    """Form for enrolling and editing members"""
    
    class Meta:
        model = Member
        fields = [
            'name', 'email', 'mobile_phone', 'date_of_birth', 'gender', 
            'address', 'member_since', 'membership_type', 'payment_amount', 'pending_amount',
            'payment_type', 'profile_picture'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Complete Address'}),
            'member_since': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'membership_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Payment Amount', 'step': '0.01'}),
            'pending_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pending Amount', 'step': '0.01'}),
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        today = date.today()
        
        if dob >= today:
            raise ValidationError("Date of birth cannot be in the future.")
        
        # Check if age is reasonable (between 10 and 100 years)
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 10:
            raise ValidationError("Member must be at least 10 years old.")
        if age > 100:
            raise ValidationError("Please check the date of birth.")
        
        return dob
    
    def clean_payment_amount(self):
        amount = self.cleaned_data['payment_amount']
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than 0.")
        return amount
    
    def clean_pending_amount(self):
        pending = self.cleaned_data['pending_amount']
        if pending < 0:
            raise ValidationError("Pending amount cannot be negative.")
        return pending
    
    def clean_member_since(self):
        member_since = self.cleaned_data['member_since']
        today = date.today()
        
        if member_since > today:
            raise ValidationError("Join date cannot be in the future.")
        
        return member_since


class MemberFilterForm(forms.Form):
    """Form for filtering members list"""
    
    EXPIRY_STATUS_CHOICES = [
        ('', 'All'),
        ('active', 'Active'),
        ('expiring_soon', 'Expiring Soon (7 days)'),
        ('expired', 'Expired'),
    ]
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or phone...'
        })
    )
    
    membership_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Member.MEMBERSHIP_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'All Genders')] + Member.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('active', 'Active'),
            ('expired', 'Expired'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    has_pending_payment = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    expiry_status = forms.ChoiceField(
        choices=EXPIRY_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class PaymentForm(forms.Form):
    """Form for adding payments"""
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Payment Amount',
            'step': '0.01'
        })
    )
    
    payment_type = forms.ChoiceField(
        choices=Member.PAYMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Transaction ID (optional)'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes (optional)'
        })
    )
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than 0.")
        return amount 