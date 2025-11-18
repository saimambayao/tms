"""
Comprehensive test suite for Notifications application.
Tests models, notification delivery, preferences, and workflow management.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time
import json
import uuid

from .models import (
    NotificationChannel, NotificationType, NotificationPreference,
    Notification, NotificationTemplate, NotificationLog, NotificationQueue
)
from apps.referrals.models import ServiceReferral

User = get_user_model()


# ==============================
# UNIT TESTS - MODELS
# ==============================

class NotificationPreferenceModelTests(TestCase):
    """Unit tests for NotificationPreference model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='member'
        )
    
    def test_notification_preference_creation(self):
        """Test creating notification preferences."""
        preferences = NotificationPreference.objects.create(
            user=self.user,
            email_enabled=True,
            in_app_enabled=True,
            push_enabled=False,
            sms_enabled=False,
            digest_frequency='daily',
            timezone='Asia/Manila'
        )
        
        self.assertEqual(preferences.user, self.user)
        self.assertTrue(preferences.email_enabled)
        self.assertTrue(preferences.in_app_enabled)
        self.assertFalse(preferences.push_enabled)
        self.assertFalse(preferences.sms_enabled)
        self.assertEqual(preferences.digest_frequency, 'daily')
        self.assertEqual(preferences.timezone, 'Asia/Manila')
    
    def test_channel_enabled_methods(self):
        """Test is_channel_enabled method."""
        preferences = NotificationPreference.objects.create(
            user=self.user,
            email_enabled=True,
            in_app_enabled=False,
            push_enabled=True,
            sms_enabled=False
        )
        
        self.assertTrue(preferences.is_channel_enabled(NotificationChannel.EMAIL))
        self.assertFalse(preferences.is_channel_enabled(NotificationChannel.IN_APP))
        self.assertTrue(preferences.is_channel_enabled(NotificationChannel.PUSH))
        self.assertFalse(preferences.is_channel_enabled(NotificationChannel.SMS))
    
    def test_type_preference_management(self):
        """Test notification type preference management."""
        preferences = NotificationPreference.objects.create(
            user=self.user,
            enabled_types={
                'referral_status': True,
                'referral_comment': False,
                'document_upload': True
            }
        )
        
        # Test checking type preferences
        self.assertTrue(preferences.is_type_enabled('referral_status'))
        self.assertFalse(preferences.is_type_enabled('referral_comment'))
        self.assertTrue(preferences.is_type_enabled('document_upload'))
        
        # Test default behavior for unset types
        self.assertTrue(preferences.is_type_enabled('chapter_event'))  # Default to True
        
        # Test setting type preference
        preferences.set_type_preference('chapter_event', False)
        self.assertFalse(preferences.is_type_enabled('chapter_event'))
    
    def test_quiet_hours_configuration(self):
        """Test quiet hours configuration."""
        preferences = NotificationPreference.objects.create(
            user=self.user,
            quiet_hours_start=time(22, 0),  # 10 PM
            quiet_hours_end=time(7, 0),     # 7 AM
            timezone='Asia/Manila'
        )
        
        self.assertEqual(preferences.quiet_hours_start, time(22, 0))
        self.assertEqual(preferences.quiet_hours_end, time(7, 0))
        self.assertEqual(preferences.timezone, 'Asia/Manila')
    
    def test_string_representation(self):
        """Test string representation of notification preferences."""
        preferences = NotificationPreference.objects.create(user=self.user)
        
        expected_str = f"Notification preferences for {self.user}"
        self.assertEqual(str(preferences), expected_str)


class NotificationModelTests(TestCase):
    """Unit tests for Notification model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='TestPass123!',
            user_type='admin'
        )
    
    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.REFERRAL_STATUS,
            title='Referral Status Update',
            message='Your referral has been processed and approved.',
            priority='high',
            data={'referral_id': '12345', 'status': 'approved'}
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.type, NotificationType.REFERRAL_STATUS)
        self.assertEqual(notification.title, 'Referral Status Update')
        self.assertEqual(notification.priority, 'high')
        self.assertFalse(notification.is_read)
        self.assertIsInstance(notification.id, uuid.UUID)
        self.assertEqual(notification.data['referral_id'], '12345')
    
    def test_notification_with_related_object(self):
        """Test notification with generic foreign key to related object."""
        # Create a referral object to link to
        referral = ServiceReferral.objects.create(
            full_name='Test User',
            email='test@email.com',
            phone_number='09123456789',
            service_type='Medical Assistance',
            description='Medical assistance request',
            urgency_level='medium',
            referral_source='walk_in'
        )
        
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.REFERRAL_STATUS,
            title='Referral Update',
            message='Your referral status has changed',
            content_type=ContentType.objects.get_for_model(ServiceReferral),
            object_id=str(referral.id),
            priority='normal'
        )
        
        # Test generic foreign key relationship
        self.assertEqual(notification.related_object, referral)
        self.assertEqual(notification.content_type, ContentType.objects.get_for_model(ServiceReferral))
        self.assertEqual(notification.object_id, str(referral.id))
    
    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.DOCUMENT_UPLOAD,
            title='Document Uploaded',
            message='A new document has been uploaded to your case.'
        )
        
        # Initially unread
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        
        # Mark as read
        notification.mark_as_read()
        
        # Verify read status
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)
        
        # Test idempotency - calling mark_as_read again shouldn't change read_at
        original_read_at = notification.read_at
        notification.mark_as_read()
        self.assertEqual(notification.read_at, original_read_at)
    
    def test_delivery_tracking(self):
        """Test notification delivery tracking."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.CHAPTER_EVENT,
            title='Chapter Meeting',
            message='You have been invited to a chapter meeting.',
            channels_attempted=[NotificationChannel.EMAIL, NotificationChannel.PUSH],
            channels_delivered=[]
        )
        
        # Mark as delivered via email
        notification.mark_delivered(NotificationChannel.EMAIL)
        
        self.assertIn(NotificationChannel.EMAIL, notification.channels_delivered)
        self.assertTrue(notification.email_sent)
        self.assertFalse(notification.push_sent)
        self.assertFalse(notification.sms_sent)
        
        # Mark as delivered via push
        notification.mark_delivered(NotificationChannel.PUSH)
        
        self.assertIn(NotificationChannel.PUSH, notification.channels_delivered)
        self.assertTrue(notification.push_sent)
        
        # Mark as delivered via SMS
        notification.mark_delivered(NotificationChannel.SMS)
        
        self.assertIn(NotificationChannel.SMS, notification.channels_delivered)
        self.assertTrue(notification.sms_sent)
    
    def test_notification_expiration(self):
        """Test notification expiration functionality."""
        # Create expired notification
        expired_notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title='Expired Announcement',
            message='This announcement has expired.',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create active notification
        active_notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.ACCOUNT_UPDATE,
            title='Account Update',
            message='Your account has been updated.',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # Test expiration status
        self.assertTrue(expired_notification.is_expired)
        self.assertFalse(active_notification.is_expired)
        
        # Test notification without expiration
        permanent_notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.SERVICE_UPDATE,
            title='Service Update',
            message='Service information updated.'
        )
        
        self.assertFalse(permanent_notification.is_expired)
    
    def test_string_representation(self):
        """Test notification string representation."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.REFERRAL_STATUS,
            title='Test Notification',
            message='Test message'
        )
        
        expected_str = f"referral_status notification for {self.user} - Test Notification"
        self.assertEqual(str(notification), expected_str)


class NotificationTemplateModelTests(TestCase):
    """Unit tests for NotificationTemplate model."""
    
    def test_notification_template_creation(self):
        """Test creating a notification template."""
        template = NotificationTemplate.objects.create(
            name='Referral Status Update Template',
            type=NotificationType.REFERRAL_STATUS,
            subject_template='Referral Status Update for {user.first_name}',
            body_template='Dear {user.first_name}, your referral #{referral.id} status is now {referral.status}.',
            html_template='<p>Dear {user.first_name}, your referral <strong>#{referral.id}</strong> status is now <em>{referral.status}</em>.</p>',
            push_title_template='Referral Update',
            push_body_template='Your referral #{referral.id} is {referral.status}',
            sms_template='Referral #{referral.id} is {referral.status}. Visit fahaniecares.ph for details.',
            variables=['user.first_name', 'user.last_name', 'referral.id', 'referral.status'],
            is_active=True
        )
        
        self.assertEqual(template.name, 'Referral Status Update Template')
        self.assertEqual(template.type, NotificationType.REFERRAL_STATUS)
        self.assertTrue(template.is_active)
        self.assertIn('user.first_name', template.variables)
        self.assertIn('referral.status', template.variables)
    
    def test_template_channel_specific_content(self):
        """Test channel-specific template content."""
        template = NotificationTemplate.objects.create(
            name='Multi-Channel Template',
            type=NotificationType.DOCUMENT_UPLOAD,
            subject_template='Document Upload Notification',
            body_template='A document has been uploaded to your case.',
            push_title_template='New Document',
            push_body_template='Document uploaded',
            sms_template='Doc uploaded. Check app.'
        )
        
        # Test that different channels have appropriate content lengths
        self.assertLessEqual(len(template.push_title_template), 100)
        self.assertLessEqual(len(template.push_body_template), 255)
        self.assertLessEqual(len(template.sms_template), 160)
    
    def test_template_variables_management(self):
        """Test template variables management."""
        template = NotificationTemplate.objects.create(
            name='Chapter Event Template',
            type=NotificationType.CHAPTER_EVENT,
            subject_template='Chapter Event: {event.title}',
            body_template='You are invited to {event.title} on {event.date} at {event.location}.',
            variables=['event.title', 'event.date', 'event.location', 'user.name']
        )
        
        self.assertEqual(len(template.variables), 4)
        self.assertIn('event.title', template.variables)
        self.assertIn('event.date', template.variables)
        self.assertIn('event.location', template.variables)
        self.assertIn('user.name', template.variables)
    
    def test_string_representation(self):
        """Test template string representation."""
        template = NotificationTemplate.objects.create(
            name='Test Template',
            type=NotificationType.SERVICE_UPDATE,
            subject_template='Test Subject',
            body_template='Test Body'
        )
        
        expected_str = f"Service Update - Test Template"
        self.assertEqual(str(template), expected_str)


class NotificationLogModelTests(TestCase):
    """Unit tests for NotificationLog model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.REFERRAL_STATUS,
            title='Test Notification',
            message='Test message'
        )
    
    def test_notification_log_creation(self):
        """Test creating a notification log entry."""
        log = NotificationLog.objects.create(
            notification=self.notification,
            channel=NotificationChannel.EMAIL,
            status='sent',
            metadata={'email_id': 'msg_12345', 'provider': 'sendgrid'},
            sent_at=timezone.now()
        )
        
        self.assertEqual(log.notification, self.notification)
        self.assertEqual(log.channel, NotificationChannel.EMAIL)
        self.assertEqual(log.status, 'sent')
        self.assertEqual(log.metadata['email_id'], 'msg_12345')
        self.assertIsNotNone(log.sent_at)
    
    def test_log_status_tracking(self):
        """Test notification log status tracking."""
        # Create log with initial status
        log = NotificationLog.objects.create(
            notification=self.notification,
            channel=NotificationChannel.PUSH,
            status='pending'
        )
        
        # Update to sent
        log.status = 'sent'
        log.sent_at = timezone.now()
        log.save()
        
        self.assertEqual(log.status, 'sent')
        self.assertIsNotNone(log.sent_at)
        
        # Update to delivered
        log.status = 'delivered'
        log.delivered_at = timezone.now()
        log.save()
        
        self.assertEqual(log.status, 'delivered')
        self.assertIsNotNone(log.delivered_at)
        
        # Test failed status
        failed_log = NotificationLog.objects.create(
            notification=self.notification,
            channel=NotificationChannel.SMS,
            status='failed',
            error_message='Invalid phone number',
            failed_at=timezone.now()
        )
        
        self.assertEqual(failed_log.status, 'failed')
        self.assertEqual(failed_log.error_message, 'Invalid phone number')
        self.assertIsNotNone(failed_log.failed_at)
    
    def test_log_metadata_tracking(self):
        """Test notification log metadata tracking."""
        metadata = {
            'provider': 'twilio',
            'message_sid': 'SM1234567890',
            'cost': 0.05,
            'segments': 1
        }
        
        log = NotificationLog.objects.create(
            notification=self.notification,
            channel=NotificationChannel.SMS,
            status='delivered',
            metadata=metadata
        )
        
        self.assertEqual(log.metadata, metadata)
        self.assertEqual(log.metadata['provider'], 'twilio')
        self.assertEqual(log.metadata['cost'], 0.05)
    
    def test_string_representation(self):
        """Test log string representation."""
        log = NotificationLog.objects.create(
            notification=self.notification,
            channel=NotificationChannel.EMAIL,
            status='sent'
        )
        
        expected_str = f"Email log for {self.notification.title}"
        self.assertEqual(str(log), expected_str)


class NotificationQueueModelTests(TestCase):
    """Unit tests for NotificationQueue model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title='Queued Notification',
            message='This notification is queued for later delivery'
        )
    
    def test_notification_queue_creation(self):
        """Test creating a notification queue item."""
        scheduled_time = timezone.now() + timedelta(hours=2)
        
        queue_item = NotificationQueue.objects.create(
            notification=self.notification,
            channel=NotificationChannel.EMAIL,
            priority=5,
            scheduled_for=scheduled_time,
            max_retries=3
        )
        
        self.assertEqual(queue_item.notification, self.notification)
        self.assertEqual(queue_item.channel, NotificationChannel.EMAIL)
        self.assertEqual(queue_item.priority, 5)
        self.assertEqual(queue_item.scheduled_for, scheduled_time)
        self.assertEqual(queue_item.max_retries, 3)
        self.assertFalse(queue_item.is_processed)
        self.assertEqual(queue_item.retry_count, 0)
    
    def test_queue_processing(self):
        """Test queue item processing."""
        queue_item = NotificationQueue.objects.create(
            notification=self.notification,
            channel=NotificationChannel.PUSH,
            scheduled_for=timezone.now() - timedelta(minutes=30)
        )
        
        # Process the queue item
        queue_item.is_processed = True
        queue_item.processed_at = timezone.now()
        queue_item.save()
        
        self.assertTrue(queue_item.is_processed)
        self.assertIsNotNone(queue_item.processed_at)
    
    def test_queue_retry_mechanism(self):
        """Test queue retry mechanism."""
        queue_item = NotificationQueue.objects.create(
            notification=self.notification,
            channel=NotificationChannel.SMS,
            max_retries=3
        )
        
        # Simulate first failure
        queue_item.retry_count += 1
        queue_item.last_error = 'Network timeout'
        queue_item.save()
        
        self.assertEqual(queue_item.retry_count, 1)
        self.assertEqual(queue_item.last_error, 'Network timeout')
        self.assertFalse(queue_item.is_processed)
        
        # Simulate second failure
        queue_item.retry_count += 1
        queue_item.last_error = 'Invalid credentials'
        queue_item.save()
        
        self.assertEqual(queue_item.retry_count, 2)
        
        # Check if max retries exceeded
        max_retries_exceeded = queue_item.retry_count >= queue_item.max_retries
        self.assertFalse(max_retries_exceeded)  # Still has 1 retry left
        
        # Simulate final failure
        queue_item.retry_count += 1
        queue_item.save()
        
        max_retries_exceeded = queue_item.retry_count >= queue_item.max_retries
        self.assertTrue(max_retries_exceeded)  # Now exceeded
    
    def test_queue_priority_ordering(self):
        """Test queue priority ordering."""
        # Create queue items with different priorities
        low_priority = NotificationQueue.objects.create(
            notification=self.notification,
            channel=NotificationChannel.EMAIL,
            priority=1
        )
        
        high_priority = NotificationQueue.objects.create(
            notification=self.notification,
            channel=NotificationChannel.PUSH,
            priority=10
        )
        
        medium_priority = NotificationQueue.objects.create(
            notification=self.notification,
            channel=NotificationChannel.SMS,
            priority=5
        )
        
        # Test ordering
        queue_items = list(NotificationQueue.objects.all())
        self.assertEqual(queue_items[0], high_priority)  # Highest priority first
        self.assertEqual(queue_items[1], medium_priority)
        self.assertEqual(queue_items[2], low_priority)
    
    def test_string_representation(self):
        """Test queue item string representation."""
        queue_item = NotificationQueue.objects.create(
            notification=self.notification,
            channel=NotificationChannel.EMAIL
        )
        
        expected_str = f"Queue item for {self.notification.title} via Email"
        self.assertEqual(str(queue_item), expected_str)


# ==============================
# INTEGRATION TESTS
# ==============================

class NotificationWorkflowIntegrationTests(TestCase):
    """Integration tests for notification workflows."""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.user = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='TestPass123!',
            user_type='member'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='TestPass123!',
            user_type='admin'
        )
        
        # Create notification preferences
        self.preferences = NotificationPreference.objects.create(
            user=self.user,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False,
            digest_frequency='immediate'
        )
    
    def test_complete_notification_workflow(self):
        """Test complete notification creation and delivery workflow."""
        # 1. Create a referral to trigger notification
        referral = ServiceReferral.objects.create(
            full_name='John Doe',
            email='john@email.com',
            phone_number='09123456789',
            service_type='Medical Assistance',
            description='Need medical assistance',
            urgency_level='high',
            referral_source='online'
        )
        
        # 2. Create notification with related object
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.REFERRAL_STATUS,
            title='New Referral Received',
            message='Your referral for medical assistance has been received and will be processed.',
            priority='high',
            content_type=ContentType.objects.get_for_model(ServiceReferral),
            object_id=str(referral.id),
            data={'referral_number': str(referral.id), 'service_type': referral.service_type}
        )
        
        # 3. Queue notification for delivery
        email_queue = NotificationQueue.objects.create(
            notification=notification,
            channel=NotificationChannel.EMAIL,
            priority=5,  # High priority
            scheduled_for=timezone.now()
        )
        
        push_queue = NotificationQueue.objects.create(
            notification=notification,
            channel=NotificationChannel.PUSH,
            priority=5,
            scheduled_for=timezone.now()
        )
        
        # 4. Simulate processing email notification
        email_log = NotificationLog.objects.create(
            notification=notification,
            channel=NotificationChannel.EMAIL,
            status='pending'
        )
        
        # Mark as sent
        email_log.status = 'sent'
        email_log.sent_at = timezone.now()
        email_log.metadata = {'email_id': 'msg_12345', 'provider': 'sendgrid'}
        email_log.save()
        
        # Mark notification as delivered via email
        notification.mark_delivered(NotificationChannel.EMAIL)
        
        # Mark queue item as processed
        email_queue.is_processed = True
        email_queue.processed_at = timezone.now()
        email_queue.save()
        
        # 5. Simulate processing push notification
        push_log = NotificationLog.objects.create(
            notification=notification,
            channel=NotificationChannel.PUSH,
            status='delivered',
            delivered_at=timezone.now(),
            metadata={'push_id': 'push_67890', 'provider': 'firebase'}
        )
        
        notification.mark_delivered(NotificationChannel.PUSH)
        
        push_queue.is_processed = True
        push_queue.processed_at = timezone.now()
        push_queue.save()
        
        # 6. Verify final state
        notification.refresh_from_db()
        self.assertTrue(notification.email_sent)
        self.assertTrue(notification.push_sent)
        self.assertFalse(notification.sms_sent)
        self.assertIn(NotificationChannel.EMAIL, notification.channels_delivered)
        self.assertIn(NotificationChannel.PUSH, notification.channels_delivered)
        
        # Verify queue processing
        self.assertTrue(email_queue.is_processed)
        self.assertTrue(push_queue.is_processed)
        
        # Verify logs
        self.assertEqual(notification.logs.count(), 2)
        self.assertTrue(notification.logs.filter(channel=NotificationChannel.EMAIL, status='sent').exists())
        self.assertTrue(notification.logs.filter(channel=NotificationChannel.PUSH, status='delivered').exists())
    
    def test_notification_preference_integration(self):
        """Test notification delivery based on user preferences."""
        # Create notification
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.CHAPTER_EVENT,
            title='Chapter Meeting Invitation',
            message='You are invited to the monthly chapter meeting.'
        )
        
        # Check user preferences
        preferences = self.user.notification_preferences
        
        # Queue only for enabled channels
        if preferences.is_channel_enabled(NotificationChannel.EMAIL):
            NotificationQueue.objects.create(
                notification=notification,
                channel=NotificationChannel.EMAIL
            )
        
        if preferences.is_channel_enabled(NotificationChannel.PUSH):
            NotificationQueue.objects.create(
                notification=notification,
                channel=NotificationChannel.PUSH
            )
        
        if preferences.is_channel_enabled(NotificationChannel.SMS):
            NotificationQueue.objects.create(
                notification=notification,
                channel=NotificationChannel.SMS
            )
        
        # Verify queue items based on preferences
        queue_items = NotificationQueue.objects.filter(notification=notification)
        
        # Should have email and push (enabled), but not SMS (disabled)
        self.assertEqual(queue_items.count(), 2)
        self.assertTrue(queue_items.filter(channel=NotificationChannel.EMAIL).exists())
        self.assertTrue(queue_items.filter(channel=NotificationChannel.PUSH).exists())
        self.assertFalse(queue_items.filter(channel=NotificationChannel.SMS).exists())
    
    def test_template_based_notification_creation(self):
        """Test creating notifications using templates."""
        # Create template
        template = NotificationTemplate.objects.create(
            name='Referral Approved Template',
            type=NotificationType.REFERRAL_STATUS,
            subject_template='Referral #{referral_id} Approved',
            body_template='Dear {user_name}, your referral #{referral_id} for {service_type} has been approved.',
            push_title_template='Referral Approved',
            push_body_template='Referral #{referral_id} approved',
            variables=['user_name', 'referral_id', 'service_type']
        )
        
        # Create referral
        referral = ServiceReferral.objects.create(
            full_name='Jane Smith',
            email='jane@email.com',
            phone_number='09987654321',
            service_type='Educational Assistance',
            description='Need educational assistance',
            urgency_level='medium',
            referral_source='walk_in',
            status='approved'
        )
        
        # Simulate template-based notification creation
        template_data = {
            'user_name': self.user.get_full_name() or self.user.username,
            'referral_id': str(referral.id),
            'service_type': referral.service_type
        }
        
        # Create notification using template data
        notification = Notification.objects.create(
            user=self.user,
            type=template.type,
            title=template.subject_template.format(**template_data),
            message=template.body_template.format(**template_data),
            content_type=ContentType.objects.get_for_model(ServiceReferral),
            object_id=str(referral.id),
            data={'template_id': template.id, 'template_data': template_data}
        )
        
        # Verify template substitution
        self.assertIn(str(referral.id), notification.title)
        self.assertIn('Educational Assistance', notification.message)
        self.assertIn(self.user.username, notification.message)


# ==============================
# EDGE CASE AND ERROR HANDLING TESTS
# ==============================

class NotificationEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!',
            user_type='member'
        )
    
    def test_notification_without_related_object(self):
        """Test notification without related object."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title='System Maintenance',
            message='The system will be under maintenance tonight.'
        )
        
        self.assertIsNone(notification.content_type)
        self.assertIsNone(notification.object_id)
        self.assertIsNone(notification.related_object)
    
    def test_notification_with_invalid_related_object(self):
        """Test notification with invalid related object reference."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.REFERRAL_STATUS,
            title='Invalid Reference',
            message='This notification has an invalid object reference',
            content_type=ContentType.objects.get_for_model(ServiceReferral),
            object_id='999999'  # Non-existent ID
        )
        
        # Should not raise exception, but related_object should be None
        self.assertIsNone(notification.related_object)
    
    def test_preferences_with_empty_enabled_types(self):
        """Test preferences with empty enabled_types."""
        preferences = NotificationPreference.objects.create(
            user=self.user,
            enabled_types={}
        )
        
        # Should default to enabled for all types
        self.assertTrue(preferences.is_type_enabled(NotificationType.REFERRAL_STATUS))
        self.assertTrue(preferences.is_type_enabled(NotificationType.DOCUMENT_UPLOAD))
    
    def test_notification_delivery_to_disabled_channel(self):
        """Test attempting to mark delivery on a channel that wasn't attempted."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.SERVICE_UPDATE,
            title='Service Update',
            message='Service information updated',
            channels_attempted=[NotificationChannel.EMAIL]
        )
        
        # Mark as delivered via SMS (not attempted)
        notification.mark_delivered(NotificationChannel.SMS)
        
        # Should still work (business logic should validate this)
        self.assertTrue(notification.sms_sent)
        self.assertIn(NotificationChannel.SMS, notification.channels_delivered)
    
    def test_queue_item_with_past_scheduled_time(self):
        """Test queue item scheduled for the past."""
        past_time = timezone.now() - timedelta(hours=2)
        
        queue_item = NotificationQueue.objects.create(
            notification=Notification.objects.create(
                user=self.user,
                type=NotificationType.ACCOUNT_UPDATE,
                title='Past Notification',
                message='This was scheduled for the past'
            ),
            channel=NotificationChannel.EMAIL,
            scheduled_for=past_time
        )
        
        # Should be created successfully
        self.assertEqual(queue_item.scheduled_for, past_time)
        self.assertFalse(queue_item.is_processed)
    
    def test_notification_log_without_timestamps(self):
        """Test notification log without sent/delivered timestamps."""
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.CHAPTER_EVENT,
            title='Event Notification',
            message='Event notification without timestamps'
        )
        
        log = NotificationLog.objects.create(
            notification=notification,
            channel=NotificationChannel.PUSH,
            status='failed',
            error_message='Device not registered'
        )
        
        self.assertIsNone(log.sent_at)
        self.assertIsNone(log.delivered_at)
        self.assertIsNotNone(log.created_at)
        self.assertEqual(log.error_message, 'Device not registered')


# ==============================
# PERFORMANCE TESTS
# ==============================

class NotificationPerformanceTests(TestCase):
    """Performance tests for notifications system."""
    
    def setUp(self):
        self.users = []
        for i in range(20):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='TestPass123!',
                user_type='member'
            )
            self.users.append(user)
            
            # Create preferences for each user
            NotificationPreference.objects.create(user=user)
    
    def test_bulk_notification_creation(self):
        """Test performance with bulk notification creation."""
        import time
        
        notifications = []
        start_time = time.time()
        
        for user in self.users:
            notification = Notification(
                user=user,
                type=NotificationType.SYSTEM_ANNOUNCEMENT,
                title='System Update',
                message='The system has been updated with new features.',
                priority='normal'
            )
            notifications.append(notification)
        
        Notification.objects.bulk_create(notifications)
        end_time = time.time()
        
        # Should complete efficiently
        self.assertLess(end_time - start_time, 2.0)  # Less than 2 seconds
        self.assertEqual(Notification.objects.count(), 20)
    
    def test_queue_processing_performance(self):
        """Test performance with large notification queue."""
        import time
        
        # Create notifications and queue items
        notifications = []
        for user in self.users:
            notification = Notification.objects.create(
                user=user,
                type=NotificationType.SERVICE_UPDATE,
                title='Service Update',
                message='Service has been updated'
            )
            notifications.append(notification)
        
        # Create queue items
        queue_items = []
        for notification in notifications:
            for channel in [NotificationChannel.EMAIL, NotificationChannel.PUSH]:
                queue_item = NotificationQueue(
                    notification=notification,
                    channel=channel,
                    priority=1
                )
                queue_items.append(queue_item)
        
        start_time = time.time()
        NotificationQueue.objects.bulk_create(queue_items)
        end_time = time.time()
        
        # Should create queue items efficiently
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second
        self.assertEqual(NotificationQueue.objects.count(), 40)  # 20 users × 2 channels
    
    def test_notification_query_performance(self):
        """Test performance of notification queries."""
        import time
        
        # Create many notifications
        for user in self.users:
            for i in range(10):
                Notification.objects.create(
                    user=user,
                    type=NotificationType.REFERRAL_STATUS,
                    title=f'Notification {i}',
                    message=f'Test notification {i}',
                    is_read=i % 3 == 0  # Some read, some unread
                )
        
        # Test query performance
        start_time = time.time()
        
        # Get unread notifications for all users
        unread_notifications = Notification.objects.filter(is_read=False).select_related('user')
        list(unread_notifications)  # Force query execution
        
        end_time = time.time()
        
        # Should query efficiently
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second
        self.assertGreater(len(list(unread_notifications)), 0)