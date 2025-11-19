from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect
from .models import ServiceProgram, ServiceApplication, ServiceDisbursement, ServiceImpact, MinistryProgram, ApplicationAttachment
from .forms import ServiceApplicationForm, ServiceAssessmentForm, ServiceDisbursementForm, ApplicationForm
from utils.notifications import send_notification
from django.conf import settings
import os

from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from apps.constituents.member_models import BMParliamentMember # Import BMParliamentMember
from apps.services.models import MinistryProgram # Import MinistryProgram

class ServiceProgramListView(ListView):
    """
    Public view of all active service programs.
    """
    model = ServiceProgram
    template_name = 'services/public_program_list.html' # Changed template name
    context_object_name = 'programs'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = ServiceProgram.objects.filter(
            status='active',
            published_at__isnull=False
        )
        
        # Filter by type if provided
        program_type = self.request.GET.get('type')
        if program_type:
            queryset = queryset.filter(program_type=program_type)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(target_beneficiaries__icontains=search)
            )
        
        # Only show programs accepting applications
        if self.request.GET.get('accepting_only'):
            active_programs = []
            for program in queryset:
                if program.is_accepting_applications():
                    active_programs.append(program.id)
            queryset = queryset.filter(id__in=active_programs)
        
        return queryset.order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program_types'] = ServiceProgram.PROGRAM_TYPES
        return context


class ServiceProgramDetailView(DetailView):
    """
    Public detail view of a service program.
    """
    model = ServiceProgram
    template_name = 'services/program_detail.html'
    context_object_name = 'program'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.get_object()
        
        # Check availability
        context['availability'] = program.is_accepting_applications() # Assuming this method exists on ServiceProgram
        
        # Check if user has existing application
        if self.request.user.is_authenticated:
            try:
                constituent = self.request.user.bm_parliament_member
                context['existing_application'] = ServiceApplication.objects.filter(
                    service_program=program, # Changed from 'program' to 'service_program'
                    constituent=constituent
                ).first()
            except BMParliamentMember.DoesNotExist:
                context['existing_application'] = None # User is logged in but has no constituent profile
        
        # Get program statistics
        context['stats'] = {
            'total_applications': program.applications.count(),
            'approved_applications': program.applications.filter(status='approved').count(),
            'budget_utilization': (program.budget_utilized / program.total_budget * 100) if program.total_budget > 0 else 0,
            'capacity_utilization': (program.beneficiary_count / program.max_beneficiaries * 100) if program.max_beneficiaries > 0 else 0,
        }
        
        return context


class MinistryProgramDetailView(DetailView):
    """
    Public detail view of a Ministry Program.
    """
    model = MinistryProgram
    template_name = 'core/ministry_program_detail_new.html'
    context_object_name = 'program'

    def get_queryset(self):
        # Ensure only public and non-deleted programs are accessible via this view
        # Exclude TDIF projects as they have their own dedicated page
        return MinistryProgram.objects.filter(
            is_public=True, 
            is_deleted=False
        ).exclude(
            program_source__in=['tdif_infra', 'tdif_non_infra']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.get_object()

        # Add any specific context needed for MinistryProgram detail page
        # For example, related history, impact, etc.
        # For now, just basic program details are sufficient.
        return context


class ApplicationFormView(View):
    template_name = 'services/application_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to apply for a program.")
            return redirect(settings.LOGIN_URL)
        
        # Ensure the user has a BMParliamentMember profile
        if not hasattr(request.user, 'bm_parliament_member'):
            messages.warning(request, "Please complete your member registration before applying for a program.")
            return redirect('member_registration') # Redirect to your member registration page

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        service_programs = ServiceProgram.objects.filter(status='active').values('id', 'name')
        ministry_programs = MinistryProgram.objects.filter(status='active', is_public=True, is_deleted=False).values('id', 'title')
        
        # Combine and format programs for the dropdown
        programs_for_dropdown = []
        for p in service_programs:
            programs_for_dropdown.append({'id': f"service_{p['id']}", 'name': p['name']})
        for p in ministry_programs:
            programs_for_dropdown.append({'id': f"ministry_{p['id']}", 'name': p['title']})

        print(f"Programs for dropdown (GET): {programs_for_dropdown}") # Debug print
        form = ApplicationForm(programs=programs_for_dropdown) # Pass programs to form
        return render(request, self.template_name, {'form': form, 'programs': programs_for_dropdown})

    def post(self, request, *args, **kwargs):
        # Pass programs to the form in the POST request as well
        service_programs = ServiceProgram.objects.filter(status='active').values('id', 'name')
        ministry_programs = MinistryProgram.objects.filter(status='active', is_public=True, is_deleted=False).values('id', 'title')
        
        programs_for_dropdown = []
        for p in service_programs:
            programs_for_dropdown.append({'id': f"service_{p['id']}", 'name': p['name']})
        for p in ministry_programs:
            programs_for_dropdown.append({'id': f"ministry_{p['id']}", 'name': p['title']})

        print(f"Programs for dropdown (POST): {programs_for_dropdown}") # Debug print
        form = ApplicationForm(request.POST, request.FILES, programs=programs_for_dropdown) # Pass programs to form

        if form.is_valid():
            program_id_str = form.cleaned_data['program_of_interest']
            program_type, program_pk = program_id_str.split('_')

            if program_type == 'service':
                program_instance = get_object_or_404(ServiceProgram, pk=program_pk)
            elif program_type == 'ministry':
                program_instance = get_object_or_404(MinistryProgram, pk=program_pk)
            else:
                messages.error(request, 'Invalid program selected.')
                return render(request, self.template_name, {'form': form, 'programs': programs_for_dropdown})

            # Create a new ServiceApplication instance
            application = ServiceApplication(
                constituent=request.user.bm_parliament_member,
                reason_for_application=form.cleaned_data['message'],
            )
            if program_type == 'service':
                application.service_program = program_instance
            elif program_type == 'ministry':
                application.ministry_program = program_instance
            application.full_clean() # Validate that only one program is set
            application.save()

            # Handle file uploads using ApplicationAttachment model
            uploaded_files = request.FILES.getlist('requirements')
            for f in uploaded_files:
                ApplicationAttachment.objects.create(application=application, file=f)
            
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('application_success')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, self.template_name, {'form': form, 'programs': programs_for_dropdown})


class ServiceApplicationCreateView(LoginRequiredMixin, CreateView):
    """
    Create a service application.
    """
    model = ServiceApplication
    form_class = ServiceApplicationForm
    template_name = 'services/application_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.program = get_object_or_404(ServiceProgram, slug=kwargs['slug'])
        
        # Check if program is accepting applications
        if not self.program.is_accepting_applications():
            messages.error(request, "This program is not currently accepting applications.")
            return redirect('service_program_detail', slug=self.program.slug)

        # Ensure the user has a BMParliamentMember profile
        if not hasattr(request.user, 'bm_parliament_member'):
            messages.warning(request, "Please complete your member registration before applying for a program.")
            return redirect('member_registration') # Redirect to your member registration page

        # Check if user already has an application
        existing = ServiceApplication.objects.filter(
            service_program=self.program, # Changed from 'program' to 'service_program'
            constituent=request.user.bm_parliament_member
        ).first()
        
        if existing:
            messages.warning(request, "You already have an application for this program.")
            return redirect('service_application_detail', pk=existing.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        application = form.save(commit=False)
        application.service_program = self.program # Assign to service_program
        application.constituent = self.request.user.bm_parliament_member
        application.full_clean() # Validate that only one program is set
        application.save()
        
        # Create in Notion
        try:
            notion_service = NotionService()
            create_service_application_in_notion(
                application,
                notion_service,
                settings.NOTION_SERVICE_APPLICATION_DB_ID
            )
        except Exception as e:
            messages.warning(self.request, f"Application created but Notion sync failed: {str(e)}")
        
        # Send notification
        send_notification(
            application.constituent.user, # Send notification to the user linked to the constituent
            'Application Submitted',
            f'Your application for {application.program.name} has been submitted successfully.'
        )
        
        messages.success(self.request, "Your application has been submitted successfully!")
        return redirect('service_application_detail', pk=application.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = self.program
        return context


class ServiceApplicationDetailView(LoginRequiredMixin, DetailView): # Removed UserPassesTestMixin
    """
    View application details.
    """
    model = ServiceApplication
    template_name = 'services/staff/application_detail.html' # Corrected template path
    context_object_name = 'application'
    
    def get_queryset(self):
        # Pre-fetch related constituent and user to avoid N+1 queries and potential related object issues
        return super().get_queryset().select_related('constituent__user')

    def dispatch(self, request, *args, **kwargs):
        # Superusers always have access
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # For other users, apply the access logic
        application = self.get_object() # get_object needs to be called here for access checks
        
        # Staff and above can view any application
        if request.user.is_staff_or_above():
            return super().dispatch(request, *args, **kwargs)
        
        # Regular users can only view their own applications if they have a bm_parliament_member profile
        if hasattr(request.user, 'bm_parliament_member') and \
           request.user.bm_parliament_member == application.constituent:
            return super().dispatch(request, *args, **kwargs)
        
        # If none of the above, deny access
        messages.error(request, "You do not have permission to view this application.")
        return redirect('home') # Or a more appropriate access denied page
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        
        # Get disbursements
        context['disbursements'] = application.disbursements.all().order_by('-scheduled_date')
        
        # Process attachments to get just the filename
        processed_attachments = []
        for attachment in application.attachments.all():
            processed_attachments.append({
                'file_url': attachment.file.url,
                'file_name': os.path.basename(attachment.file.name),
                'description': attachment.description,
                'uploaded_at': attachment.uploaded_at,
            })
        context['processed_attachments'] = processed_attachments

        # Check if user can assess
        context['can_assess'] = self.request.user.is_staff_or_above()
        
        return context


class ServiceApplicationListView(LoginRequiredMixin, ListView):
    """
    View user's applications.
    """
    model = ServiceApplication
    template_name = 'services/application_list.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = ServiceApplication.objects.filter(
            constituent=self.request.user.bm_parliament_member
        )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-application_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ServiceApplication.APPLICATION_STATUS
        return context


class StaffApplicationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Staff view of all applications.
    """
    model = ServiceApplication
    template_name = 'services/program_list.html' # Changed template name
    context_object_name = 'applications' # Changed context object name
    paginate_by = 20
    
    def test_func(self):
        # Access granted to superusers and specific staff roles
        return self.request.user.is_superuser or \
               self.request.user.user_type in ['mp', 'chief_of_staff', 'admin', 'coordinator']
    
    def get_queryset(self):
        queryset = ServiceApplication.objects.all()
        
        # Get filters from request
        search = self.request.GET.get('search')
        program_slug = self.request.GET.get('program')
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        sort_by = self.request.GET.get('sort_by', '-application_date') # Default sort, changed from date_submitted to application_date
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(constituent__first_name__icontains=search) |
                Q(constituent__last_name__icontains=search) |
                Q(constituent__user__email__icontains=search) |
                Q(service_program__name__icontains=search) | # Search by service program name
                Q(ministry_program__title__icontains=search) # Search by ministry program name
            )
        if program_slug:
            queryset = queryset.filter(Q(service_program__slug=program_slug) | Q(ministry_program__slug=program_slug))
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority_level=priority)
        if date_from:
            queryset = queryset.filter(application_date__gte=date_from) # Changed from date_submitted to application_date
        if date_to:
            queryset = queryset.filter(application_date__lte=date_to) # Changed from date_submitted to application_date
        
        # Apply sorting
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Debug print to confirm template being rendered
        print(f"DEBUG: StaffApplicationListView is rendering template: {self.template_name}")

        # Get all programs for the filter dropdown
        service_programs = ServiceProgram.objects.filter(status='active')
        ministry_programs = MinistryProgram.objects.filter(status='active', is_public=True, is_deleted=False)
        context['all_programs'] = list(service_programs) + list(ministry_programs)
        
        context['application_statuses'] = ServiceApplication.APPLICATION_STATUS
        context['application_priorities'] = ServiceApplication.PRIORITY_LEVELS
        
        # Current filters for re-populating form fields
        context['current_filters'] = self.request.GET.copy()
        
        # Get statistics
        all_applications = ServiceApplication.objects.all()
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        context['total_applications'] = all_applications.count()
        context['approved_applications'] = all_applications.filter(status='approved').count()
        context['pending_applications'] = all_applications.filter(status='pending').count()
        context['rejected_applications'] = all_applications.filter(status='rejected').count()
        context['this_month_applications'] = all_applications.filter(application_date__gte=start_of_month).count() # Changed from date_submitted to application_date
        
        # Permission flags for the template
        user = self.request.user
        context['can_add_application'] = user.is_authenticated and hasattr(user, 'bm_parliament_member') # Assuming any logged-in member can add
        context['can_edit_application'] = user.is_staff_or_above() # Or more granular permission
        context['can_delete_application'] = user.is_staff_or_above() # Or more granular permission
        
        return context


class ServiceApplicationAssessmentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Assess a service application.
    """
    model = ServiceApplication
    form_class = ServiceAssessmentForm
    template_name = 'services/staff/application_assessment.html'
    
    def test_func(self):
        # Access granted to superusers and specific staff roles
        return self.request.user.is_superuser or \
               self.request.user.user_type in ['mp', 'chief_of_staff', 'admin', 'coordinator']
    
    def form_valid(self, form):
        application = form.save(commit=False)
        application.reviewed_at = timezone.now()
        application.reviewed_by = self.request.user
        
        # Handle approval/rejection
        action = self.request.POST.get('action')
        if action == 'approve':
            application.approve(
                self.request.user,
                amount=form.cleaned_data.get('assistance_amount'),
                description=form.cleaned_data.get('assistance_description')
            )
            
            # Send notification
            send_notification(
                application.constituent.user, # Send notification to the user linked to the constituent
                'Application Approved',
                f'Your application for {application.program.name} has been approved.'
            )
            
            messages.success(self.request, "Application approved successfully!")
            
        elif action == 'reject':
            application.reject(
                self.request.user,
                reason=form.cleaned_data.get('rejection_reason')
            )
            
            # Send notification
            send_notification(
                application.constituent.user, # Send notification to the user linked to the constituent
                'Application Update',
                f'Your application for {application.program.name} has been reviewed. Please check the portal for details.'
            )
            
            messages.success(self.request, "Application rejected.")
        
        else:
            application.save()
            messages.success(self.request, "Assessment saved.")
        
        # Update in Notion
        try:
            notion_service = NotionService()
            update_service_application_in_notion(application, notion_service)
        except Exception as e:
            messages.warning(self.request, f"Assessment saved but Notion sync failed: {str(e)}")
        
        return redirect('staff_application_detail', pk=application.pk)


class ServiceDisbursementCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create a disbursement for an approved application.
    """
    model = ServiceDisbursement
    form_class = ServiceDisbursementForm
    template_name = 'services/staff/disbursement_form.html'
    
    def test_func(self):
        # Access granted to superusers and specific staff roles
        return self.request.user.is_superuser or \
               self.request.user.user_type in ['mp', 'chief_of_staff', 'admin', 'coordinator']
    
    def dispatch(self, request, *args, **kwargs):
        self.application = get_object_or_404(ServiceApplication, pk=kwargs['application_id'])
        
        # Check if application is approved
        if self.application.status != 'approved':
            messages.error(request, "Cannot create disbursement for non-approved application.")
            return redirect('staff_application_detail', pk=self.application.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        disbursement = form.save(commit=False)
        disbursement.application = self.application
        disbursement.save()
        
        messages.success(self.request, "Disbursement scheduled successfully!")
        return redirect('staff_application_detail', pk=self.application.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        initial['amount'] = self.application.assistance_amount
        initial['recipient_name'] = self.application.constituent.get_full_name()
        return initial


class ServiceProgramDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Service program dashboard for staff.
    """
    template_name = 'services/staff/dashboard.html'
    
    def test_func(self):
        # Access granted to superusers and specific staff roles
        return self.request.user.is_superuser or \
               self.request.user.user_type in ['mp', 'chief_of_staff', 'admin', 'coordinator']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get programs
        context['programs'] = ServiceProgram.objects.all().order_by('-created_at')
        
        # Get overall statistics
        context['overall_stats'] = {
            'total_programs': ServiceProgram.objects.count(),
            'active_programs': ServiceProgram.objects.filter(status='active').count(),
            'total_applications': ServiceApplication.objects.count(),
            'pending_applications': ServiceApplication.objects.filter(status='submitted').count(),
            'total_beneficiaries': ServiceProgram.objects.aggregate(
                total=Sum('beneficiary_count')
            )['total'] or 0,
            'total_budget': ServiceProgram.objects.aggregate(
                total=Sum('total_budget')
            )['total'] or 0,
            'budget_utilized': ServiceProgram.objects.aggregate(
                total=Sum('budget_utilized')
            )['total'] or 0,
        }
        
        # Get recent applications
        context['recent_applications'] = ServiceApplication.objects.filter(
            status='submitted'
        ).order_by('-application_date')[:10]
        
        # Get upcoming disbursements
        context['upcoming_disbursements'] = ServiceDisbursement.objects.filter(
            status='pending',
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date')[:10]
        
        return context
