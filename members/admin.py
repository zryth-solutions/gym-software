from django.contrib import admin
from django.utils.html import format_html
from .models import Member, PaymentHistory, Lead
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


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'phone', 'email', 'status', 'source', 
        'interest_level', 'days_since_created', 'lead_status_display',
        'follow_up_status', 'created_at'
    ]
    
    list_filter = [
        'status', 'source', 'interest_level', 'created_at',
        'next_follow_up', 'conversion_date'
    ]
    
    search_fields = ['name', 'phone', 'email']
    
    readonly_fields = [
        'created_at', 'updated_at', 'conversion_date', 
        'days_since_created', 'is_overdue_follow_up'
    ]
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Lead Details', {
            'fields': ('status', 'source', 'interest_level', 'notes')
        }),
        ('Follow-up Information', {
            'fields': ('last_contacted', 'next_follow_up')
        }),
        ('Conversion Tracking', {
            'fields': ('converted_member', 'conversion_date'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('days_since_created', 'is_overdue_follow_up'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    def lead_status_display(self, obj):
        status_colors = {
            'new': 'blue',
            'contacted': 'orange',
            'interested': 'purple',
            'converted': 'green',
            'not_interested': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    lead_status_display.short_description = 'Status'
    
    def follow_up_status(self, obj):
        if not obj.next_follow_up:
            return format_html('<span style="color: gray;">No follow-up set</span>')
        elif obj.is_overdue_follow_up:
            return format_html(
                '<span style="color: red; font-weight: bold;">OVERDUE ({})</span>',
                obj.next_follow_up.strftime('%m/%d/%Y')
            )
        else:
            return format_html(
                '<span style="color: green;">Due: {}</span>',
                obj.next_follow_up.strftime('%m/%d/%Y')
            )
    follow_up_status.short_description = 'Follow-up'
    
    def days_since_created(self, obj):
        return f"{obj.days_since_created} days"
    days_since_created.short_description = 'Age'
    
    actions = ['mark_as_contacted', 'mark_as_interested', 'mark_as_not_interested']
    
    def mark_as_contacted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='new').update(
            status='contacted',
            last_contacted=timezone.now()
        )
        self.message_user(request, f'{updated} leads marked as contacted.')
    mark_as_contacted.short_description = "Mark selected leads as contacted"
    
    def mark_as_interested(self, request, queryset):
        updated = queryset.update(status='interested')
        self.message_user(request, f'{updated} leads marked as interested.')
    mark_as_interested.short_description = "Mark selected leads as interested"
    
    def mark_as_not_interested(self, request, queryset):
        updated = queryset.update(status='not_interested')
        self.message_user(request, f'{updated} leads marked as not interested.')
    mark_as_not_interested.short_description = "Mark selected leads as not interested"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('converted_member')
