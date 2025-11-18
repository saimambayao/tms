from django.urls import path
from . import views
from .member_views import (
    FahanieCaresMemberRegistrationView, 
    RegistrationSuccessView,
    MemberProfileView,
    MemberUpdateView,
    MemberListView,
    MemberDetailView,
    MemberCreateView,
    GetMunicipalitiesView
)
from .simple_views import SimpleMemberRegistrationView

urlpatterns = [
    # Member Registration URLs
    path('member/register/', FahanieCaresMemberRegistrationView.as_view(), name='member_register'),
    path('member/register/quick/', SimpleMemberRegistrationView.as_view(), name='quick_register'),
    path('member/register/success/', RegistrationSuccessView.as_view(), name='registration_success'),
    path('member/profile/', MemberProfileView.as_view(), name='member_profile'),
    path('member/profile/update/', MemberUpdateView.as_view(), name='member_update'),
    path('staff/members/', MemberListView.as_view(), name='staff_member_list'),
    path('staff/members/create/', MemberCreateView.as_view(), name='member_create'),
    path('staff/members/<int:pk>/', MemberDetailView.as_view(), name='member_detail'),
    
    # Database of Registrants URLs (Authorized Users Only)
    path('database/registrants/', views.DatabaseRegistrantsView.as_view(), name='database_registrants'),
    path('database/registrants/<int:pk>/', views.DatabaseRegistrantDetailView.as_view(), name='database_registrant_detail'),
    path('database/registrants/<int:pk>/edit/', views.DatabaseRegistrantUpdateView.as_view(), name='database_registrant_edit'),
    path('database/registrants/<int:pk>/approve/', views.RegistrantApproveView.as_view(), name='database_registrant_approve'),
    path('database/registrants/<int:pk>/mark-incomplete/', views.RegistrantMarkIncompleteView.as_view(), name='database_registrant_mark_incomplete'),
    path('database/registrants/<int:pk>/mark-non-compliant/', views.RegistrantMarkNonCompliantView.as_view(), name='database_registrant_mark_non_compliant'),
    path('database/registrants/<int:pk>/delete/', views.DatabaseRegistrantDeleteView.as_view(), name='database_registrant_delete'),
    path('database/registrants/export/csv/', views.ExportRegistrantsCSVView.as_view(), name='database_registrants_export_csv'),
    path('database/registrants/user/<int:user_pk>/password-reset/', views.AdminPasswordResetView.as_view(), name='admin_password_reset'),
    path('database/registrants/groups/add/', views.AddRegistrantGroupView.as_view(), name='add_registrant_group'),
    path('database/registrants/report/member-count/', views.MemberCountReportView.as_view(), name='member_count_report'),
    path('database/registrants/excel-name-check/', views.ExcelNameCheckView.as_view(), name='excel_name_check'),
    
    # Public Membership Check URL
    path('check-membership/', views.CheckMembershipView.as_view(), name='check_membership'),

    # Staff Constituent URLs
    path('staff/constituents/', views.StaffConstituentDashboardView.as_view(), name='staff_constituent_dashboard'),
    path('staff/constituents/<int:pk>/', views.StaffConstituentDetailView.as_view(), name='staff_constituent_detail'),
    path('staff/constituents/create/', views.StaffConstituentCreateView.as_view(), name='staff_constituent_create'),
    path('staff/constituents/<int:pk>/update/', views.StaffConstituentUpdateView.as_view(), name='staff_constituent_update'),
    
    # Constituent Interaction URLs
    path('staff/constituents/<int:constituent_id>/interactions/create/', views.StaffConstituentInteractionCreateView.as_view(), name='staff_constituent_interaction_create'),
    
    # Constituent Group URLs
    path('staff/constituent-groups/', views.StaffConstituentGroupListView.as_view(), name='staff_constituent_group_list'),
    path('staff/constituent-groups/<slug:slug>/', views.StaffConstituentGroupDetailView.as_view(), name='staff_constituent_group_detail'),
    path('staff/constituent-groups/create/', views.StaffConstituentGroupCreateView.as_view(), name='staff_constituent_group_create'),
    path('staff/constituent-groups/<slug:slug>/update/', views.StaffConstituentGroupUpdateView.as_view(), name='staff_constituent_group_update'),
    
    # Analytics
    path('staff/constituents/analytics/', views.StaffConstituentAnalyticsView.as_view(), name='staff_constituent_analytics'),
    
    # AJAX endpoints
    path('api/municipalities/', GetMunicipalitiesView.as_view(), name='get_municipalities'),
]
