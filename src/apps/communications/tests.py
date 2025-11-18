"""
Comprehensive test suite for Communications application.
Tests models, views, forms, and complex workflows for communications management.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.validators import ValidationError
from django.db import IntegrityError
from datetime import datetime, timedelta, time
from decimal import Decimal
import json

from .models import (
    ContactFormSubmission, PartnershipSubmission, DonationSubmission,
    CommunicationTemplate, CommunicationCampaign, CommunicationMessage,
    AnnouncementPost, EventNotification, CommunicationSettings, EmailSubscription
)
from apps.constituents.models import Constituent, ConstituentGroup
from apps.chapters.models import Chapter

User = get_user_model()


# ==============================
# UNIT TESTS - MODELS
# ==============================

class ContactFormSubmissionModelTests(TestCase):
    """Unit tests for ContactFormSubmission model."""
    
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='TestPass123!',
            user_type='staff'
        )
    
    def test_contact_form_submission_creation(self):
        """Test creating a contact form submission."""
        submission = ContactFormSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@email.com',
            phone_number='09123456789',
            subject='assistance',
            message='Need help with medical assistance',
            form_source='contact_page',
            status='new'
        )
        
        self.assertEqual(submission.first_name, 'John')
        self.assertEqual(submission.last_name, 'Doe')
        self.assertEqual(submission.subject, 'assistance')
        self.assertEqual(submission.status, 'new')
        self.assertTrue(submission.is_recent)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        # With middle name
        submission = ContactFormSubmission.objects.create(
            first_name='John',
            middle_name='Michael',
            last_name='Doe',
            email='john@email.com',
            subject='feedback',
            message='Test message',
            form_source='test'
        )
        self.assertEqual(submission.get_full_name(), 'John Michael Doe')
        
        # Without middle name
        submission_no_middle = ContactFormSubmission.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@email.com',
            subject='feedback',
            message='Test message',
            form_source='test'
        )
        self.assertEqual(submission_no_middle.get_full_name(), 'Jane Smith')
    
    def test_is_recent_property(self):
        """Test is_recent property for submissions."""
        # Recent submission (created now)
        recent_submission = ContactFormSubmission.objects.create(
            first_name='Recent',
            last_name='User',
            email='recent@email.com',
            subject='assistance',
            message='Recent message',
            form_source='test'
        )
        self.assertTrue(recent_submission.is_recent)
        
        # Old submission (create and modify submitted_at)
        old_submission = ContactFormSubmission.objects.create(
            first_name='Old',
            last_name='User',
            email='old@email.com',
            subject='assistance',
            message='Old message',
            form_source='test'
        )
        # Manually set to 3 days ago
        old_submission.submitted_at = timezone.now() - timedelta(days=3)
        old_submission.save()
        self.assertFalse(old_submission.is_recent)
    
    def test_string_representation(self):
        """Test string representation of contact form submission."""
        submission = ContactFormSubmission.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@email.com',
            subject='assistance',
            message='Test message',
            form_source='test'
        )
        
        expected_str = f"John Doe - Request Assistance ({submission.submitted_at.strftime('%Y-%m-%d')})"
        self.assertEqual(str(submission), expected_str)


class PartnershipSubmissionModelTests(TestCase):
    """Unit tests for PartnershipSubmission model."""
    
    def setUp(self):
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='TestPass123!',
            user_type='admin'
        )
    
    def test_partnership_submission_creation(self):
        """Test creating a partnership submission."""
        submission = PartnershipSubmission.objects.create(
            organization_name='Test NGO',
            contact_person='Jane Smith',
            email='jane@testngo.org',
            phone_number='09987654321',
            website='https://testngo.org',
            partnership_type='ngo',
            proposed_collaboration='Joint community health program',
            resources_offered='Medical volunteers and equipment',
            expected_outcomes='Improved health services in rural areas',
            status='new'
        )
        
        self.assertEqual(submission.organization_name, 'Test NGO')
        self.assertEqual(submission.partnership_type, 'ngo')
        self.assertEqual(submission.status, 'new')
        self.assertIsNone(submission.reviewed_at)
        self.assertIsNone(submission.reviewed_by)
    
    def test_partnership_review_process(self):
        """Test partnership review workflow."""
        submission = PartnershipSubmission.objects.create(
            organization_name='Test Corp',
            contact_person='John CEO',
            email='john@testcorp.com',
            partnership_type='business',
            proposed_collaboration='CSR program',
            status='new'
        )
        
        # Simulate review
        submission.status = 'approved'
        submission.reviewed_by = self.reviewer
        submission.reviewed_at = timezone.now()
        submission.notes = 'Excellent proposal, proceed with partnership'
        submission.save()
        
        self.assertEqual(submission.status, 'approved')
        self.assertEqual(submission.reviewed_by, self.reviewer)
        self.assertIsNotNone(submission.reviewed_at)
    
    def test_string_representation(self):
        """Test string representation of partnership submission."""
        submission = PartnershipSubmission.objects.create(
            organization_name='Community Foundation',
            partnership_type='ngo',
            contact_person='Maria Garcia',
            email='maria@foundation.org',
            proposed_collaboration='Education program'
        )
        
        self.assertEqual(str(submission), 'Community Foundation - NGO/Non-Profit Organization')


class DonationSubmissionModelTests(TestCase):
    """Unit tests for DonationSubmission model."""
    
    def setUp(self):
        self.processor = User.objects.create_user(
            username='processor',
            email='processor@test.com',
            password='TestPass123!',
            user_type='staff'
        )
    
    def test_donation_submission_creation(self):
        """Test creating a donation submission."""
        donation = DonationSubmission.objects.create(
            donor_name='Generous Donor',
            donor_type='individual',
            email='donor@email.com',
            phone_number='09123456789',
            donation_type='monetary',
            amount=Decimal('5000.00'),
            description='Support for education programs',
            frequency='monthly',
            preferred_program='Education Initiative',
            status='inquiry'
        )
        
        self.assertEqual(donation.donor_name, 'Generous Donor')
        self.assertEqual(donation.donation_type, 'monetary')
        self.assertEqual(donation.amount, Decimal('5000.00'))
        self.assertEqual(donation.frequency, 'monthly')
        self.assertFalse(donation.receipt_issued)
    
    def test_donation_processing_workflow(self):
        """Test donation processing workflow."""
        donation = DonationSubmission.objects.create(
            donor_name='Corporate Donor',
            donor_type='business',
            email='contact@business.com',
            donation_type='goods',
            description='Office supplies and equipment',
            status='pledged'
        )
        
        # Process donation
        donation.status = 'received'
        donation.processed_by = self.processor
        donation.processed_at = timezone.now()
        donation.receipt_issued = True
        donation.notes = 'Donation received and catalogued'
        donation.save()
        
        self.assertEqual(donation.status, 'received')
        self.assertEqual(donation.processed_by, self.processor)
        self.assertTrue(donation.receipt_issued)
    
    def test_string_representation_with_amount(self):
        """Test string representation with monetary donation."""
        donation = DonationSubmission.objects.create(
            donor_name='John Philanthropist',
            donation_type='monetary',
            amount=Decimal('10000.00'),
            email='john@email.com',
            description='General donation'
        )
        
        self.assertEqual(str(donation), 'John Philanthropist - ₱10000.00 (Monetary Donation)')
    
    def test_string_representation_without_amount(self):
        """Test string representation without amount."""
        donation = DonationSubmission.objects.create(
            donor_name='Community Group',
            donation_type='volunteer_time',
            email='group@email.com',
            description='Community service volunteers'
        )
        
        self.assertEqual(str(donation), 'Community Group - Volunteer Time')


class CommunicationTemplateModelTests(TestCase):
    """Unit tests for CommunicationTemplate model."""
    
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='TestPass123!',
            user_type='information_officer'
        )
    
    def test_template_creation(self):
        """Test creating a communication template."""
        template = CommunicationTemplate.objects.create(
            name='Welcome Email',
            template_type='email',
            category='announcement',
            subject='Welcome to #FahanieCares',
            content='Dear {{name}}, welcome to our community...',
            is_active=True,
            created_by=self.creator
        )
        
        self.assertEqual(template.name, 'Welcome Email')
        self.assertEqual(template.slug, 'welcome-email')
        self.assertEqual(template.template_type, 'email')
        self.assertEqual(template.category, 'announcement')
        self.assertTrue(template.is_active)
    
    def test_slug_auto_generation(self):
        """Test automatic slug generation from name."""
        template = CommunicationTemplate.objects.create(
            name='Holiday Greeting Template',
            template_type='sms',
            category='holiday',
            content='Happy holidays from #FahanieCares!',
            created_by=self.creator
        )
        
        self.assertEqual(template.slug, 'holiday-greeting-template')
    
    def test_string_representation(self):
        """Test string representation of template."""
        template = CommunicationTemplate.objects.create(
            name='Birthday Greeting',
            template_type='email',
            category='birthday',
            content='Happy birthday!',
            created_by=self.creator
        )
        
        self.assertEqual(str(template), 'Birthday Greeting (Email)')


class CommunicationCampaignModelTests(TestCase):
    """Unit tests for CommunicationCampaign model."""
    
    def setUp(self):
        self.campaign_creator = User.objects.create_user(
            username='campaigner',
            email='campaigner@test.com',
            password='TestPass123!',
            user_type='information_officer'
        )
        
        self.template = CommunicationTemplate.objects.create(
            name='Test Template',
            template_type='email',
            category='announcement',
            content='Test content',
            created_by=self.campaign_creator
        )
        
        # Create test constituents
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        # Create test groups and chapters
        self.group = ConstituentGroup.objects.create(
            name='Test Group',
            description='Test group for campaigns'
        )
        
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.campaign_creator
        )
    
    def test_campaign_creation(self):
        """Test creating a communication campaign."""
        campaign = CommunicationCampaign.objects.create(
            name='Monthly Newsletter',
            description='Regular updates for constituents',
            template=self.template,
            subject='#FahanieCares Monthly Update',
            content='This month we accomplished...',
            status='draft',
            created_by=self.campaign_creator
        )
        
        self.assertEqual(campaign.name, 'Monthly Newsletter')
        self.assertEqual(campaign.status, 'draft')
        self.assertEqual(campaign.total_recipients, 0)
        self.assertIsNone(campaign.sent_time)
    
    def test_get_recipients_all_constituents(self):
        """Test getting all constituents as recipients."""
        campaign = CommunicationCampaign.objects.create(
            name='All Constituents Campaign',
            subject='Important Announcement',
            content='Important message for everyone',
            target_all_constituents=True,
            created_by=self.campaign_creator
        )
        
        recipients = campaign.get_recipients()
        # Should include both active users
        self.assertGreaterEqual(len(recipients), 2)
    
    def test_get_recipients_by_user_types(self):
        """Test getting recipients by user types."""
        campaign = CommunicationCampaign.objects.create(
            name='Members Only Campaign',
            subject='Member Update',
            content='Special message for members',
            target_user_types=['member'],
            created_by=self.campaign_creator
        )
        
        recipients = campaign.get_recipients()
        # Should include users with member type
        member_users = [r for r in recipients if hasattr(r, 'user_type') and r.user_type == 'member']
        self.assertGreater(len(member_users), 0)


class CommunicationMessageModelTests(TestCase):
    """Unit tests for CommunicationMessage model."""
    
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='TestPass123!',
            user_type='staff'
        )
        
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.campaign = CommunicationCampaign.objects.create(
            name='Test Campaign',
            subject='Test Subject',
            content='Test content',
            created_by=self.sender
        )
    
    def test_message_creation(self):
        """Test creating a communication message."""
        message = CommunicationMessage.objects.create(
            campaign=self.campaign,
            recipient=self.recipient,
            message_type='email',
            subject='Test Email',
            content='This is a test email message',
            status='pending'
        )
        
        self.assertEqual(message.campaign, self.campaign)
        self.assertEqual(message.recipient, self.recipient)
        self.assertEqual(message.message_type, 'email')
        self.assertEqual(message.status, 'pending')
        self.assertIsNone(message.sent_at)
    
    def test_mark_as_read(self):
        """Test marking message as read."""
        message = CommunicationMessage.objects.create(
            recipient=self.recipient,
            message_type='email',
            subject='Test',
            content='Test content',
            status='delivered'
        )
        
        # Mark as read
        message.mark_as_read()
        
        self.assertEqual(message.status, 'read')
        self.assertIsNotNone(message.read_at)
    
    def test_mark_as_read_wrong_status(self):
        """Test marking message as read from wrong status."""
        message = CommunicationMessage.objects.create(
            recipient=self.recipient,
            message_type='email',
            subject='Test',
            content='Test content',
            status='pending'  # Not delivered yet
        )
        
        # Try to mark as read
        message.mark_as_read()
        
        # Status should not change
        self.assertEqual(message.status, 'pending')
        self.assertIsNone(message.read_at)


class AnnouncementPostModelTests(TestCase):
    """Unit tests for AnnouncementPost model."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='TestPass123!',
            user_type='information_officer'
        )
        
        self.chapter = Chapter.objects.create(
            name='Test Chapter',
            municipality='Test City',
            tier='municipal',
            coordinator=self.author
        )
    
    def test_announcement_creation(self):
        """Test creating an announcement post."""
        announcement = AnnouncementPost.objects.create(
            title='Important Update',
            category='news',
            summary='Brief summary of the update',
            content='<p>Detailed content of the announcement</p>',
            status='draft',
            author=self.author
        )
        
        self.assertEqual(announcement.title, 'Important Update')
        self.assertEqual(announcement.slug, 'important-update')
        self.assertEqual(announcement.category, 'news')
        self.assertEqual(announcement.status, 'draft')
        self.assertIsNone(announcement.published_date)
    
    def test_auto_publish_date_setting(self):
        """Test automatic published_date setting when publishing."""
        announcement = AnnouncementPost.objects.create(
            title='Published Announcement',
            category='event',
            summary='Event announcement',
            content='Event details',
            status='published',
            author=self.author
        )
        
        self.assertIsNotNone(announcement.published_date)
    
    def test_slug_generation(self):
        """Test automatic slug generation."""
        announcement = AnnouncementPost.objects.create(
            title='My Special Announcement Title',
            category='update',
            summary='Summary',
            content='Content',
            author=self.author
        )
        
        self.assertEqual(announcement.slug, 'my-special-announcement-title')
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        announcement = AnnouncementPost.objects.create(
            title='Test Announcement',
            category='news',
            summary='Summary',
            content='Content',
            author=self.author
        )
        
        expected_url = reverse('announcement_detail', args=[announcement.slug])
        self.assertEqual(announcement.get_absolute_url(), expected_url)


class EmailSubscriptionModelTests(TestCase):
    """Unit tests for EmailSubscription model."""
    
    def test_subscription_creation(self):
        """Test creating an email subscription."""
        subscription = EmailSubscription.objects.create(
            email='subscriber@email.com',
            first_name='John',
            last_name='Subscriber',
            subscription_type='all',
            status='active',
            subscription_source='website'
        )
        
        self.assertEqual(subscription.email, 'subscriber@email.com')
        self.assertEqual(subscription.subscription_type, 'all')
        self.assertEqual(subscription.status, 'active')
        self.assertTrue(subscription.is_verified)
        self.assertEqual(subscription.emails_sent, 0)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        subscription = EmailSubscription.objects.create(
            email='test@email.com',
            first_name='Jane',
            last_name='Doe',
            subscription_type='general'
        )
        
        self.assertEqual(subscription.get_full_name(), 'Jane Doe')
    
    def test_unsubscribe(self):
        """Test unsubscribe method."""
        subscription = EmailSubscription.objects.create(
            email='test@email.com',
            first_name='Test',
            last_name='User',
            status='active'
        )
        
        # Unsubscribe
        subscription.unsubscribe()
        
        self.assertEqual(subscription.status, 'unsubscribed')
        self.assertIsNotNone(subscription.unsubscribed_at)
    
    def test_resubscribe(self):
        """Test resubscribe method."""
        subscription = EmailSubscription.objects.create(
            email='test@email.com',
            first_name='Test',
            last_name='User',
            status='unsubscribed'
        )
        
        # Resubscribe
        subscription.resubscribe()
        
        self.assertEqual(subscription.status, 'active')
        self.assertIsNone(subscription.unsubscribed_at)
    
    def test_unique_email_constraint(self):
        """Test unique email constraint."""
        EmailSubscription.objects.create(
            email='unique@email.com',
            first_name='First',
            last_name='User'
        )
        
        # Try to create another subscription with same email
        with self.assertRaises(IntegrityError):
            EmailSubscription.objects.create(
                email='unique@email.com',
                first_name='Second',
                last_name='User'
            )


class CommunicationSettingsModelTests(TestCase):
    """Unit tests for CommunicationSettings model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='member'
        )
    
    def test_communication_settings_creation(self):
        """Test creating communication settings."""
        settings = CommunicationSettings.objects.create(
            user=self.user,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True,
            allow_marketing=False,
            preferred_language='en'
        )
        
        self.assertEqual(settings.user, self.user)
        self.assertTrue(settings.email_enabled)
        self.assertFalse(settings.sms_enabled)
        self.assertTrue(settings.push_enabled)
        self.assertFalse(settings.allow_marketing)
        self.assertEqual(settings.preferred_language, 'en')
    
    def test_quiet_hours_settings(self):
        """Test quiet hours settings."""
        settings = CommunicationSettings.objects.create(
            user=self.user,
            quiet_hours_enabled=True,
            quiet_hours_start=time(22, 0),  # 10 PM
            quiet_hours_end=time(7, 0)     # 7 AM
        )
        
        self.assertTrue(settings.quiet_hours_enabled)
        self.assertEqual(settings.quiet_hours_start, time(22, 0))
        self.assertEqual(settings.quiet_hours_end, time(7, 0))
    
    def test_string_representation(self):
        """Test string representation of communication settings."""
        settings = CommunicationSettings.objects.create(user=self.user)
        
        expected_str = f"Communication settings for {self.user.get_full_name()}"
        self.assertEqual(str(settings), expected_str)


# ==============================
# INTEGRATION TESTS
# ==============================

class CommunicationWorkflowIntegrationTests(TestCase):
    """Integration tests for communication workflows."""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.info_officer = User.objects.create_user(
            username='info_officer',
            email='info@test.com',
            password='TestPass123!',
            user_type='information_officer'
        )
        
        self.member1 = User.objects.create_user(
            username='member1',
            email='member1@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.member2 = User.objects.create_user(
            username='member2',
            email='member2@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        # Create communication template
        self.template = CommunicationTemplate.objects.create(
            name='Newsletter Template',
            template_type='email',
            category='newsletter',
            subject='#FahanieCares Newsletter',
            content='Dear {{name}}, here are this month\'s updates...',
            created_by=self.info_officer
        )
    
    def test_campaign_creation_and_sending_workflow(self):
        """Test complete campaign creation and sending workflow."""
        self.client.login(username='info_officer', password='TestPass123!')
        
        # 1. Create campaign
        campaign = CommunicationCampaign.objects.create(
            name='Monthly Newsletter Campaign',
            description='Regular monthly updates',
            template=self.template,
            subject='April Newsletter',
            content='April updates and announcements',
            target_all_constituents=True,
            created_by=self.info_officer
        )
        
        # 2. Verify recipients calculation
        recipients = campaign.get_recipients()
        self.assertGreaterEqual(len(recipients), 2)  # At least our 2 members
        
        # 3. Create messages for recipients
        for recipient in recipients[:2]:  # Test with first 2 recipients
            message = CommunicationMessage.objects.create(
                campaign=campaign,
                recipient=recipient,
                message_type='email',
                subject=campaign.subject,
                content=campaign.content,
                status='pending'
            )
        
        # 4. Simulate sending
        campaign.status = 'sending'
        campaign.total_recipients = 2
        campaign.save()
        
        # 5. Mark messages as sent
        for message in campaign.messages.all():
            message.status = 'sent'
            message.sent_at = timezone.now()
            message.save()
        
        # 6. Update campaign status
        campaign.status = 'sent'
        campaign.sent_time = timezone.now()
        campaign.successful_sends = 2
        campaign.save()
        
        # Verify final state
        self.assertEqual(campaign.status, 'sent')
        self.assertEqual(campaign.successful_sends, 2)
        self.assertIsNotNone(campaign.sent_time)
    
    def test_contact_form_submission_workflow(self):
        """Test contact form submission and response workflow."""
        # 1. Create contact form submission
        submission = ContactFormSubmission.objects.create(
            first_name='Maria',
            last_name='Garcia',
            email='maria@email.com',
            phone_number='09123456789',
            subject='assistance',
            message='I need help with healthcare assistance for my family',
            form_source='website_contact_form'
        )
        
        # 2. Verify submission created properly
        self.assertEqual(submission.status, 'new')
        self.assertTrue(submission.is_recent)
        
        # 3. Assign to staff for review
        submission.assigned_to = self.info_officer
        submission.status = 'in_progress'
        submission.internal_notes = 'Forwarded to healthcare assistance team'
        submission.save()
        
        # 4. Resolve submission
        submission.status = 'resolved'
        submission.internal_notes += '\nResolved: Connected with partner clinic'
        submission.save()
        
        # Verify final state
        self.assertEqual(submission.status, 'resolved')
        self.assertEqual(submission.assigned_to, self.info_officer)
        self.assertIn('Connected with partner clinic', submission.internal_notes)
    
    def test_email_subscription_management_workflow(self):
        """Test email subscription management workflow."""
        # 1. Create subscription
        subscription = EmailSubscription.objects.create(
            email='newsletter@email.com',
            first_name='Newsletter',
            last_name='Subscriber',
            subscription_type='all',
            subscription_source='website'
        )
        
        # 2. Verify initial state
        self.assertEqual(subscription.status, 'active')
        self.assertEqual(subscription.emails_sent, 0)
        
        # 3. Simulate sending newsletters
        subscription.emails_sent += 1
        subscription.last_engagement = timezone.now()
        subscription.save()
        
        # 4. Simulate user engagement (opening email)
        subscription.emails_opened += 1
        subscription.save()
        
        # 5. User decides to unsubscribe
        subscription.unsubscribe()
        
        # Verify final state
        self.assertEqual(subscription.status, 'unsubscribed')
        self.assertIsNotNone(subscription.unsubscribed_at)
        self.assertEqual(subscription.emails_sent, 1)
        self.assertEqual(subscription.emails_opened, 1)


class CommunicationSystemIntegrationTests(TestCase):
    """Integration tests with other #FahanieCares systems."""
    
    def setUp(self):
        self.client = Client()
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='TestPass123!',
            user_type='coordinator'
        )
        
        # Create chapter for targeting
        self.chapter = Chapter.objects.create(
            name='Cotabato Chapter',
            municipality='Cotabato City',
            tier='municipal',
            coordinator=self.coordinator
        )
    
    def test_chapter_targeted_announcements(self):
        """Test creating announcements targeted to specific chapters."""
        # Create announcement targeted to specific chapter
        announcement = AnnouncementPost.objects.create(
            title='Cotabato Chapter Meeting',
            category='event',
            summary='Monthly chapter meeting announcement',
            content='<p>Join us for our monthly chapter meeting...</p>',
            status='published',
            target_all=False,
            author=self.coordinator
        )
        
        # Target specific chapter
        announcement.target_chapters.add(self.chapter)
        
        # Verify targeting
        self.assertFalse(announcement.target_all)
        self.assertEqual(announcement.target_chapters.count(), 1)
        self.assertIn(self.chapter, announcement.target_chapters.all())


# ==============================
# EDGE CASE AND ERROR HANDLING TESTS
# ==============================

class CommunicationEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='member'
        )
    
    def test_email_validation(self):
        """Test email validation in models."""
        # Test invalid email in contact form
        with self.assertRaises(ValidationError):
            submission = ContactFormSubmission(
                first_name='Test',
                last_name='User',
                email='invalid-email',
                subject='test',
                message='test message',
                form_source='test'
            )
            submission.full_clean()
    
    def test_empty_campaign_recipients(self):
        """Test campaign with no recipients."""
        campaign = CommunicationCampaign.objects.create(
            name='Empty Campaign',
            subject='No Recipients',
            content='This campaign has no recipients',
            target_all_constituents=False,
            created_by=self.user
        )
        
        recipients = campaign.get_recipients()
        self.assertEqual(len(recipients), 0)
    
    def test_template_without_creator(self):
        """Test template creation without creator."""
        template = CommunicationTemplate.objects.create(
            name='Anonymous Template',
            template_type='email',
            category='announcement',
            content='Template without creator'
        )
        
        self.assertIsNone(template.created_by)
        self.assertEqual(template.name, 'Anonymous Template')
    
    def test_message_retry_count(self):
        """Test message retry functionality."""
        message = CommunicationMessage.objects.create(
            recipient=self.user,
            message_type='email',
            subject='Test',
            content='Test content',
            status='failed',
            error_message='SMTP connection failed',
            retry_count=0
        )
        
        # Simulate retry
        message.retry_count += 1
        message.error_message = 'Second attempt failed'
        message.save()
        
        self.assertEqual(message.retry_count, 1)
        self.assertEqual(message.status, 'failed')
    
    def test_duplicate_email_subscription(self):
        """Test handling duplicate email subscriptions."""
        # Create first subscription
        EmailSubscription.objects.create(
            email='duplicate@email.com',
            first_name='First',
            last_name='User'
        )
        
        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            EmailSubscription.objects.create(
                email='duplicate@email.com',
                first_name='Second',
                last_name='User'
            )


# ==============================
# PERFORMANCE TESTS
# ==============================

class CommunicationPerformanceTests(TestCase):
    """Performance tests for communications system."""
    
    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='TestPass123!',
            user_type='information_officer'
        )
    
    def test_large_campaign_recipients_calculation(self):
        """Test performance with large number of recipients."""
        # Create many users
        users = []
        for i in range(100):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='TestPass123!',
                user_type='member'
            )
            users.append(user)
        
        # Create campaign targeting all users
        campaign = CommunicationCampaign.objects.create(
            name='Large Campaign',
            subject='Mass Communication',
            content='Message to many recipients',
            target_all_constituents=True,
            created_by=self.creator
        )
        
        # Test recipient calculation performance
        import time
        start_time = time.time()
        recipients = campaign.get_recipients()
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 5.0)  # Less than 5 seconds
        self.assertGreaterEqual(len(recipients), 100)
    
    def test_bulk_message_creation(self):
        """Test bulk message creation performance."""
        # Create recipients
        recipients = []
        for i in range(50):
            user = User.objects.create_user(
                username=f'recipient{i}',
                email=f'recipient{i}@test.com',
                password='TestPass123!',
                user_type='member'
            )
            recipients.append(user)
        
        campaign = CommunicationCampaign.objects.create(
            name='Bulk Test',
            subject='Bulk Messages',
            content='Testing bulk creation',
            created_by=self.creator
        )
        
        # Test bulk creation
        import time
        start_time = time.time()
        
        messages = []
        for recipient in recipients:
            message = CommunicationMessage(
                campaign=campaign,
                recipient=recipient,
                message_type='email',
                subject=campaign.subject,
                content=campaign.content
            )
            messages.append(message)
        
        CommunicationMessage.objects.bulk_create(messages)
        end_time = time.time()
        
        # Should complete efficiently
        self.assertLess(end_time - start_time, 2.0)  # Less than 2 seconds
        self.assertEqual(CommunicationMessage.objects.filter(campaign=campaign).count(), 50)