#!/usr/bin/env python3
"""
Database backup script for #FahanieCares production database.
Backs up PostgreSQL database to AWS S3 with encryption and retention policies.
"""

import os
import sys
import subprocess
import datetime
import logging
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.s3_bucket = os.environ.get('AWS_S3_BACKUP_BUCKET', 'fahaniecares-backups')
        self.s3_prefix = os.environ.get('AWS_S3_BACKUP_PREFIX', 'database-backups/')
        self.retention_days = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Parse database URL
        parsed = urlparse(self.database_url)
        self.db_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],
            'username': parsed.username,
            'password': parsed.password,
        }
        
        # Initialize S3 client
        self.s3_client = boto3.client('s3')
    
    def create_backup(self):
        """Create a PostgreSQL backup using pg_dump."""
        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"fahaniecares_backup_{timestamp}.sql.gz"
        
        logger.info(f"Starting database backup: {backup_filename}")
        
        # Set PostgreSQL password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_params['password']
        
        # Create pg_dump command
        dump_cmd = [
            'pg_dump',
            '-h', self.db_params['host'],
            '-p', str(self.db_params['port']),
            '-U', self.db_params['username'],
            '-d', self.db_params['database'],
            '--no-owner',
            '--no-privileges',
            '--clean',
            '--if-exists',
            '--verbose'
        ]
        
        # Compress with gzip
        gzip_cmd = ['gzip', '-9']
        
        try:
            # Execute pg_dump and pipe to gzip
            dump_process = subprocess.Popen(
                dump_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            with open(backup_filename, 'wb') as backup_file:
                gzip_process = subprocess.Popen(
                    gzip_cmd,
                    stdin=dump_process.stdout,
                    stdout=backup_file,
                    stderr=subprocess.PIPE
                )
                
                # Close dump_process stdout to signal we're done reading
                dump_process.stdout.close()
                
                # Wait for both processes to complete
                dump_stderr = dump_process.stderr.read()
                gzip_stderr = gzip_process.stderr.read()
                
                dump_returncode = dump_process.wait()
                gzip_returncode = gzip_process.wait()
                
                if dump_returncode != 0:
                    logger.error(f"pg_dump failed: {dump_stderr.decode()}")
                    raise Exception("Database dump failed")
                
                if gzip_returncode != 0:
                    logger.error(f"gzip failed: {gzip_stderr.decode()}")
                    raise Exception("Compression failed")
            
            logger.info(f"Backup created successfully: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            # Clean up partial backup file
            if os.path.exists(backup_filename):
                os.remove(backup_filename)
            raise
    
    def upload_to_s3(self, backup_filename):
        """Upload backup file to S3 with encryption."""
        s3_key = f"{self.s3_prefix}{backup_filename}"
        
        logger.info(f"Uploading backup to S3: s3://{self.s3_bucket}/{s3_key}")
        
        try:
            # Upload with server-side encryption
            self.s3_client.upload_file(
                backup_filename,
                self.s3_bucket,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD_IA',  # Infrequent Access for cost savings
                    'Metadata': {
                        'backup-date': datetime.datetime.utcnow().isoformat(),
                        'database': self.db_params['database'],
                        'retention-days': str(self.retention_days)
                    }
                }
            )
            
            logger.info("Upload completed successfully")
            
            # Verify upload
            response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
            file_size = response['ContentLength']
            logger.info(f"Verified upload: {file_size} bytes")
            
            return s3_key
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period."""
        logger.info(f"Cleaning up backups older than {self.retention_days} days")
        
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=self.retention_days)
        
        try:
            # List all backup objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.s3_bucket, Prefix=self.s3_prefix)
            
            deleted_count = 0
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    # Check if object is older than retention period
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        logger.info(f"Deleting old backup: {obj['Key']}")
                        self.s3_client.delete_object(Bucket=self.s3_bucket, Key=obj['Key'])
                        deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} old backups")
            
        except ClientError as e:
            logger.error(f"Cleanup failed: {str(e)}")
            # Don't raise - cleanup failure shouldn't fail the entire backup
    
    def verify_backup(self, s3_key):
        """Verify backup integrity by checking metadata and size."""
        try:
            response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
            
            # Check file size (should be at least 1KB)
            if response['ContentLength'] < 1024:
                raise Exception("Backup file too small, possible corruption")
            
            # Check encryption
            if 'ServerSideEncryption' not in response:
                logger.warning("Backup is not encrypted!")
            
            logger.info(f"Backup verification passed: {response['ContentLength']} bytes")
            return True
            
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            raise
    
    def run(self):
        """Execute the complete backup process."""
        backup_filename = None
        
        try:
            # Create backup
            backup_filename = self.create_backup()
            
            # Upload to S3
            s3_key = self.upload_to_s3(backup_filename)
            
            # Verify backup
            self.verify_backup(s3_key)
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            logger.info("Backup process completed successfully")
            
            # Send success notification (implement as needed)
            self.send_notification(
                "success",
                f"Database backup completed: {s3_key}"
            )
            
        except Exception as e:
            logger.error(f"Backup process failed: {str(e)}")
            
            # Send failure notification
            self.send_notification(
                "failure",
                f"Database backup failed: {str(e)}"
            )
            
            sys.exit(1)
            
        finally:
            # Clean up local backup file
            if backup_filename and os.path.exists(backup_filename):
                os.remove(backup_filename)
                logger.info(f"Cleaned up local file: {backup_filename}")
    
    def send_notification(self, status, message):
        """Send backup status notification."""
        # This could send to Slack, email, or other notification service
        # For now, just log it
        logger.info(f"Notification [{status}]: {message}")
        
        # Example Slack notification (requires webhook URL)
        slack_webhook = os.environ.get('SLACK_WEBHOOK')
        if slack_webhook:
            import requests
            
            color = "good" if status == "success" else "danger"
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": "Database Backup Status",
                    "text": message,
                    "footer": "#FahanieCares Backup System",
                    "ts": int(datetime.datetime.utcnow().timestamp())
                }]
            }
            
            try:
                requests.post(slack_webhook, json=payload)
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {str(e)}")


if __name__ == "__main__":
    backup = DatabaseBackup()
    backup.run()