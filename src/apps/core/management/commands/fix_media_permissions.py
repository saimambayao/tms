import os
import stat
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Fix media directory permissions for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation of directories even if they exist',
        )

    def handle(self, *args, **options):
        """Fix media directory permissions"""
        
        # Media directories to create
        directories = [
            'announcements',
            'documents',
            'constituents', 
            'constituents/voter_id_photos',  # Nested directory for voter IDs
            'services',
            'chapters',
            'voter_id_photos',  # Top-level voter ID directory
            'temp',  # Temporary upload directory
        ]
        
        self.stdout.write(f"Media root: {settings.MEDIA_ROOT}")
        
        for directory in directories:
            dir_path = os.path.join(settings.MEDIA_ROOT, directory)
            
            try:
                # Create directory if it doesn't exist
                if not os.path.exists(dir_path) or options['force']:
                    os.makedirs(dir_path, mode=0o755, exist_ok=True)
                    self.stdout.write(
                        self.style.SUCCESS(f'Created directory: {dir_path}')
                    )
                else:
                    self.stdout.write(f'Directory exists: {dir_path}')
                
                # Check and fix permissions
                try:
                    current_mode = oct(stat.S_IMODE(os.lstat(dir_path).st_mode))
                    self.stdout.write(f'Current permissions for {dir_path}: {current_mode}')
                    
                    # Try to set permissions
                    os.chmod(dir_path, 0o755)
                    self.stdout.write(
                        self.style.SUCCESS(f'Fixed permissions for: {dir_path}')
                    )
                except PermissionError:
                    self.stdout.write(
                        self.style.WARNING(f'Cannot change permissions for: {dir_path}')
                    )
                    
            except PermissionError as e:
                self.stdout.write(
                    self.style.ERROR(f'Permission denied for {dir_path}: {e}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error with {dir_path}: {e}')
                )
        
        # Check overall media root permissions
        try:
            media_stat = os.stat(settings.MEDIA_ROOT)
            self.stdout.write(f'Media root owner: {media_stat.st_uid}:{media_stat.st_gid}')
            self.stdout.write(f'Media root permissions: {oct(stat.S_IMODE(media_stat.st_mode))}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking media root: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Media permissions check completed')
        )