"""
Management command to invalidate CloudFront CDN cache
Usage: python manage.py invalidate_cdn_cache
"""

import os
import boto3
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone


class Command(BaseCommand):
    help = 'Invalidate CloudFront CDN cache for static files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--paths',
            nargs='+',
            default=['/*'],
            help='Paths to invalidate (default: /*)'
        )
        parser.add_argument(
            '--distribution-id',
            type=str,
            help='CloudFront distribution ID (overrides environment variable)'
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for invalidation to complete'
        )

    def handle(self, *args, **options):
        # Get distribution ID
        distribution_id = (
            options.get('distribution_id') or 
            os.getenv('CLOUDFRONT_DISTRIBUTION_ID') or
            getattr(settings, 'CLOUDFRONT_DISTRIBUTION_ID', None)
        )

        if not distribution_id:
            self.stdout.write(
                self.style.ERROR(
                    'No CloudFront distribution ID found. '
                    'Set CLOUDFRONT_DISTRIBUTION_ID environment variable or use --distribution-id'
                )
            )
            return

        # Initialize CloudFront client
        try:
            cloudfront = boto3.client(
                'cloudfront',
                region_name=os.getenv('AWS_REGION', 'ap-southeast-1')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize AWS client: {e}')
            )
            return

        # Create invalidation
        paths = options['paths']
        caller_reference = f"django-{timezone.now().timestamp()}"

        self.stdout.write(f"Creating invalidation for paths: {', '.join(paths)}")

        try:
            response = cloudfront.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': caller_reference
                }
            )

            invalidation_id = response['Invalidation']['Id']
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Invalidation created successfully!\n"
                    f"   Distribution: {distribution_id}\n"
                    f"   Invalidation ID: {invalidation_id}\n"
                    f"   Status: {response['Invalidation']['Status']}"
                )
            )

            # Wait for completion if requested
            if options['wait']:
                self.stdout.write("⏳ Waiting for invalidation to complete...")
                waiter = cloudfront.get_waiter('invalidation_completed')
                
                try:
                    waiter.wait(
                        DistributionId=distribution_id,
                        Id=invalidation_id,
                        WaiterConfig={
                            'Delay': 20,
                            'MaxAttempts': 30  # Wait up to 10 minutes
                        }
                    )
                    self.stdout.write(
                        self.style.SUCCESS("✅ Invalidation completed!")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Timeout waiting for invalidation: {e}"
                        )
                    )

            # Check current invalidations
            self._check_invalidation_quota(cloudfront, distribution_id)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to create invalidation: {e}")
            )

    def _check_invalidation_quota(self, cloudfront, distribution_id):
        """Check and display current invalidation quota usage"""
        try:
            # List current invalidations
            response = cloudfront.list_invalidations(
                DistributionId=distribution_id,
                MaxItems='10'
            )

            in_progress = sum(
                1 for inv in response.get('InvalidationList', {}).get('Items', [])
                if inv['Status'] == 'InProgress'
            )

            self.stdout.write(
                f"\n📊 Invalidation Status:\n"
                f"   In Progress: {in_progress}\n"
                f"   Monthly Limit: 3000 (AWS provides 1000 free per month)"
            )

        except Exception:
            pass  # Ignore quota check errors