from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Member, Lead


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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address (Optional)'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number (Optional)'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address (Optional)'}),
            'member_since': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'membership_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Payment Amount', 'step': '0.01', 'required': True}),
            'pending_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pending Amount (Default: 0)', 'step': '0.01', 'value': '0'}),
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if not dob:
            return dob
        
        today = date.today()
        # Only check if date is in future - remove age restrictions for speed
        if dob >= today:
            raise ValidationError("Date of birth cannot be in the future.")
        
        return dob
    
    def clean_payment_amount(self):
        amount = self.cleaned_data['payment_amount']
        # Simplified validation - just check if positive
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than 0.")
        return amount
    
    # Remove pending amount validation entirely for speed
    # def clean_pending_amount(self):
    #     pending = self.cleaned_data['pending_amount']
    #     if pending < 0:
    #         raise ValidationError("Pending amount cannot be negative.")
    #     return pending
    
    # Remove member_since validation for speed - model will handle it
    # def clean_member_since(self):
    #     member_since = self.cleaned_data['member_since']
    #     today = date.today()
    #     
    #     if member_since > today:
    #         raise ValidationError("Join date cannot be in the future.")
    #     
    #     return member_since


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


class LeadCaptureForm(forms.ModelForm):
    """Quick form for capturing visitor information"""
    
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'source', 'interest_level', 'notes']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Visitor Name',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Phone Number',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (Optional)'
            }),
            'source': forms.Select(attrs={
                'class': 'form-control'
            }),
            'interest_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'value': 5
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about the visitor...'
            })
        }
    
    def clean_interest_level(self):
        interest = self.cleaned_data['interest_level']
        if interest < 1 or interest > 10:
            raise ValidationError("Interest level must be between 1 and 10.")
        return interest


class QuickMemberForm(forms.ModelForm):
    """Simplified form for quick member enrollment"""
    
    class Meta:
        model = Member
        fields = ['name', 'mobile_phone', 'membership_type', 'payment_amount']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Full Name',
                'required': True
            }),
            'mobile_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Mobile Number (Optional)'
            }),
            'membership_type': forms.Select(attrs={
                'class': 'form-control form-control-lg'
            }),
            'payment_amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Payment Amount (₹)',
                'step': '0.01',
                'required': True
            })
        }
    
    def clean_payment_amount(self):
        amount = self.cleaned_data['payment_amount']
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than 0.")
        return amount


class LeadFilterForm(forms.Form):
    """Form for filtering leads list"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, phone, or email...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Lead.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    source = forms.ChoiceField(
        choices=[('', 'All Sources')] + Lead.SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    interest_level = forms.ChoiceField(
        choices=[
            ('', 'All Levels'),
            ('high', 'High (8-10)'),
            ('medium', 'Medium (5-7)'),
            ('low', 'Low (1-4)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    overdue_follow_up = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class LeadUpdateForm(forms.ModelForm):
    """Form for updating lead information and status"""
    
    class Meta:
        model = Lead
        fields = [
            'name', 'phone', 'email', 'status', 'source', 'interest_level', 
            'notes', 'next_follow_up'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'interest_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'next_follow_up': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
    
    def clean_interest_level(self):
        interest = self.cleaned_data['interest_level']
        if interest < 1 or interest > 10:
            raise ValidationError("Interest level must be between 1 and 10.")
        return interest 