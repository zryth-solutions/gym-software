from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Member management
    path('members/', views.member_list, name='member_list'),
    path('members/enroll/', views.member_enroll, name='member_enroll'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/payment/', views.add_payment, name='add_payment'),
    
    # Lead management
    path('lead-capture/', views.lead_capture, name='lead_capture'),
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/convert/', views.convert_lead, name='convert_lead'),
    path('leads/<int:pk>/update-status/', views.lead_quick_update_status, name='lead_update_status'),
    
    # Reports and actions
    path('reports/', views.reports, name='reports'),
    path('quick-actions/', views.quick_actions, name='quick_actions'),
] 