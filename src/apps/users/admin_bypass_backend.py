"""
Admin Bypass Authentication Backend for #FahanieCares.
This backend allows admin users to bypass normal authentication.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AdminBypassBackend(ModelBackend):
    """
    Custom authentication backend that bypasses authentication for admin accounts.
    This allows admin users to access the portal without going through normal auth.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate admin users with bypass mechanism.
        """
        if not username:
            return None
            
        try:
            # Check if user exists
            user = User.objects.get(username=username)
            
            # Define admin usernames that can bypass authentication
            admin_usernames = ['admin', 'saidamen.m']
            admin_passwords = {
                'admin': 'admin123',
                'saidamen.m': 'saidamen123'
            }
            
            # If it's an admin user with correct password, bypass normal auth
            if username in admin_usernames and password == admin_passwords.get(username):
                # Ensure user has proper admin privileges
                if not user.is_staff:
                    user.is_staff = True
                if not user.is_superuser:
                    user.is_superuser = True
                if not user.is_active:
                    user.is_active = True
                    
                # Update user type if needed
                if username == 'admin' and user.user_type != 'superuser':
                    user.user_type = 'superuser'
                elif username == 'saidamen.m' and user.user_type != 'admin':
                    user.user_type = 'admin'
                    
                user.save()
                
                logger.info(f"Admin bypass authentication successful for {username}")
                return user
            
            # For non-admin users, fall back to normal authentication
            elif user.check_password(password):
                return user
                
        except User.DoesNotExist:
            logger.warning(f"Authentication failed: User {username} does not exist")
            return None
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            return None
            
        return None
    
    def get_user(self, user_id):
        """
        Retrieve user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None