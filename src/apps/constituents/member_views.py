from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from .member_models import FahanieCaresMember
from .member_forms import FahanieCaresMemberRegistrationForm, FahanieCaresMemberUpdateForm
from .models import Constituent # Import Constituent model
from .utils import MUNICIPALITY_CHOICES_DATA # Import the centralized data


class FahanieCaresMemberRegistrationView(CreateView):
    """
    View for new #FahanieCares member registration
    """
    form_class = FahanieCaresMemberRegistrationForm
    template_name = 'constituents/member_registration.html'
    success_url = reverse_lazy('registration_success')
    
    def get_form(self, form_class=None):
        """Override to ensure proper form initialization with POST data"""
        form = super().get_form(form_class)
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        
        if self.request.method == 'POST':
            logger.info(f"POST data keys: {list(self.request.POST.keys())}")
            logger.info(f"Radio values - sex: {self.request.POST.get('sex')}, sector: {self.request.POST.get('sector')}, highest_education: {self.request.POST.get('highest_education')}, eligibility: {self.request.POST.get('eligibility')}")
        
        return form
    
    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Log form data for debugging
            logger.info(f"Form validation successful. User: {form.cleaned_data.get('username')}")
            
            # Check if file was uploaded
            if 'voter_id_photo' in self.request.FILES:
                uploaded_file = self.request.FILES['voter_id_photo']
                logger.info(f"File uploaded: {uploaded_file.name}, Size: {uploaded_file.size} bytes")
            else:
                logger.info("No voter ID photo uploaded")
            
            response = super().form_valid(form)
            
            # After FahanieCaresMember is saved, create a Constituent profile
            # The user object is created implicitly by FahanieCaresMemberRegistrationForm
            # and linked to the FahanieCaresMember instance.
            # We can access the user via form.instance.user
            try:
                if not hasattr(form.instance.user, 'constituent'):
                    Constituent.objects.create(user=form.instance.user)
                    logger.info(f"Constituent profile created for user: {form.instance.user.username}")
                else:
                    logger.info(f"Constituent profile already exists for user: {form.instance.user.username}")
            except Exception as e:
                logger.error(f"Error creating Constituent profile for user {form.instance.user.username}: {e}", exc_info=True)
                messages.error(self.request, 'An error occurred while creating your constituent profile. Please contact support.')
                return self.form_invalid(form)

            messages.success(
                self.request, 
                'Your #FahanieCares membership application has been submitted successfully! '
                'You will receive an email once your application is approved.'
            )
            return response
            
        except Exception as e:
            logger.error(f"Error during form submission: {str(e)}", exc_info=True)
            messages.error(
                self.request,
                'An error occurred while processing your registration. Please try again.'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors while preserving form data"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Log validation errors for debugging
        logger.warning(f"Form validation failed. Errors: {form.errors}")
        
        # Debug: Log the raw POST data to see what was actually submitted
        logger.info(f"POST data received: {dict(self.request.POST)}")
        
        # Debug: Check specifically for radio button fields
        logger.info(f"Radio button values - Sex: {self.request.POST.get('sex')}, Sector: {self.request.POST.get('sector')}, Education: {self.request.POST.get('highest_education')}, Eligibility: {self.request.POST.get('eligibility')}")
        
        # Ensure form is properly bound with POST data
        # This should already be done by Django, but let's make sure radio buttons are preserved
        if hasattr(form, 'data'):
            # The form should already have the POST data bound
            logger.info(f"Form is bound: {form.is_bound}")
            logger.info(f"Form data preserved: sex={form.data.get('sex')}, sector={form.data.get('sector')}")
        
        # Add helpful message for users
        messages.error(
            self.request,
            'Please correct the errors below and try again. Your selections have been preserved.'
        )
        
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '#FahanieCares Member Registration'
        return context


class RegistrationSuccessView(DetailView):
    """
    Success page after registration
    """
    template_name = 'constituents/registration_success.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'title': 'Registration Successful'
        })


@method_decorator(login_required, name='dispatch')
class MemberProfileView(DetailView):
    """
    View for members to see their own profile
    """
    model = FahanieCaresMember
    template_name = 'constituents/member_profile.html'
    context_object_name = 'member'
    
    def get_object(self, queryset=None):
        try:
            return FahanieCaresMember.objects.get(user=self.request.user)
        except FahanieCaresMember.DoesNotExist:
            return None
    
    def get_context_data(self, **kwargs):
        # Override to handle None object
        context = {
            'member': self.get_object(),
            'title': 'My #FahanieCares Profile',
            'view': self
        }
        return context


@method_decorator(login_required, name='dispatch')
class MemberUpdateView(UpdateView):
    """
    View for members to update their profile
    """
    model = FahanieCaresMember
    form_class = FahanieCaresMemberUpdateForm
    template_name = 'constituents/member_update.html'
    success_url = reverse_lazy('member_profile')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has a member profile, redirect to registration if not
        try:
            FahanieCaresMember.objects.get(user=request.user)
        except FahanieCaresMember.DoesNotExist:
            messages.info(
                request, 
                'You need to complete your member registration first.'
            )
            return redirect('member_register')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        return FahanieCaresMember.objects.get(user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update My Profile'
        return context


@method_decorator(login_required, name='dispatch')
class MemberListView(ListView):
    """
    Staff view to see all members
    """
    model = FahanieCaresMember
    template_name = 'constituents/staff/member_list.html'
    context_object_name = 'members'
    paginate_by = 50
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff_or_above():
            messages.error(request, 'You do not have permission to view this page.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(middle_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(contact_number__icontains=search_query)
            )
        
        # Filter by sector
        sector = self.request.GET.get('sector')
        if sector:
            queryset = queryset.filter(sector=sector)
        
        # Filter by approval status
        approval = self.request.GET.get('approved')
        if approval == 'yes':
            queryset = queryset.filter(is_approved=True)
        elif approval == 'no':
            queryset = queryset.filter(is_approved=False)
        
        # Filter by municipality
        municipality = self.request.GET.get('municipality')
        if municipality:
            queryset = queryset.filter(address_municipality__icontains=municipality)
        
        return queryset.select_related('user', 'approved_by').order_by('-date_of_application')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '#FahanieCares Members'
        context['sector_choices'] = FahanieCaresMember.SECTOR_CHOICES
        context['total_members'] = FahanieCaresMember.objects.count()
        context['approved_members'] = FahanieCaresMember.objects.filter(is_approved=True).count()
        context['pending_members'] = FahanieCaresMember.objects.filter(is_approved=False).count()
        return context


class MemberDetailView(DetailView):
    """
    Staff view for viewing member details
    """
    model = FahanieCaresMember
    template_name = 'constituents/member_profile.html'
    context_object_name = 'member'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.first_name} {self.object.last_name} - Member Profile'
        return context


class MemberCreateView(CreateView):
    """
    Staff view for creating new members
    """
    model = FahanieCaresMember
    form_class = FahanieCaresMemberRegistrationForm
    template_name = 'constituents/member_registration.html'
    success_url = reverse_lazy('staff_member_list')
    
    def form_valid(self, form):
        # Staff can approve members immediately
        form.instance.is_approved = True
        form.instance.approved_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Member {self.object.first_name} {self.object.last_name} has been created successfully!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Member'
        context['is_staff_create'] = True
        return context


class GetMunicipalitiesView(View):
    """
    View to return municipalities based on selected province
    """
    def get(self, request):
        province = request.GET.get('province', '')
        
        municipalities = MUNICIPALITY_CHOICES_DATA.get(province, [])
        
        return JsonResponse({
            'municipalities': municipalities
        })
