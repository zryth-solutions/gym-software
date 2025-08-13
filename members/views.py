from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.db import transaction
from datetime import date, timedelta
from django.utils import timezone
from .models import Member, PaymentHistory, Lead
from .forms import MemberForm, MemberFilterForm, LeadCaptureForm, LeadFilterForm, LeadUpdateForm, QuickMemberForm
from .tasks import send_welcome_email


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'members/login.html')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def home(request):
    """Home page with gym information"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'members/home.html')


@login_required
def dashboard(request):
    """Admin dashboard with member statistics"""
    total_members = Member.objects.count()
    active_members = Member.objects.filter(is_active=True).count()
    expired_members = Member.objects.filter(expiry_date__lt=date.today()).count()
    expiring_soon = Member.objects.filter(
        expiry_date__gte=date.today(),
        expiry_date__lte=date.today() + timedelta(days=7)
    ).count()
    
    pending_payments = Member.objects.filter(pending_amount__gt=0).aggregate(
        total=Sum('pending_amount')
    )['total'] or 0
    
    # Recent members with pagination for dashboard table
    recent_members_queryset = Member.objects.order_by('-created_at')
    recent_paginator = Paginator(recent_members_queryset, 8)  # 8 per page for dashboard
    recent_page = request.GET.get('recent_page')
    recent_members = recent_paginator.get_page(recent_page)
    
    # Membership type distribution
    membership_stats = Member.objects.values('membership_type').annotate(
        count=Count('id')
    ).order_by('membership_type')
    
    # Lead statistics
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    converted_leads = Lead.objects.filter(status='converted').count()
    leads_this_week = Lead.objects.filter(
        created_at__gte=date.today() - timedelta(days=7)
    ).count()
    
    # Quick stats for cards
    stats = {
        'total_members': total_members,
        'active_members': active_members,
        'expired_members': expired_members,
        'expiring_soon': expiring_soon,
        'pending_payments': pending_payments,
        'new_this_week': Member.objects.filter(
            created_at__gte=date.today() - timedelta(days=7)
        ).count(),
        'total_revenue': Member.objects.aggregate(
            total=Sum('payment_amount')
        )['total'] or 0,
        'pending_count': Member.objects.filter(pending_amount__gt=0).count(),
        'total_leads': total_leads,
        'new_leads': new_leads,
        'converted_leads': converted_leads,
        'leads_this_week': leads_this_week,
    }
    
    context = {
        **stats,
        'recent_members': recent_members,
        'membership_stats': membership_stats,
    }
    
    return render(request, 'members/dashboard.html', context)


@login_required
def member_list(request):
    """List all members with filtering options"""
    # Set default for is_active only if no query parameters at all (first visit)
    get_data = request.GET.copy()
    if not request.GET:  # Only when no query parameters exist (first page load)
        get_data['is_active'] = 'active'
    
    form = MemberFilterForm(get_data)
    members = Member.objects.all().order_by('-created_at')
    
    # Apply filters
    if form.is_valid():
        if form.cleaned_data['search']:
            search_term = form.cleaned_data['search']
            members = members.filter(
                Q(name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(mobile_phone__icontains=search_term)
            )
        
        if form.cleaned_data['membership_type']:
            members = members.filter(membership_type=form.cleaned_data['membership_type'])
        
        if form.cleaned_data['gender']:
            members = members.filter(gender=form.cleaned_data['gender'])
        
        if form.cleaned_data['is_active'] == 'active':
            # Active members = is_active=True AND not expired
            members = members.filter(
                is_active=True,
                expiry_date__gt=date.today()
            )
        elif form.cleaned_data['is_active'] == 'expired':
            # Expired members = expired regardless of is_active status
            members = members.filter(expiry_date__lt=date.today())
        
        if form.cleaned_data['has_pending_payment']:
            members = members.filter(pending_amount__gt=0)
        
        if form.cleaned_data['expiry_status'] == 'expired':
            members = members.filter(expiry_date__lt=date.today())
        elif form.cleaned_data['expiry_status'] == 'expiring_soon':
            members = members.filter(
                expiry_date__gte=date.today(),
                expiry_date__lte=date.today() + timedelta(days=7)
            )
        elif form.cleaned_data['expiry_status'] == 'active':
            members = members.filter(expiry_date__gt=date.today() + timedelta(days=7))
    
    # Pagination
    paginator = Paginator(members, 12)  # 12 members per page for card view
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'members': page_obj,
        'total_count': members.count(),
    }
    
    return render(request, 'members/member_list.html', context)


@login_required
def member_enroll(request):
    """Enroll a new member"""
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                member = form.save(commit=False)
                member.save()
                
                # Send welcome email only if email is provided and Celery is available
                if member.email:
                    try:
                        send_welcome_email.delay(member.id)
                    except Exception:
                        # If Celery is not running, skip email silently
                        pass
                
                messages.success(
                    request, 
                    f'🎉 Member {member.name} enrolled successfully! Welcome to The Fit Forge Gym.'
                )
                # Redirect back to enrollment form for next member
                return redirect('member_enroll')
    else:
        form = MemberForm()
    
    return render(request, 'members/member_enroll.html', {'form': form})


@login_required
def quick_member_enroll(request):
    """Quick member enrollment with minimal fields"""
    if request.method == 'POST':
        form = QuickMemberForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                member = form.save(commit=False)
                member.save()
                
                # Send welcome email only if email is provided and Celery is available
                if member.email:
                    try:
                        send_welcome_email.delay(member.id)
                    except Exception:
                        pass
                
                messages.success(
                    request, 
                    f'⚡ Member {member.name} enrolled quickly! You can add more details later if needed.'
                )
                # Redirect back to quick enrollment form for next member
                return redirect('quick_member_enroll')
    else:
        form = QuickMemberForm()
    
    return render(request, 'members/quick_member_enroll.html', {'form': form})


@login_required
def member_detail(request, pk):
    """View member details"""
    member = get_object_or_404(Member, pk=pk)
    
    # Payment history with pagination
    payment_history_queryset = member.payment_history.all().order_by('-payment_date')
    payment_paginator = Paginator(payment_history_queryset, 10)  # 10 payments per page
    payment_page = request.GET.get('payment_page')
    payment_history = payment_paginator.get_page(payment_page)
    
    context = {
        'member': member,
        'payment_history': payment_history,
    }
    
    return render(request, 'members/member_detail.html', context)


@login_required
def member_edit(request, pk):
    """Edit member information"""
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, f'✅ Member {member.name} updated successfully!')
                return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm(instance=member)
    
    context = {
        'form': form,
        'member': member,
    }
    
    return render(request, 'members/member_edit.html', context)


@login_required
def add_payment(request, pk):
    """Add payment for a member"""
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        payment_type = request.POST.get('payment_type')
        transaction_id = request.POST.get('transaction_id', '')
        notes = request.POST.get('notes', '')
        
        if amount <= 0:
            messages.error(request, 'Payment amount must be greater than 0.')
            return render(request, 'members/add_payment.html', {'member': member})
        
        if amount > member.pending_amount:
            messages.error(request, f'Payment amount cannot exceed pending amount of ₹{member.pending_amount}.')
            return render(request, 'members/add_payment.html', {'member': member})
        
        # Create payment history record
        PaymentHistory.objects.create(
            member=member,
            amount=amount,
            payment_type=payment_type,
            transaction_id=transaction_id,
            notes=notes
        )
        
        # Update pending amount
        member.pending_amount = max(0, member.pending_amount - amount)
        member.save()
        
        messages.success(request, f'💰 Payment of ₹{amount} recorded successfully!')
        return redirect('member_detail', pk=member.pk)
    
    return render(request, 'members/add_payment.html', {'member': member})


@login_required
def reports(request):
    """Generate reports"""
    # Monthly revenue - simplified approach for Django 4.2.7
    from django.db.models.functions import TruncMonth
    monthly_revenue = PaymentHistory.objects.annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('-month')[:6]  # Last 6 months
    
    # Membership type breakdown
    membership_breakdown = Member.objects.values('membership_type').annotate(
        count=Count('id'),
        revenue=Sum('payment_amount')
    )
    
    # Pending payments with pagination
    pending_payments_queryset = Member.objects.filter(pending_amount__gt=0).order_by('-pending_amount')
    pending_paginator = Paginator(pending_payments_queryset, 10)
    pending_page = request.GET.get('pending_page')
    pending_payments = pending_paginator.get_page(pending_page)
    
    # Expiring memberships with pagination
    expiring_queryset = Member.objects.filter(
        expiry_date__gte=date.today(),
        expiry_date__lte=date.today() + timedelta(days=30)
    ).order_by('expiry_date')
    expiring_paginator = Paginator(expiring_queryset, 10)
    expiring_page = request.GET.get('expiring_page')
    expiring_memberships = expiring_paginator.get_page(expiring_page)
    
    # Summary stats
    total_pending = Member.objects.filter(pending_amount__gt=0).aggregate(
        total=Sum('pending_amount')
    )['total'] or 0
    
    # Calculate total revenue (same as dashboard)
    total_revenue = Member.objects.aggregate(
        total=Sum('payment_amount')
    )['total'] or 0
    
    context = {
        'monthly_revenue': monthly_revenue,
        'membership_breakdown': membership_breakdown,
        'pending_payments': pending_payments,
        'expiring_memberships': expiring_memberships,
        'total_pending': total_pending,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'members/reports.html', context)


@login_required
def quick_actions(request):
    """Quick actions page for common tasks"""
    # Get members needing attention (same logic as dashboard)
    expired_members = Member.objects.filter(
        expiry_date__lt=date.today()
    ).count()
    
    expiring_soon = Member.objects.filter(
        expiry_date__gte=date.today(),
        expiry_date__lte=date.today() + timedelta(days=7)
    ).count()
    
    pending_payments = Member.objects.filter(pending_amount__gt=0).count()
    
    context = {
        'expired_members': expired_members,
        'expiring_soon': expiring_soon,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'members/quick_actions.html', context)


# ======= LEAD MANAGEMENT VIEWS =======

def lead_capture(request):
    """Quick lead capture form for visitors (no login required)"""
    if request.method == 'POST':
        form = LeadCaptureForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(
                request, 
                f'Thank you {lead.name}! We have captured your information and will contact you soon.'
            )
            # Reset form for next visitor
            form = LeadCaptureForm()
    else:
        form = LeadCaptureForm()
    
    return render(request, 'members/lead_capture.html', {'form': form})


@login_required
def lead_list(request):
    """List all leads with filtering options"""
    form = LeadFilterForm(request.GET)
    leads = Lead.objects.all().order_by('-created_at')
    
    # Apply filters
    if form.is_valid():
        if form.cleaned_data['search']:
            search_term = form.cleaned_data['search']
            leads = leads.filter(
                Q(name__icontains=search_term) |
                Q(phone__icontains=search_term) |
                Q(email__icontains=search_term)
            )
        
        if form.cleaned_data['status']:
            leads = leads.filter(status=form.cleaned_data['status'])
        
        if form.cleaned_data['source']:
            leads = leads.filter(source=form.cleaned_data['source'])
        
        if form.cleaned_data['interest_level']:
            level = form.cleaned_data['interest_level']
            if level == 'high':
                leads = leads.filter(interest_level__gte=8)
            elif level == 'medium':
                leads = leads.filter(interest_level__gte=5, interest_level__lt=8)
            elif level == 'low':
                leads = leads.filter(interest_level__lt=5)
        
        if form.cleaned_data['overdue_follow_up']:
            leads = leads.filter(
                next_follow_up__lt=date.today(),
                status__in=['new', 'contacted', 'interested']
            )
    
    # Pagination
    paginator = Paginator(leads, 12)  # 12 leads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lead statistics
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    converted_leads = Lead.objects.filter(status='converted').count()
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    context = {
        'form': form,
        'leads': page_obj,
        'total_count': leads.count(),
        'total_leads': total_leads,
        'new_leads': new_leads,
        'converted_leads': converted_leads,
        'conversion_rate': round(conversion_rate, 1),
    }
    
    return render(request, 'members/lead_list.html', context)


@login_required
def lead_detail(request, pk):
    """View and update lead details"""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        form = LeadUpdateForm(request.POST, instance=lead)
        if form.is_valid():
            updated_lead = form.save()
            # Update last_contacted if status changed to contacted
            if updated_lead.status == 'contacted' and not updated_lead.last_contacted:
                updated_lead.last_contacted = timezone.now()
                updated_lead.save()
            
            messages.success(request, f'Lead {lead.name} updated successfully!')
            return redirect('lead_detail', pk=lead.pk)
    else:
        form = LeadUpdateForm(instance=lead)
    
    context = {
        'lead': lead,
        'form': form,
    }
    
    return render(request, 'members/lead_detail.html', context)


@login_required
def convert_lead(request, pk):
    """Convert a lead to a member"""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        # Pre-fill member form with lead data
        initial_data = {
            'name': lead.name,
            'mobile_phone': lead.phone,
            'email': lead.email or '',
            'member_since': date.today(),
        }
        
        member_form = MemberForm(request.POST, request.FILES, initial=initial_data)
        if member_form.is_valid():
            with transaction.atomic():
                member = member_form.save(commit=False)
                member.save()
                
                # Mark lead as converted
                lead.mark_converted(member)
                
                # Send welcome email only if email is provided
                if member.email:
                    try:
                        send_welcome_email.delay(member.id)
                    except Exception:
                        pass
                
                messages.success(
                    request, 
                    f'🎉 Lead {lead.name} converted to member successfully! Welcome to The Fit Forge Gym.'
                )
                return redirect('member_detail', pk=member.pk)
    else:
        # Pre-fill the form with lead data
        initial_data = {
            'name': lead.name,
            'mobile_phone': lead.phone,
            'email': lead.email or '',
            'member_since': date.today(),
        }
        member_form = MemberForm(initial=initial_data)
    
    context = {
        'lead': lead,
        'form': member_form,
    }
    
    return render(request, 'members/convert_lead.html', context)


@login_required
def lead_quick_update_status(request, pk):
    """Quick AJAX endpoint to update lead status"""
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in [choice[0] for choice in Lead.STATUS_CHOICES]:
            lead.status = new_status
            if new_status == 'contacted':
                lead.last_contacted = timezone.now()
            lead.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Lead status updated to {lead.get_status_display()}',
                'new_status': lead.get_status_display()
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
