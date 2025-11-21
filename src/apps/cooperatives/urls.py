from django.urls import path
from . import views

app_name = 'cooperatives'

urlpatterns = [
    path('', views.CooperativeListView.as_view(), name='cooperative-list'),
    path('<int:pk>/', views.CooperativeDetailView.as_view(), name='cooperative-detail'),
    path('register/', views.CooperativeRegistrationView.as_view(), name='cooperative-register'),
    path('<int:pk>/update/', views.CooperativeUpdateView.as_view(), name='cooperative-update'),
    path('<int:pk>/delete/', views.CooperativeDeleteView.as_view(), name='cooperative-delete'),
    path('<int:pk>/officers/', views.CooperativeOfficerManagementView.as_view(), name='cooperative-officer-management'),
    path('<int:pk>/officers/register/', views.EnhancedOfficerRegistrationView.as_view(), name='enhanced-officer-register'),
    path('bulk-register-officers/', views.BulkOfficerRegistrationView.as_view(), name='bulk-officer-register'),
    path('dashboard/', views.CooperativeDashboardView.as_view(), name='cooperative-dashboard'),
    path('<int:cooperative_pk>/officers/<int:officer_pk>/delete/', views.CooperativeOfficerDeleteView.as_view(), name='cooperative-officer-delete'),
]
