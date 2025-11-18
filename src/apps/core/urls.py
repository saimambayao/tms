from django.urls import path, reverse_lazy
from django.views.generic import RedirectView # Import RedirectView
from . import views
from apps.communications.views import EmailSubscriptionView, EmailSubscriptionSuccessView
from apps.services.views import MinistryProgramDetailView # Import MinistryProgramDetailView from services app

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('about-chapters/', views.PublicChaptersView.as_view(), name='chapters_public'),
    path('contact/', views.ContactPageView.as_view(), name='contact'),
    path('ministries-ppas/', views.MinistriesPPAsView.as_view(), name='ministries_ppas'),
    path('programs/', views.ProgramsView.as_view(), name='programs'),
    path('tdif-projects/', views.TDIFProjectsView.as_view(), name='tdif_projects'),
    path('completed-programs/', views.CompletedProgramsView.as_view(), name='completed_programs'),
    path('accessible-ministry-programs/', views.AccessibleMinistryProgramsView.as_view(), name='accessible_ministry_programs'),
    path('partner/', views.PartnerPageView.as_view(), name='partner'),
    path('donate/', views.DonatePageView.as_view(), name='donate'),
    
    # Database Views - Restricted Access
    path('database/chapters/', views.ChaptersPageView.as_view(), name='database_chapters'),
    path('chapters-overview/', views.ChaptersPageView.as_view(), name='chapters_overview'),
    path('database/staff/', views.DatabaseStaffView.as_view(), name='database_staff'),
    path('database/staff/create/', views.DatabaseStaffCreateView.as_view(), name='database_staff_create'),
    path('database/staff/<int:pk>/edit/', views.DatabaseStaffEditView.as_view(), name='database_staff_edit'),
    path('database/staff/<int:pk>/delete/', views.DatabaseStaffDeleteView.as_view(), name='database_staff_delete'),
    path('database/partners/', views.DatabasePartnersView.as_view(), name='database_partners'),
    path('database/donors/', views.DatabaseDonorsView.as_view(), name='database_donors'),
    path('database/members/bulk-register/', views.MemberBulkRegistrationView.as_view(), name='bulk_member_registration'),
    path('database/members/', views.DatabaseMembersView.as_view(), name='database_members_list'),
    path('database/ppas/', views.DatabasePPAsView.as_view(), name='database_ppas'),
    path('database/updates/', views.DatabaseUpdatesView.as_view(), name='database_updates'),
    path('database/updates/create/', views.DatabaseAnnouncementCreateView.as_view(), name='database_announcement_create'),
    path('database/updates/<slug:slug>/edit/', views.DatabaseAnnouncementUpdateView.as_view(), name='database_announcement_edit'),
    path('database/updates/<int:pk>/delete/', views.DatabaseAnnouncementDeleteView.as_view(), name='database_announcement_delete'),
    path('database/contact-messages/', views.DatabaseContactMessagesView.as_view(), name='database_contact_messages'),
    path('database/contact-messages/<int:pk>/', views.DatabaseContactMessageDetailView.as_view(), name='database_contact_message_detail'),
    path('database/contact-messages/<int:pk>/mark-read/', views.MarkMessageReadView.as_view(), name='mark_message_read'),
    path('database/contact-messages/<int:pk>/mark-replied/', views.MarkMessageRepliedView.as_view(), name='mark_message_replied'),
    path('database/contact-messages/<int:pk>/delete/', views.DatabaseContactMessageDeleteView.as_view(), name='database_contact_message_delete'),
    path('database/contact-messages/export/', views.DatabaseContactMessagesExportView.as_view(), name='database_contact_messages_export'),
    path('database/contact-messages/<int:pk>/reply/', views.ReplyToContactMessageView.as_view(), name='reply_contact_message'),
    
    # Chapter Assignment
    path('assign-chapter/', views.AssignChapterView.as_view(), name='assign_chapter'),
    
    # Chapter Request Management (CRUD)
    path('chapter-request-detail/<int:request_id>/', views.ChapterRequestDetailView.as_view(), name='chapter_request_detail'),
    path('chapter-request-update-status/<int:request_id>/', views.ChapterRequestUpdateStatusView.as_view(), name='chapter_request_update_status'),
    path('chapter-request-assign/<int:request_id>/', views.ChapterRequestAssignView.as_view(), name='chapter_request_assign'),
    path('chapter-request-delete/<int:request_id>/', views.ChapterRequestDeleteView.as_view(), name='chapter_request_delete'),
    path('chapter-request-notes/<int:request_id>/', views.ChapterRequestNotesView.as_view(), name='chapter_request_notes'),
    
    # Announcements
    path('updates/', views.AnnouncementListView.as_view(), name='announcements'),
    path('updates/<slug:slug>/', views.AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('faqs/', views.faqs_view, name='faqs'),
    
    # Email Subscription
    path('subscribe/', EmailSubscriptionView.as_view(), name='email_subscribe'),
    path('subscribe/success/', EmailSubscriptionSuccessView.as_view(), name='email_subscribe_success'),
    
    # Mobile views
    path('mobile/', views.MobileServiceView.as_view(), name='mobile_services'),
    path('mobile/offline/', views.OfflineFormView.as_view(), name='mobile_offline'),
    
    # API endpoints
    path('api/mobile/sync/', views.mobile_sync_api, name='mobile_sync_api'),
    
    # PWA files
    path('service-worker.js', views.service_worker, name='service_worker'),
    path('manifest.json', views.manifest, name='manifest'),
    path('offline/', views.offline_page, name='offline'),
    path('test-url/', views.TestUrlView.as_view(), name='test_url'), # For debugging TemplateSyntaxError
    
    # Health Check and Monitoring Endpoints
    path('health/', views.health_check, name='health_check'),
    path('health/detailed/', views.health_detailed, name='health_detailed'),
    path('ready/', views.readiness_check, name='readiness_check'),
    path('metrics/', views.metrics_endpoint, name='metrics'),
    
    # Test pages
    path('test-icons/', views.test_icons, name='test_icons'),
    path('test-radio/', views.test_radio, name='test_radio'),
    
    # Detail view for TDIF Projects
    path('tdif-projects/<slug:slug>/', views.TDIFProjectDetailView.as_view(), name='tdif_project_detail'),
    
    # Detail view for Ministry Programs (using MinistryProgramDetailView from services app)
    path('ministry-programs/<slug:slug>/', MinistryProgramDetailView.as_view(), name='ministry_program_detail'),

    # Debug endpoints (temporary)
    path('debug/csrf/', views.csrf_debug, name='csrf_debug'),
    
    # Monitoring Dashboard (Staff/Admin only)
    path('monitoring/', views.monitoring_dashboard, name='monitoring_dashboard'),
]
