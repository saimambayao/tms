from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from .forms import UserRegistrationForm
from .models import User, RoleTransitionLog, DynamicPermission, UserPermissionOverride
from .decorators import require_role, require_role_or_higher, RoleRequiredMixin
from .permissions import assign_user_to_role_group
from apps.constituents.member_forms import FahanieCaresMemberRegistrationForm
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    """
    Custom login view for #FahanieCares.
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        # Add custom login logic here if needed
        return super().form_valid(form)

class UserRegistrationView(CreateView):
    """
    User registration view for #FahanieCares.
    Creates a new user and also adds them to the Notion members database.
    """
    template_name = 'constituents/member_registration.html'
    form_class = FahanieCaresMemberRegistrationForm
    success_url = reverse_lazy('registration_success')
    
    def form_valid(self, form):
        # The form's save method handles both User and FahanieCaresMember creation
        response = super().form_valid(form)
        
        # Show success message
        messages.success(
            self.request, 
            'Your #FahanieCares membership application has been submitted successfully! '
            'You will receive an email once your application is approved.'
        )
        
        return response

class RegistrationSuccessView(TemplateView):
    """
    Success page after registration.
    """
    template_name = 'constituents/registration_success.html'
    

class MemberRegistrationView(LoginRequiredMixin, CreateView):
    """
    View for upgrading a constituent to a member.
    Only accessible to authenticated users who are not already members.
    """
    template_name = 'users/member_registration.html'
    form_class = UserRegistrationForm  # We'll reuse the same form
    success_url = reverse_lazy('home')
    login_url = '/accounts/login/'
    
    def get_initial(self):
        # Pre-fill the form with the user's existing data
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            user = self.request.user
            initial.update({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'address': user.address,
                'municipality': user.municipality,
            })
        return initial
    
    def form_valid(self, form):
        # Update the existing user instead of creating a new one
        user = self.request.user
        user.user_type = 'member'  # Upgrade to member
        
        # Update other fields from the form
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.phone_number = form.cleaned_data['phone_number']
        user.address = form.cleaned_data['address']
        user.municipality = form.cleaned_data['municipality']
        user.save()
        
        # Add the user to Notion database (when set up)
        try:
            notion_service = NotionService()
            
            # Only try to create or update Notion record if API key is configured
            if settings.NOTION_API_KEY and settings.NOTION_MEMBER_DATABASE:
                # If user already has a Notion ID, update the record
                if user.notion_id:
                    member_properties = {
                        'Name': format_title(f"{user.first_name} {user.last_name}"),
                        'Email': format_email(user.email),
                        'Phone': format_phone_number(user.phone_number),
                        'Address': format_rich_text(user.address),
                        'Municipality': format_rich_text(user.municipality),
                        'User Type': format_select(user.user_type),
                    }
                    notion_service.update_page(user.notion_id, member_properties)
                else:
                    # Create a record in the Members database
                    member_properties = {
                        'Name': format_title(f"{user.first_name} {user.last_name}"),
                        'Email': format_email(user.email),
                        'Phone': format_phone_number(user.phone_number),
                        'Address': format_rich_text(user.address),
                        'Municipality': format_rich_text(user.municipality),
                        'User Type': format_select(user.user_type),
                        'Is Approved': format_checkbox(user.is_approved),
                        'User ID': format_rich_text(str(user.id)),
                    }
                    
                    notion_page = notion_service.create_page(
                        database_id=settings.NOTION_MEMBER_DATABASE,
                        properties=member_properties
                    )
                    
                    # Save the Notion ID back to the user
                    user.notion_id = notion_page['id']
                    user.save(update_fields=['notion_id'])
        except Exception as e:
            # Log the error but don't prevent user upgrade
            print(f"Error updating Notion record: {str(e)}")
        
        # Show success message
        messages.success(self.request, "Congratulations! You are now a registered #FahanieCares member.")
        
        return redirect(self.success_url)


# RBAC Management Views

@method_decorator(require_role_or_higher('chief_of_staff'), name='dispatch')
class UserManagementListView(ListView):
    """List view for user management - Chief of Staff and above."""
    model = User
    template_name = 'users/management/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        """Get filtered queryset based on search and filters."""
        queryset = User.objects.all().order_by('-date_joined')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filter by role
        role_filter = self.request.GET.get('role')
        if role_filter:
            queryset = queryset.filter(user_type=role_filter)
        
        # Filter by approval status
        approval_filter = self.request.GET.get('approved')
        if approval_filter == 'true':
            queryset = queryset.filter(is_approved=True)
        elif approval_filter == 'false':
            queryset = queryset.filter(is_approved=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context."""
        context = super().get_context_data(**kwargs)
        context['role_choices'] = User.USER_TYPES
        context['search'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['approval_filter'] = self.request.GET.get('approved', '')
        return context


@method_decorator(require_role_or_higher('chief_of_staff'), name='dispatch')
class UserDetailView(DetailView):
    """Detail view for a specific user - Chief of Staff and above."""
    model = User
    template_name = 'users/management/user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        """Add role transition history and permissions."""
        context = super().get_context_data(**kwargs)
        
        # Get role transition history
        context['role_history'] = RoleTransitionLog.objects.filter(
            user=self.object
        ).order_by('-changed_at')[:10]
        
        # Get user permissions
        context['user_permissions'] = self.object.get_all_permissions()
        
        # Get permission overrides
        context['permission_overrides'] = UserPermissionOverride.objects.filter(
            user=self.object
        ).select_related('permission', 'created_by')
        
        return context


@method_decorator(require_role('chief_of_staff'), name='dispatch')
class UserRoleUpdateView(UpdateView):
    """Update user role - Chief of Staff only."""
    model = User
    template_name = 'users/management/user_role_update.html'
    fields = ['user_type', 'is_approved', 'chapter_id']
    context_object_name = 'user_obj'
    
    def form_valid(self, form):
        """Handle role update."""
        user = form.instance
        old_role = User.objects.get(pk=user.pk).user_type
        
        # Check if role is changing
        if old_role != user.user_type:
            # Log the role transition
            RoleTransitionLog.objects.create(
                user=user,
                from_role=old_role,
                to_role=user.user_type,
                reason=self.request.POST.get('reason', 'Role update via web interface'),
                changed_by=self.request.user,
                ip_address=self.request.META.get('REMOTE_ADDR')
            )
            
            # Update role assignment metadata
            user.role_assigned_by = self.request.user
            user.role_assigned_at = timezone.now()
            
            # Save the user
            response = super().form_valid(form)
            
            # Reassign to appropriate group
            assign_user_to_role_group(user)
            
            messages.success(
                self.request, 
                f'Successfully updated {user.get_full_name()}\'s role to {user.get_user_type_display()}'
            )
            
            return response
        
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to user detail after update."""
        return f'/users/management/{self.object.pk}/'


@require_role_or_higher('admin')
@login_required
def user_approval_view(request, pk):
    """Quick approve/reject user - Admin and above."""
    user = get_object_or_404(User, pk=pk)
    action = request.POST.get('action')
    
    if action == 'approve':
        user.is_approved = True
        user.save()
        
        # Assign to group
        assign_user_to_role_group(user)
        
        messages.success(request, f'{user.get_full_name()} has been approved.')
        
    elif action == 'reject':
        user.is_approved = False
        user.save()
        messages.warning(request, f'{user.get_full_name()} has been rejected.')
    
    return redirect('users:user-management-list')


@require_role_or_higher('coordinator')
@login_required
def role_statistics_view(request):
    """View role distribution statistics."""
    # Get role distribution
    role_stats = {}
    for role_code, role_name in User.USER_TYPES:
        count = User.objects.filter(user_type=role_code).count()
        role_stats[role_name] = count
    
    # Get recent role changes
    recent_changes = RoleTransitionLog.objects.select_related(
        'user', 'changed_by'
    ).order_by('-changed_at')[:20]
    
    # Get approval pending count
    pending_count = User.objects.filter(is_approved=False).count()
    
    context = {
        'role_stats': role_stats,
        'recent_changes': recent_changes,
        'pending_count': pending_count,
        'total_users': User.objects.count(),
    }
    
    return render(request, 'users/management/role_statistics.html', context)