from django.contrib import admin
from django.utils.html import format_html
from .models import Member, PaymentHistory
from datetime import date


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'mobile_phone', 'membership_type', 
        'expiry_date', 'membership_status', 'payment_status', 
        'age', 'created_at'
    ]
    
    list_filter = [
        'membership_type', 'gender', 'is_active', 'payment_type',
        'created_at', 'expiry_date'
    ]
    
    search_fields = ['name', 'email', 'mobile_phone']
    
    readonly_fields = ['age', 'created_at', 'updated_at', 'is_membership_expired', 'days_until_expiry', 'expiry_date']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'mobile_phone', 'date_of_birth', 'gender', 'address', 'profile_picture')
        }),
        ('Membership Details', {
            'fields': ('member_since', 'membership_type', 'is_active')
        }),
        ('Payment Information', {
            'fields': ('payment_amount', 'pending_amount', 'payment_type')
        }),
        ('Calculated Fields', {
            'fields': ('age', 'expiry_date', 'is_membership_expired', 'days_until_expiry'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    def membership_status(self, obj):
        if obj.is_membership_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">EXPIRED</span>'
            )
        elif obj.days_until_expiry <= 7:
            return format_html(
                '<span style="color: orange; font-weight: bold;">EXPIRING SOON</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">ACTIVE</span>'
            )
    membership_status.short_description = 'Status'
    
    def payment_status(self, obj):
        if obj.has_pending_payment:
            return format_html(
                '<span style="color: red;">₹{} PENDING</span>',
                obj.pending_amount
            )
        else:
            return format_html(
                '<span style="color: green;">PAID</span>'
            )
    payment_status.short_description = 'Payment'
    
    def age(self, obj):
        return f"{obj.age} years"
    age.short_description = 'Age'
    
    actions = ['mark_as_inactive', 'send_reminder_emails']
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} members marked as inactive.')
    mark_as_inactive.short_description = "Mark selected members as inactive"
    
    def send_reminder_emails(self, request, queryset):
        # This will be implemented with the email service
        count = queryset.filter(pending_amount__gt=0).count()
        self.message_user(request, f'Reminder emails will be sent to {count} members with pending payments.')
    send_reminder_emails.short_description = "Send payment reminder emails"


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'payment_date', 'payment_type', 'transaction_id']
    list_filter = ['payment_type', 'payment_date']
    search_fields = ['member__name', 'member__email', 'transaction_id']
    date_hierarchy = 'payment_date'
    
    readonly_fields = ['payment_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('member')
