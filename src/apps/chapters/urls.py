from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('', views.ChapterListView.as_view(), name='chapter_list'),
    
    # Staff only - MUST come before slug patterns
    path('create/', views.ChapterCreateView.as_view(), name='chapter_create'),
    
    # Activities - specific patterns before slug patterns
    path('activity/<int:pk>/', views.ChapterActivityDetailView.as_view(), name='activity_detail'),
    path('activity/<int:pk>/register/', views.ActivityRegistrationView.as_view(), name='activity_register'),
    
    # Slug-based patterns - MUST come after specific patterns
    path('<slug:slug>/', views.ChapterDetailView.as_view(), name='chapter_detail'),
    path('<slug:slug>/join/', views.MembershipApplicationView.as_view(), name='chapter_join'),
    path('<slug:slug>/members/', views.ChapterMembershipView.as_view(), name='chapter_members'),
    path('<slug:slug>/activities/', views.ChapterActivityListView.as_view(), name='chapter_activities'),
    path('<slug:slug>/dashboard/', views.ChapterDashboardView.as_view(), name='chapter_dashboard'),
    path('<slug:slug>/edit/', views.ChapterUpdateView.as_view(), name='chapter_edit'),
    
    # Activity management - TODO: Implement ActivityCreateView if needed
    # path('<slug:slug>/activities/create/', views.ActivityCreateView.as_view(), name='activity_create'),
]