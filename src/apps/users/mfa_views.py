"""
Multi-Factor Authentication views for #FahanieCares.
"""

import qrcode
import io
import base64
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from .security import MFAService, SMSOTPService
from .models import User

@login_required
def mfa_setup(request):
    """
    Setup MFA for user accounts.
    """
    user = request.user
    
    # Only allow setup for users who require MFA
    if not user.is_staff_or_above():
        messages.error(request, "MFA is only required for staff accounts.")
        return redirect('home')
    
    if request.method == 'POST':
        token = request.POST.get('token')
        secret = request.session.get('mfa_secret')
        
        if not secret:
            messages.error(request, "MFA setup session expired. Please try again.")
            return redirect('mfa_setup')
        
        # Verify the token
        if MFAService.verify_token(secret, token):
            # Save MFA secret to user
            user.mfa_secret = secret
            user.mfa_enabled = True
            user.save()
            
            # Generate backup codes
            backup_codes = MFAService.generate_backup_codes()
            user.mfa_backup_codes = ','.join(backup_codes)
            user.save()
            
            # Clear session secret
            del request.session['mfa_secret']
            
            # Mark MFA as verified for this session
            request.session['mfa_verified'] = True
            
            messages.success(request, "MFA has been successfully enabled.")
            
            # Show backup codes
            return render(request, 'users/mfa_backup_codes.html', {
                'backup_codes': backup_codes
            })
        else:
            messages.error(request, "Invalid token. Please try again.")
    
    # Generate new secret if not in session
    if 'mfa_secret' not in request.session:
        request.session['mfa_secret'] = MFAService.generate_secret()
    
    secret = request.session['mfa_secret']
    qr_url = MFAService.generate_qr_url(user, secret)
    
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'qr_code': f"data:image/png;base64,{qr_code_base64}",
        'secret': secret,
        'setup_url': qr_url
    }
    
    return render(request, 'users/mfa_setup.html', context)

@login_required
def mfa_verify(request):
    """
    Verify MFA token for login.
    """
    user = request.user
    
    # Redirect if MFA is already verified for this session
    if request.session.get('mfa_verified'):
        return redirect('home')
    
    # Redirect if user doesn't have MFA enabled
    if not user.mfa_enabled:
        return redirect('mfa_setup')
    
    if request.method == 'POST':
        token = request.POST.get('token')
        
        # Check regular token
        if MFAService.verify_token(user.mfa_secret, token):
            request.session['mfa_verified'] = True
            messages.success(request, "MFA verification successful.")
            
            # Redirect to original destination or home
            next_url = request.session.get('mfa_next', reverse('home'))
            if 'mfa_next' in request.session:
                del request.session['mfa_next']
            
            return redirect(next_url)
        
        # Check backup codes
        elif user.mfa_backup_codes:
            backup_codes = user.mfa_backup_codes.split(',')
            if token in backup_codes:
                # Remove used backup code
                backup_codes.remove(token)
                user.mfa_backup_codes = ','.join(backup_codes)
                user.save()
                
                request.session['mfa_verified'] = True
                messages.success(request, "MFA verification successful using backup code.")
                messages.warning(request, f"You have {len(backup_codes)} backup codes remaining.")
                
                return redirect(request.session.get('mfa_next', reverse('home')))
        
        messages.error(request, "Invalid token. Please try again.")
    
    # Store the next URL for redirect after verification
    if 'next' in request.GET:
        request.session['mfa_next'] = request.GET['next']
    
    return render(request, 'users/mfa_verify.html')

@login_required
@require_POST
def mfa_disable(request):
    """
    Disable MFA for user account.
    """
    user = request.user
    
    # Verify current password
    password = request.POST.get('password')
    if not user.check_password(password):
        messages.error(request, "Invalid password.")
        return redirect('user_security_settings')
    
    # Disable MFA
    user.mfa_enabled = False
    user.mfa_secret = ''
    user.mfa_backup_codes = ''
    user.save()
    
    # Clear MFA session
    if 'mfa_verified' in request.session:
        del request.session['mfa_verified']
    
    messages.success(request, "MFA has been disabled.")
    return redirect('user_security_settings')

@login_required
def regenerate_backup_codes(request):
    """
    Regenerate MFA backup codes.
    """
    user = request.user
    
    if not user.mfa_enabled:
        messages.error(request, "MFA is not enabled.")
        return redirect('user_security_settings')
    
    if request.method == 'POST':
        # Verify current password or MFA token
        password = request.POST.get('password')
        token = request.POST.get('token')
        
        if password and user.check_password(password):
            # Generate new backup codes
            backup_codes = MFAService.generate_backup_codes()
            user.mfa_backup_codes = ','.join(backup_codes)
            user.save()
            
            return render(request, 'users/mfa_backup_codes.html', {
                'backup_codes': backup_codes,
                'regenerated': True
            })
        
        elif token and MFAService.verify_token(user.mfa_secret, token):
            # Generate new backup codes
            backup_codes = MFAService.generate_backup_codes()
            user.mfa_backup_codes = ','.join(backup_codes)
            user.save()
            
            return render(request, 'users/mfa_backup_codes.html', {
                'backup_codes': backup_codes,
                'regenerated': True
            })
        
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'users/mfa_regenerate_codes.html')

@login_required
def user_security_settings(request):
    """
    User security settings page.
    """
    user = request.user
    
    # Get login history
    login_history = []
    # This would typically fetch from a login history model
    
    # Get active sessions
    active_sessions = []
    # This would typically fetch from session storage
    
    context = {
        'user': user,
        'mfa_enabled': user.mfa_enabled,
        'login_history': login_history,
        'active_sessions': active_sessions,
        'backup_codes_count': len(user.mfa_backup_codes.split(',')) if user.mfa_backup_codes else 0
    }
    
    return render(request, 'users/security_settings.html', context)


@login_required
def mfa_method_choice(request):
    """
    Allow user to choose between TOTP and SMS for MFA.
    """
    user = request.user
    
    # Only allow setup for users who require MFA
    if not user.is_staff_or_above():
        messages.error(request, "MFA is only required for staff accounts.")
        return redirect('home')
    
    if request.method == 'POST':
        method = request.POST.get('method')
        
        if method in ['totp', 'sms']:
            # Update user's preferred method
            user.mfa_method = method
            user.save()
            
            if method == 'totp':
                return redirect('mfa_setup')
            else:  # SMS
                # Check if phone number exists
                if not user.phone_number:
                    messages.error(request, "Please add a phone number to your profile first.")
                    return redirect('profile_edit')
                
                return redirect('mfa_verify_phone')
        else:
            messages.error(request, "Please select a valid MFA method.")
    
    return render(request, 'users/mfa_method_choice.html')


@login_required
def mfa_verify_phone(request):
    """
    Verify phone number for SMS OTP setup.
    """
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send_otp':
            # Generate and send OTP
            otp = SMSOTPService.generate_otp()
            
            # Store OTP temporarily
            user.sms_otp_secret = otp
            user.sms_otp_expires = timezone.now() + timedelta(minutes=SMSOTPService.OTP_VALIDITY_MINUTES)
            user.save()
            
            # Send SMS
            if SMSOTPService.send_otp(user.phone_number, otp, user):
                messages.success(request, f"Verification code sent to {user.phone_number}")
            else:
                messages.error(request, "Failed to send SMS. Please check your phone number or try again later.")
            
            return render(request, 'users/mfa_verify_phone.html', {'otp_sent': True})
        
        elif action == 'verify_otp':
            provided_otp = request.POST.get('otp', '').strip()
            
            if SMSOTPService.verify_otp(user.sms_otp_secret, user.sms_otp_expires, provided_otp):
                # Mark phone as verified
                user.phone_verified = True
                user.mfa_enabled = True
                user.sms_otp_secret = ''  # Clear OTP
                user.save()
                
                # Generate backup codes
                backup_codes = MFAService.generate_backup_codes()
                user.mfa_backup_codes = ','.join(backup_codes)
                user.save()
                
                messages.success(request, "Phone number verified! SMS MFA has been enabled.")
                
                # Mark MFA as verified for this session
                request.session['mfa_verified'] = True
                
                # Show backup codes
                return render(request, 'users/mfa_backup_codes.html', {
                    'backup_codes': backup_codes,
                    'sms_enabled': True
                })
            else:
                messages.error(request, "Invalid or expired verification code.")
    
    return render(request, 'users/mfa_verify_phone.html', {
        'phone_number': user.phone_number,
        'otp_sent': False
    })


@login_required
def mfa_sms_verify(request):
    """
    Verify SMS OTP for login (similar to mfa_verify but for SMS).
    """
    user = request.user
    
    # Redirect if MFA is already verified for this session
    if request.session.get('mfa_verified'):
        return redirect('home')
    
    # Check if user has SMS MFA enabled
    if not user.mfa_enabled or user.mfa_method != 'sms':
        return redirect('mfa_verify')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send_otp':
            # Check rate limiting
            if not SMSOTPService.check_rate_limit(user):
                messages.error(request, "Too many OTP requests. Please wait before trying again.")
                return render(request, 'users/mfa_sms_verify.html', {'rate_limited': True})
            
            # Generate and send OTP
            otp = SMSOTPService.generate_otp()
            
            # Store OTP temporarily
            user.sms_otp_secret = otp
            user.sms_otp_expires = timezone.now() + timedelta(minutes=SMSOTPService.OTP_VALIDITY_MINUTES)
            user.save()
            
            # Send SMS
            if SMSOTPService.send_otp(user.phone_number, otp, user):
                messages.success(request, f"Verification code sent to {user.phone_number}")
            else:
                messages.error(request, "Failed to send SMS. Please try again later.")
            
            return render(request, 'users/mfa_sms_verify.html', {'otp_sent': True})
        
        elif action == 'verify_otp':
            provided_otp = request.POST.get('otp', '').strip()
            
            # First check OTP
            if SMSOTPService.verify_otp(user.sms_otp_secret, user.sms_otp_expires, provided_otp):
                # Clear OTP
                user.sms_otp_secret = ''
                user.save()
                
                # Mark MFA as verified
                request.session['mfa_verified'] = True
                messages.success(request, "MFA verification successful.")
                
                # Redirect to original destination or home
                next_url = request.session.get('mfa_next', reverse('home'))
                if 'mfa_next' in request.session:
                    del request.session['mfa_next']
                
                return redirect(next_url)
            
            # Check backup codes if OTP fails
            elif user.mfa_backup_codes:
                backup_codes = user.mfa_backup_codes.split(',')
                if provided_otp in backup_codes:
                    # Remove used backup code
                    backup_codes.remove(provided_otp)
                    user.mfa_backup_codes = ','.join(backup_codes)
                    user.save()
                    
                    request.session['mfa_verified'] = True
                    messages.success(request, "MFA verification successful using backup code.")
                    messages.warning(request, f"You have {len(backup_codes)} backup codes remaining.")
                    
                    return redirect(request.session.get('mfa_next', reverse('home')))
            
            messages.error(request, "Invalid verification code.")
    
    # Store the next URL for redirect after verification
    if 'next' in request.GET:
        request.session['mfa_next'] = request.GET['next']
    
    return render(request, 'users/mfa_sms_verify.html', {
        'phone_number': user.phone_number,
        'otp_sent': False
    })