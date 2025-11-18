from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # Public views
    # Public views
    path('programs/', views.ServiceProgramListView.as_view(), name='service_program_list'), # Changed URL path
    path('program/<slug:slug>/', views.ServiceProgramDetailView.as_view(), name='service_program_detail'),
    path('fahaniecares-program/<slug:slug>/', views.MinistryProgramDetailView.as_view(), name='fahaniecares_program_detail'),
    
    # Application views
    path('apply/', views.ApplicationFormView.as_view(), name='application_form'),
    path('apply/success/', views.TemplateView.as_view(template_name='services/application_success.html'), name='application_success'),
    path('program/<slug:slug>/apply/', views.ServiceApplicationCreateView.as_view(), name='service_apply'),
    path('applications/', views.StaffApplicationListView.as_view(), name='service_applications'), # Changed to StaffApplicationListView
    path('application/<int:pk>/', views.ServiceApplicationDetailView.as_view(), name='service_application_detail'),
    
    # Staff views (keeping the old staff applications path for now, though it's now redundant)
    path('staff/dashboard/', views.ServiceProgramDashboardView.as_view(), name='service_dashboard'),
    path('staff/applications/all/', views.StaffApplicationListView.as_view(), name='staff_all_applications'), # Renamed for clarity
    path('staff/application/<int:pk>/', views.ServiceApplicationDetailView.as_view(), name='staff_application_detail'),
    path('staff/application/<int:pk>/assess/', views.ServiceApplicationAssessmentView.as_view(), name='service_application_assessment'),
    path('staff/application/<int:application_id>/disbursement/', views.ServiceDisbursementCreateView.as_view(), name='service_disbursement_create'),
    
    # Ministry Programs Admin Interface
    path('admin/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/programs/', admin_views.ProgramListView.as_view(), name='program_list'),
    path('admin/programs/create/', admin_views.ProgramCreateView.as_view(), name='program_create'),
    path('admin/programs/<int:pk>/', admin_views.program_detail_view, name='program_detail'),
    path('admin/programs/<int:pk>/edit/', admin_views.ProgramUpdateView.as_view(), name='program_update'),
    path('admin/programs/<int:pk>/delete/', admin_views.program_delete_view, name='program_delete'),
    path('admin/programs/bulk-action/', admin_views.bulk_actions_view, name='program_bulk_action'),
    path('admin/programs/export/', admin_views.export_programs_view, name='program_export'),
    path('admin/programs/import/', admin_views.import_programs_view, name='program_import'),
    path('admin/programs/history/', admin_views.program_history_view, name='program_history'),
]
