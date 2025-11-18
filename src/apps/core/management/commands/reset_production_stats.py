"""
Reset Production Statistics Management Command

This command resets all statistics and sample data to provide a clean 
production environment starting from zero. Use this command before 
production launch to ensure accurate statistics tracking.

Usage:
    python manage.py reset_production_stats
    python manage.py reset_production_stats --confirm
    python manage.py reset_production_stats --preserve-superusers
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reset all production statistics and sample data for clean production launch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )
        parser.add_argument(
            '--preserve-superusers',
            action='store_true',
            help='Keep all superuser accounts intact',
        )
        parser.add_argument(
            '--preserve-staff',
            action='store_true', 
            help='Keep all staff accounts intact',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                '\n=== #FahanieCares Production Statistics Reset ===\n'
            )
        )
        
        # Confirmation check
        if not options['confirm'] and not options['dry_run']:
            confirm = input(
                'This will reset ALL statistics and sample data.\n'
                'This action cannot be undone.\n'
                'Are you sure you want to continue? (yes/no): '
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        try:
            with transaction.atomic():
                self._reset_user_data(options)
                self._reset_chapters_data(options)
                self._reset_referrals_data(options)
                self._reset_communications_data(options)
                self._reset_services_data(options)
                self._reset_notifications_data(options)
                self._reset_session_data(options)
                self._reset_admin_logs(options)
                self._clear_cache(options)
                
                if not options['dry_run']:
                    self._update_statistics_cache()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✅ Production statistics reset completed successfully!\n'
                        'The platform now starts with zero statistics and clean data.\n'
                    )
                )
                
        except Exception as e:
            logger.error(f"Error resetting production stats: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error during reset: {e}')
            )

    def _reset_user_data(self, options):
        """Reset user-related data"""
        self.stdout.write('\n📊 Resetting User Data...')
        
        User = get_user_model()
        
        if options['dry_run']:
            # Count what would be deleted
            test_users = User.objects.filter(email__contains='test')
            demo_users = User.objects.filter(email__contains='demo')
            loadtest_users = User.objects.filter(username__contains='loadtest')
            
            if not options['preserve_superusers']:
                if not options['preserve_staff']:
                    # Would delete all users except developers
                    keep_users = User.objects.filter(
                        email__in=['dev@fahaniecares.gov.ph', 'admin@fahaniecares.gov.ph']
                    )
                    all_users = User.objects.exclude(
                        email__in=['dev@fahaniecares.gov.ph', 'admin@fahaniecares.gov.ph']
                    )
                else:
                    # Would delete non-staff users
                    all_users = User.objects.filter(is_staff=False, is_superuser=False)
                    keep_users = User.objects.filter(is_staff=True)
            else:
                # Would delete non-superuser users
                all_users = User.objects.filter(is_superuser=False)
                keep_users = User.objects.filter(is_superuser=True)
            
            self.stdout.write(f'  - Would delete {all_users.count()} user accounts')
            self.stdout.write(f'  - Would preserve {keep_users.count()} essential accounts')
            self.stdout.write(f'  - Test users to delete: {test_users.count()}')
            self.stdout.write(f'  - Demo users to delete: {demo_users.count()}')
            self.stdout.write(f'  - Load test users to delete: {loadtest_users.count()}')
            return

        # Actual deletion
        deleted_counts = {'test_users': 0, 'demo_users': 0, 'loadtest_users': 0, 'total': 0}
        
        # Delete test and demo users
        test_users = User.objects.filter(email__contains='test')
        deleted_counts['test_users'] = test_users.count()
        test_users.delete()
        
        demo_users = User.objects.filter(email__contains='demo') 
        deleted_counts['demo_users'] = demo_users.count()
        demo_users.delete()
        
        loadtest_users = User.objects.filter(username__contains='loadtest')
        deleted_counts['loadtest_users'] = loadtest_users.count()
        loadtest_users.delete()

        # Handle production users based on options
        if not options['preserve_superusers']:
            if not options['preserve_staff']:
                # Delete all users except essential developers
                keep_emails = ['dev@fahaniecares.gov.ph', 'admin@fahaniecares.gov.ph']
                users_to_delete = User.objects.exclude(email__in=keep_emails)
                deleted_counts['total'] = users_to_delete.count()
                users_to_delete.delete()
                self.stdout.write('  ✅ Reset all users (kept essential developer accounts)')
            else:
                # Delete only non-staff users
                non_staff = User.objects.filter(is_staff=False, is_superuser=False)
                deleted_counts['total'] = non_staff.count()
                non_staff.delete()
                self.stdout.write('  ✅ Reset non-staff users (preserved staff accounts)')
        else:
            # Delete only non-superuser users
            non_super = User.objects.filter(is_superuser=False)
            deleted_counts['total'] = non_super.count()
            non_super.delete()
            self.stdout.write('  ✅ Reset non-superuser accounts (preserved superusers)')
        
        self.stdout.write(f'  - Deleted {deleted_counts["total"]} total user accounts')
        self.stdout.write(f'  - Deleted {deleted_counts["test_users"]} test accounts')
        self.stdout.write(f'  - Deleted {deleted_counts["demo_users"]} demo accounts')
        self.stdout.write(f'  - Deleted {deleted_counts["loadtest_users"]} load test accounts')

    def _reset_chapters_data(self, options):
        """Reset chapters-related sample data"""
        self.stdout.write('\n🏛️ Resetting Chapters Data...')
        
        try:
            from apps.chapters.models import Chapter
            
            if options['dry_run']:
                test_chapters = Chapter.objects.filter(name__contains='Test')
                self.stdout.write(f'  - Would delete {test_chapters.count()} test chapters')
                return
                
            # Delete test chapters but preserve real ones
            test_chapters = Chapter.objects.filter(name__contains='Test')
            deleted_count = test_chapters.count()
            test_chapters.delete()
            
            self.stdout.write(f'  ✅ Reset test chapters (deleted {deleted_count})')
            self.stdout.write('  ✅ Preserved legitimate chapter data')
            
        except ImportError:
            self.stdout.write('  ⚠️  Chapters app not available, skipping...')

    def _reset_referrals_data(self, options):
        """Reset referrals and service request data"""
        self.stdout.write('\n📋 Resetting Referrals Data...')
        
        try:
            from apps.referrals.models import Referral, Service, Agency
            
            if options['dry_run']:
                test_referrals = Referral.objects.filter(description__contains='test')
                all_referrals = Referral.objects.all()
                test_services = Service.objects.filter(name__contains='Test')
                self.stdout.write(f'  - Would delete {all_referrals.count()} referrals')
                self.stdout.write(f'  - Would delete {test_services.count()} test services')
                return
            
            # Reset all referrals for clean start
            referrals_count = Referral.objects.count()
            Referral.objects.all().delete()
            
            # Delete test services but preserve real ones
            test_services = Service.objects.filter(name__contains='Test')
            test_services_count = test_services.count()
            test_services.delete()
            
            self.stdout.write(f'  ✅ Reset all referrals (deleted {referrals_count})')
            self.stdout.write(f'  ✅ Reset test services (deleted {test_services_count})')
            self.stdout.write('  ✅ Preserved legitimate service definitions')
            
        except ImportError:
            self.stdout.write('  ⚠️  Referrals app not available, skipping...')

    def _reset_communications_data(self, options):
        """Reset communications and announcements data"""
        self.stdout.write('\n📢 Resetting Communications Data...')
        
        try:
            from apps.communications.models import ContactFormSubmission, EmailSubscription
            
            if options['dry_run']:
                submissions = ContactFormSubmission.objects.all()
                subscriptions = EmailSubscription.objects.filter(email__contains='test')
                self.stdout.write(f'  - Would delete {submissions.count()} contact submissions')
                self.stdout.write(f'  - Would delete {subscriptions.count()} test subscriptions')
                return
            
            # Reset contact form submissions
            submissions_count = ContactFormSubmission.objects.count()
            ContactFormSubmission.objects.all().delete()
            
            # Delete test email subscriptions
            test_subs = EmailSubscription.objects.filter(email__contains='test')
            test_subs_count = test_subs.count()
            test_subs.delete()
            
            self.stdout.write(f'  ✅ Reset contact submissions (deleted {submissions_count})')
            self.stdout.write(f'  ✅ Reset test subscriptions (deleted {test_subs_count})')
            
        except ImportError:
            self.stdout.write('  ⚠️  Communications app not available, skipping...')

    def _reset_services_data(self, options):
        """Reset services and ministry programs sample data"""
        self.stdout.write('\n🏛️ Resetting Services Data...')
        
        try:
            from apps.services.models import MinistryProgram, ServiceApplication
            
            if options['dry_run']:
                test_programs = MinistryProgram.objects.filter(name__contains='Test')
                applications = ServiceApplication.objects.all()
                self.stdout.write(f'  - Would delete {test_programs.count()} test programs')
                self.stdout.write(f'  - Would delete {applications.count()} applications')
                return
            
            # Delete test ministry programs
            test_programs = MinistryProgram.objects.filter(name__contains='Test')
            test_programs_count = test_programs.count()
            test_programs.delete()
            
            # Reset all service applications for clean start
            applications_count = ServiceApplication.objects.count()
            ServiceApplication.objects.all().delete()
            
            self.stdout.write(f'  ✅ Reset test programs (deleted {test_programs_count})')
            self.stdout.write(f'  ✅ Reset applications (deleted {applications_count})')
            self.stdout.write('  ✅ Preserved legitimate ministry programs')
            
        except ImportError:
            self.stdout.write('  ⚠️  Services app not available, skipping...')

    def _reset_notifications_data(self, options):
        """Reset notifications data"""
        self.stdout.write('\n🔔 Resetting Notifications Data...')
        
        try:
            from apps.notifications.models import Notification
            
            if options['dry_run']:
                notifications = Notification.objects.all()
                self.stdout.write(f'  - Would delete {notifications.count()} notifications')
                return
            
            # Reset all notifications for clean start
            notifications_count = Notification.objects.count()
            Notification.objects.all().delete()
            
            self.stdout.write(f'  ✅ Reset notifications (deleted {notifications_count})')
            
        except ImportError:
            self.stdout.write('  ⚠️  Notifications app not available, skipping...')

    def _reset_session_data(self, options):
        """Reset session data"""
        self.stdout.write('\n🔐 Resetting Session Data...')
        
        if options['dry_run']:
            sessions_count = Session.objects.count()
            self.stdout.write(f'  - Would delete {sessions_count} active sessions')
            return
        
        # Clear all active sessions
        sessions_count = Session.objects.count()
        Session.objects.all().delete()
        
        self.stdout.write(f'  ✅ Reset sessions (deleted {sessions_count})')

    def _reset_admin_logs(self, options):
        """Reset admin log entries"""
        self.stdout.write('\n📝 Resetting Admin Logs...')
        
        if options['dry_run']:
            logs_count = LogEntry.objects.count()
            self.stdout.write(f'  - Would delete {logs_count} admin log entries')
            return
        
        # Clear admin log entries
        logs_count = LogEntry.objects.count()
        LogEntry.objects.all().delete()
        
        self.stdout.write(f'  ✅ Reset admin logs (deleted {logs_count})')

    def _clear_cache(self, options):
        """Clear all cached data"""
        self.stdout.write('\n🗄️ Clearing Cache Data...')
        
        if options['dry_run']:
            self.stdout.write('  - Would clear all cached data')
            return
        
        # Clear Django cache
        cache.clear()
        
        self.stdout.write('  ✅ Cache cleared')

    def _update_statistics_cache(self):
        """Update statistics cache with zero values"""
        self.stdout.write('\n📊 Updating Statistics Cache...')
        
        # Set initial statistics to zero
        cache.set('stats_total_members', 0, 3600)
        cache.set('stats_active_chapters', 0, 3600) 
        cache.set('stats_referrals_processed', 0, 3600)
        cache.set('stats_community_programs', 0, 3600)
        cache.set('stats_last_updated', timezone.now(), 3600)
        
        self.stdout.write('  ✅ Statistics cache updated with zero values')

    def _log_reset_action(self):
        """Log the reset action for audit purposes"""
        logger.info(
            "Production statistics reset completed",
            extra={
                'action': 'production_stats_reset',
                'timestamp': timezone.now(),
                'user': 'system'
            }
        )