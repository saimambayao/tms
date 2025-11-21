from django.urls import path
from . import views

app_name = 'unified_db'

urlpatterns = [
    # Main search interface
    path('search/', views.UnifiedPersonSearchView.as_view(), name='person_search'),

    # Unified person detail view
    path('person/<str:person_type>/<int:person_id>/', views.UnifiedPersonDetailView.as_view(), name='person_detail'),

    # Database management
    path('databases/', views.DatabaseListView.as_view(), name='database_list'),
    path('databases/create/', views.DatabaseCreateView.as_view(), name='database_create'),
    path('databases/<slug:slug>/', views.DatabaseDetailView.as_view(), name='database_detail'),
    path('databases/<slug:slug>/delete/', views.DatabaseDeleteView.as_view(), name='database_delete'),
    path('databases/<str:database_slug>/', views.DatabaseDetailView.as_view(), name='database_detail_str'),

    # Database entries
    path('databases/<slug:database_slug>/entries/create/', views.DatabaseEntryCreateView.as_view(), name='database_entry_create'),
    path('databases/<slug:database_slug>/entries/<int:pk>/', views.DatabaseEntryDetailView.as_view(), name='database_entry_detail'),
    path('databases/<slug:database_slug>/entries/<int:pk>/detail/', views.DatabaseEntryDetailView.as_view(), name='database_entry_detail_alt'),

    # Alternative URL patterns for flexibility
    path('databases/<str:database_slug>/entries/<int:pk>/', views.DatabaseEntryDetailView.as_view(), name='database_entry_detail_str'),

    # Excel/CSV Import
    path('databases/<slug:database_slug>/import/', views.DatabaseImportView.as_view(), name='database_import'),
    path('databases/<slug:database_slug>/import/process/', views.DatabaseImportProcessView.as_view(), name='database_import_process'),
]
