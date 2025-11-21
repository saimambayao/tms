"""
Management command to reset all statistics and sample data for production launch.
This command will reset counters and remove sample data while preserving essential configuration.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reset all statistics and sample data for production launch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to reset all production statistics',
        )
        parser.add_argument(
            '--preserve-superusers',
            action='store_true',
            help='Preserve superuser accounts during reset',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will reset ALL statistics and sample data!\n'
                    'This action is IRREVERSIBLE and should only be run on production launch.\n\n'
                    'Run with --confirm to proceed.'
                )
            )
            return

        self.stdout.write(
            self.style.WARNING(
                'Starting production statistics reset...\n'
                'This will remove all sample data and reset counters to zero.'
            )
        )

        try:
            with transaction.atomic():
                self.reset_constituent_data()
                self.reset_referral_data()
                self.reset_chapter_data()
                self.reset_service_data()
                self.reset_communication_data()
                self.reset_staff_data(options['preserve_superusers'])
                self.reset_user_data(options['preserve_superusers'])
                self.update_home_page_stats()

            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ Production statistics reset completed successfully!\n'
                    'All sample data has been removed and counters reset to zero.\n'
                    'The platform is ready for production launch.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during reset: {str(e)}')
            )
            logger.error(f'Production reset failed: {str(e)}')

    def reset_constituent_data(self):
        """Reset constituent/registrant data"""
        from apps.constituents.models import Constituent
        
        # Count before deletion
        count = Constituent.objects.count()
        
        # Delete all constituents
        Constituent.objects.all().delete()
        
        self.stdout.write(f'🔄 Removed {count} constituent records')

    def reset_referral_data(self):
        """Reset referral and service request data"""
        from apps.referrals.models import Referral, ReferralUpdate, ReferralDocument
        
        # Count before deletion
        referral_count = Referral.objects.count()
        update_count = ReferralUpdate.objects.count()
        document_count = ReferralDocument.objects.count()
        
        # Delete all referral data
        ReferralDocument.objects.all().delete()
        ReferralUpdate.objects.all().delete()
        Referral.objects.all().delete()
        
        self.stdout.write(
            f'🔄 Removed {referral_count} referrals, '
            f'{update_count} updates, {document_count} documents'
        )

    def reset_chapter_data(self):
        """Reset chapter membership data but preserve chapter structure"""
        from apps.chapters.models import Chapter, ChapterMembership, ChapterActivity
        
        # Count before deletion
        membership_count = ChapterMembership.objects.count()
        activity_count = ChapterActivity.objects.count()
        
        # Delete membership and activity data but preserve chapters
        ChapterMembership.objects.all().delete()
        ChapterActivity.objects.all().delete()
        
        # Reset chapter member counts
        Chapter.objects.all().update(member_count=0)
        
        self.stdout.write(
            f'🔄 Removed {membership_count} memberships and {activity_count} activities'
        )

    def reset_service_data(self):
        """Reset service application data but preserve service definitions"""
        from apps.services.models import ServiceApplication, MinistryProgramHistory
        
        # Count before deletion
        application_count = ServiceApplication.objects.count() if hasattr(ServiceApplication.objects, 'count') else 0
        history_count = MinistryProgramHistory.objects.count()
        
        # Delete application history
        if hasattr(ServiceApplication.objects, 'all'):
            ServiceApplication.objects.all().delete()
        MinistryProgramHistory.objects.all().delete()
        
        self.stdout.write(
            f'🔄 Removed {application_count} service applications and {history_count} program histories'
        )

    def reset_communication_data(self):
        """Reset communication submissions but preserve templates"""
        from apps.communications.models import (
            ContactFormSubmission, 
            PartnershipSubmission, 
            DonationSubmission,
            EmailSubscription
        )
        
        # Count before deletion
        contact_count = ContactFormSubmission.objects.count()
        partnership_count = PartnershipSubmission.objects.count()
        donation_count = DonationSubmission.objects.count()
        subscription_count = EmailSubscription.objects.count()
        
        # Delete all submissions
        ContactFormSubmission.objects.all().delete()
        PartnershipSubmission.objects.all().delete()
        DonationSubmission.objects.all().delete()
        EmailSubscription.objects.all().delete()
        
        self.stdout.write(
            f'🔄 Removed {contact_count} contact forms, {partnership_count} partnerships, '
            f'{donation_count} donations, {subscription_count} subscriptions'
        )

    def reset_staff_data(self, preserve_superusers=False):
        """Reset staff data but preserve essential staff accounts"""
        from apps.staff.models import Staff, Task, WorkflowTask
        
        # Count before deletion
        staff_count = Staff.objects.count()
        task_count = Task.objects.count() if hasattr(Task.objects, 'count') else 0
        workflow_count = WorkflowTask.objects.count() if hasattr(WorkflowTask.objects, 'count') else 0
        
        # Delete task data
        if hasattr(Task.objects, 'all'):
            Task.objects.all().delete()
        if hasattr(WorkflowTask.objects, 'all'):
            WorkflowTask.objects.all().delete()
        
        # Reset staff performance metrics but preserve accounts
        Staff.objects.all().update(
            cases_handled=0,
            performance_rating=0.0
        )
        
        self.stdout.write(
            f'🔄 Reset {staff_count} staff records, removed {task_count} tasks, {workflow_count} workflows'
        )

    def reset_user_data(self, preserve_superusers=False):
        """Reset user data but preserve essential accounts"""
        User = get_user_model()
        
        if preserve_superusers:
            # Count non-superusers
            regular_users = User.objects.filter(is_superuser=False)
            count = regular_users.count()
            
            # Delete only regular users
            regular_users.delete()
            
            self.stdout.write(f'🔄 Removed {count} regular user accounts (preserved superusers)')
        else:
            # Count all users
            count = User.objects.count()
            
            # Delete all users
            User.objects.all().delete()
            
            self.stdout.write(f'🔄 Removed {count} user accounts')

    def update_home_page_stats(self):
        """Update the hardcoded stats in the home page view to start from zero"""
        self.stdout.write(
            '📝 Note: Update the hardcoded stats in apps/core/views.py HomePageView\n'
            '   Set impact_stats values to realistic starting numbers for production:\n'
            '   - constituents_served: 0\n'
            '   - active_chapters: [actual chapter count]\n'
            '   - referrals_processed: 0\n'
            '   - community_programs: [actual program count]'
        )

    def get_reset_summary(self):
        """Provide a summary of what will be reset"""
        return """
        🚨 PRODUCTION RESET SUMMARY 🚨
        
        This command will permanently delete:
        ✅ All constituent/registrant records
        ✅ All referral requests and updates  
        ✅ All chapter memberships and activities
        ✅ All service applications
        ✅ All contact form submissions
        ✅ All partnership and donation requests
        ✅ All email subscriptions
        ✅ All staff tasks and workflows
        ✅ All regular user accounts (optional)
        
        This command will preserve:
        ⭐ Chapter structure and definitions
        ⭐ Service and program definitions
        ⭐ System configuration
        ⭐ Superuser accounts (if --preserve-superusers used)
        ⭐ Staff accounts (but reset performance metrics)
        
        Result: Clean production environment with zero statistics
        """