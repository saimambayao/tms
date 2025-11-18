from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View, DetailView, ListView, CreateView, UpdateView, DeleteView
from apps.communications.models import ContactFormSubmission
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.db import connection
from django.core.cache import cache
from django.core.exceptions import ValidationError # Import ValidationError
import json
import csv
import os
from datetime import datetime, timedelta
import logging
from apps.constituents.models import Constituent, FahanieCaresMember
from apps.referrals.models import ServiceCategory, Service
from apps.chapters.models import Chapter, ChapterMembership
from apps.services.models import ServiceProgram, MinistryProgram, MinistryProgramHistory

logger = logging.getLogger(__name__)
from apps.services.audit import MinistryProgramAuditService
from apps.communications.forms import ContactForm, PartnershipForm, DonationForm, MessageComposeForm
from apps.communications.models import ContactFormSubmission, PartnershipSubmission, DonationSubmission, CommunicationMessage
from apps.staff.models import Staff
from apps.users.models import User # Import User model
from .models import Announcement
from .forms import StaffForm
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import secrets
import string
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.constituents.forms import FahanieCaresMemberFormSet # Import the formset
from django.core.exceptions import ValidationError # Import ValidationError

class TestUrlView(TemplateView):
    """A simple view to test URL reversal."""
    template_name = 'core/test_url.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'URL Test Page'
        return context

class HomePageView(TemplateView):
    """Home page view."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured services
        context['featured_services'] = Service.objects.filter(
            is_active=True,
            is_featured=True
        )[:6]
        
        # Get active chapters count
        context['active_chapters'] = Chapter.objects.filter(
            status='active'
        ).count()
        
        # Get service programs
        context['service_programs'] = ServiceProgram.objects.filter(
            status='active',
            published_at__isnull=False
        )[:3]
        
        # Production impact stats - dynamically fetched
        context['impact_stats'] = {
            'registered_members': FahanieCaresMember.objects.count(),
            'active_chapters': Chapter.objects.filter(status='active').count(),
            'community_events': MinistryProgram.objects.filter(program_source='fahaniecares', is_public=True).count(),
            'volunteer_hours': ChapterMembership.objects.filter(is_volunteer=True, status='active').aggregate(total_hours=Sum('volunteer_hours'))['total_hours'] or 0
        }
        
        # Get latest announcements from database
        context['announcements'] = Announcement.objects.filter(
            status='published',
            is_featured=True
        ).order_by('-published_date')[:3]
        
        # Add contact form to context
        context['contact_form'] = ContactForm()
        
        return context
        
    def post(self, request, *args, **kwargs):
        # Process contact form submission from Home page
        contact_form = ContactForm(request.POST)
        
        if contact_form.is_valid():
            # Save the contact form submission
            submission = contact_form.save(commit=False)
            submission.form_source = 'home_page'
            submission.save()
            
            context = self.get_context_data(**kwargs)
            context['message'] = 'Thank you for your message. We will get back to you soon.'
            context['message_type'] = 'success'
            context['contact_form'] = ContactForm()  # Fresh form
            return render(request, self.template_name, context)
        else:
            # Form has errors
            context = self.get_context_data(**kwargs)
            context['contact_form'] = contact_form
            context['message'] = 'Please correct the errors below.'
            context['message_type'] = 'error'
            return render(request, self.template_name, context)

class MinistriesPPAsView(TemplateView):
    """Sector-based PPAs browsing view."""
    template_name = 'core/ministries_ppas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get sector filter from URL parameter
        sector_filter = self.request.GET.get('sector')
        
        # Define sector to ministry mapping
        sector_mapping = self._get_sector_mapping()
        
        # Get all ministry programs (excluding deleted ones and TDIF projects)
        ministry_programs = MinistryProgram.objects.filter(
            is_deleted=False,
            is_public=True
        ).exclude(
            program_source='tdif'
        ).order_by('ministry', '-created_at')
        
        # Filter by sector if specified
        if sector_filter and sector_filter in sector_mapping:
            ministry_codes = sector_mapping[sector_filter]['ministries']
            ministry_programs = ministry_programs.filter(ministry__in=ministry_codes)
        
        # Get sector statistics
        sectors = []
        for sector_code, sector_data in sector_mapping.items():
            count = MinistryProgram.objects.filter(
                ministry__in=sector_data['ministries'],
                is_deleted=False,
                is_public=True
            ).exclude(
                program_source='tdif'
            ).count()
            
            if count > 0:  # Only include sectors with programs
                sectors.append({
                    'code': sector_code,
                    'name': sector_data['name'],
                    'description': sector_data['description'],
                    'icon': sector_data['icon'],
                    'color': sector_data['color'],
                    'count': count,
                    'ministries': [
                        {
                            'code': ministry_code,
                            'name': dict(MinistryProgram.MINISTRIES)[ministry_code],
                            'count': MinistryProgram.objects.filter(
                                ministry=ministry_code,
                                is_deleted=False,
                                is_public=True
                            ).exclude(program_source='tdif').count()
                        } 
                        for ministry_code in sector_data['ministries']
                        if MinistryProgram.objects.filter(
                            ministry=ministry_code,
                            is_deleted=False,
                            is_public=True
                        ).exclude(program_source='tdif').count() > 0
                    ]
                })
        
        # Get featured programs
        featured_programs = MinistryProgram.objects.filter(
            is_featured=True,
            is_deleted=False,
            is_public=True
        ).exclude(
            program_source='tdif'
        )[:6]
        
        # Prepare PPAS items for template with sector information
        ppas_items = []
        for program in ministry_programs[:12]:  # Limit to 12 for initial load
            # Format budget for display
            budget_display = ''
            if program.total_budget > 0:
                if program.total_budget >= 1000000000:  # Billions
                    budget_display = f"₱{program.total_budget / 1000000000:.1f}B"
                elif program.total_budget >= 1000000:  # Millions
                    budget_display = f"₱{program.total_budget / 1000000:.1f}M"
                elif program.total_budget >= 1000:  # Thousands
                    budget_display = f"₱{program.total_budget / 1000:.1f}K"
                else:
                    budget_display = f"₱{program.total_budget:,.0f}"
            
            # Get sector for this program
            program_sector = self._get_program_sector(program.ministry, sector_mapping)
            
            ppas_items.append({
                'id': program.id,
                'title': program.title,
                'type': program.get_ppa_type_display(),
                'ministry': program.get_ministry_display(),
                'ministry_code': program.ministry,
                'sector': program_sector['name'] if program_sector else 'Other',
                'sector_code': program_sector['code'] if program_sector else 'other',
                'sector_icon': program_sector['icon'] if program_sector else 'fas fa-cog',
                'sector_color': program_sector['color'] if program_sector else 'gray',
                'description': program.description[:200] + '...' if len(program.description) > 200 else program.description,
                'location': program.geographic_coverage,
                'target': program.target_beneficiaries[:100] + '...' if len(program.target_beneficiaries) > 100 else program.target_beneficiaries,
                'timeline': f"{program.start_date.strftime('%b %Y')} - {program.end_date.strftime('%b %Y')}",
                'budget': program.total_budget,
                'budget_display': budget_display,
                'status': program.get_status_display(),
                'priority': program.get_priority_level_display(),
                'slug': program.slug
            })
        
        # Get current sector data for display
        current_sector = None
        if sector_filter and sector_filter in sector_mapping:
            current_sector = {
                'code': sector_filter,
                'name': sector_mapping[sector_filter]['name'],
                'description': sector_mapping[sector_filter]['description'],
                'icon': sector_mapping[sector_filter]['icon'],
                'color': sector_mapping[sector_filter]['color'],
                'count': len([item for item in ppas_items if item['sector_code'] == sector_filter])
            }
        
        context.update({
            'sectors': sectors,
            'ppas_items': ppas_items,
            'featured_programs': featured_programs,
            'sector_filter': sector_filter,
            'current_sector': current_sector,
            'total_programs': ministry_programs.count(),
            'sector_mapping': sector_mapping,
        })
        
        return context
    
    def _get_sector_mapping(self):
        """Define sector to ministry mapping with visual attributes."""
        return {
            'health': {
                'name': 'Health',
                'description': 'Healthcare services, medical programs, and public health initiatives for the Bangsamoro people.',
                'icon': 'fas fa-heartbeat',
                'color': 'green',
                'ministries': ['moh']
            },
            'education': {
                'name': 'Education',
                'description': 'Educational programs, training initiatives, and skills development for learners of all ages.',
                'icon': 'fas fa-graduation-cap',
                'color': 'blue',
                'ministries': ['mbasiced', 'mhe', 'volunteer_teachers']
            },
            'agriculture': {
                'name': 'Agriculture',
                'description': 'Agricultural development, fisheries support, and agrarian reform programs.',
                'icon': 'fas fa-seedling',
                'color': 'green',
                'ministries': ['mafar']
            },
            'social_services': {
                'name': 'Social Services',
                'description': 'Social protection, welfare programs, and support for vulnerable populations.',
                'icon': 'fas fa-hands-helping',
                'color': 'purple',
                'ministries': ['mssd']
            },
            'infrastructure': {
                'name': 'Infrastructure',
                'description': 'Public works, transportation networks, and infrastructure development projects.',
                'icon': 'fas fa-road',
                'color': 'orange',
                'ministries': ['mpwh', 'motc']
            },
            'economic_development': {
                'name': 'Economic Development',
                'description': 'Trade promotion, industry development, tourism, and employment opportunities.',
                'icon': 'fas fa-chart-line',
                'color': 'indigo',
                'ministries': ['mtit', 'mle']
            },
            'environment_governance': {
                'name': 'Environment & Governance',
                'description': 'Environmental protection, sustainable development, and governance initiatives.',
                'icon': 'fas fa-leaf',
                'color': 'emerald',
                'ministries': ['mei']
            }
        }
    
    def _get_program_sector(self, ministry_code, sector_mapping):
        """Get sector information for a given ministry code."""
        for sector_code, sector_data in sector_mapping.items():
            if ministry_code in sector_data['ministries']:
                return {
                    'code': sector_code,
                    'name': sector_data['name'],
                    'icon': sector_data['icon'],
                    'color': sector_data['color']
                }
        return None
    
    def _get_ministry_description(self, ministry_code):
        """Get description for each ministry."""
        descriptions = {
            'mssd': 'Leading social protection and welfare programs for vulnerable populations across BARMM.',
            'mafar': 'Promoting sustainable agriculture, fisheries, and agrarian reform for food security and economic growth.',
            'mtit': 'Driving economic development through trade promotion, industrial growth, and tourism development.',
            'mhe': 'Advancing higher education and technical skills development for the Bangsamoro people.',
            'mbasiced': 'Ensuring quality basic education and technical training for all learners in BARMM.',
            'moh': 'Providing comprehensive healthcare services and promoting public health across the region.',
            'mpwh': 'Building essential infrastructure and maintaining public works for regional development.',
            'motc': 'Developing transportation networks and communication systems for connectivity and growth.',
            'mei': 'Protecting the environment and promoting sustainable development and good governance.',
            'mle': "Creating employment opportunities and protecting workers' rights in BARMM.",
        }
        return descriptions.get(ministry_code, 'Ministry programs and services for the Bangsamoro people.')

class ProgramsView(TemplateView):
    """#FahanieCares Programs view - unified with MinistryProgram model."""
    template_name = 'core/programs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters - using sector instead of type
        sector_filter = self.request.GET.get('sector', '')
        sort_by = self.request.GET.get('sort', '-start_date')
        
        # Get sector mapping
        sector_mapping = self._get_sector_mapping()
        
        # Get #FahanieCares programs using unified MinistryProgram model
        programs = MinistryProgram.objects.filter(
            program_source='fahaniecares',  # Only #FahanieCares programs
            is_public=True,                 # Constituent-accessible programs
            is_deleted=False,               # Not deleted
            status__in=['active', 'pending_approval']  # Available statuses
        )
        
        # Apply sector filter if specified
        if sector_filter and sector_filter in sector_mapping:
            ministry_codes = sector_mapping[sector_filter]['ministries']
            programs = programs.filter(ministry__in=ministry_codes)
        
        # Apply sorting with validation
        valid_sort_fields = ['-start_date', 'start_date', 'title', '-title', 'end_date', '-end_date']
        if sort_by in valid_sort_fields:
            programs = programs.order_by(sort_by)
        else:
            programs = programs.order_by('-start_date')  # Default sort
        
        # Prepare programs data for template compatibility
        program_list = []
        for program in programs:
            # Get sector for this program
            program_sector = self._get_program_sector(program.ministry, sector_mapping)
            
            # Map MinistryProgram fields to template expectations
            program_data = {
                'id': program.id,
                'title': program.title,
                'category': program_sector['name'] if program_sector else program.get_ppa_type_display(),  # Use sector as category
                'status': program.get_status_display(),
                'description': program.description[:200] + '...' if len(program.description) > 200 else program.description,
                'eligibility': program.target_beneficiaries[:100] + '...' if len(program.target_beneficiaries) > 100 else program.target_beneficiaries,
                'application_deadline': program.end_date,  # Map end_date to application_deadline
                'start_date': program.start_date,
                'end_date': program.end_date,
                'geographic_coverage': program.geographic_coverage,
                'budget_display': self._format_budget(program.total_budget),
                'slug': program.slug,
                'is_featured': program.is_featured,
                'ministry': program.get_ministry_display(),
                'priority': program.get_priority_level_display(),
                'sector': program_sector['name'] if program_sector else 'Other',
                'sector_code': program_sector['code'] if program_sector else 'other',
                'sector_icon': program_sector['icon'] if program_sector else 'fas fa-cog',
                'sector_color': program_sector['color'] if program_sector else 'gray',
            }
            program_list.append(program_data)
        
        context['programs'] = program_list
        
        # Prepare sector data for filters
        sectors = []
        for sector_code, sector_data in sector_mapping.items():
            count = len([p for p in program_list if p.get('sector_code') == sector_code])
            if count > 0:  # Only include sectors with programs
                sectors.append({
                    'code': sector_code,
                    'name': sector_data['name'],
                    'icon': sector_data['icon'],
                    'color': sector_data['color'],
                    'count': count
                })
        
        # Add filtering context
        context['sectors'] = sectors
        context['current_sector'] = sector_filter
        context['current_sort'] = sort_by
        context['total_programs'] = len(program_list)
        
        # Add program statistics
        context['program_stats'] = {
            'total': len(program_list),
            'active': len([p for p in program_list if 'Active' in p['status']]),
            'featured': len([p for p in program_list if p['is_featured']]),
        }
        
        return context
    
    def _get_sector_mapping(self):
        """Define sector to ministry mapping with visual attributes."""
        return {
            'health': {
                'name': 'Health',
                'description': 'Healthcare services, medical programs, and public health initiatives.',
                'icon': 'fas fa-heartbeat',
                'color': 'green',
                'ministries': ['moh', 'MOH']
            },
            'education': {
                'name': 'Education',
                'description': 'Educational programs, training initiatives, and skills development.',
                'icon': 'fas fa-graduation-cap',
                'color': 'blue',
                'ministries': ['mbasiced', 'mhe', 'MOE', 'TESDA', 'volunteer_teachers']
            },
            'agriculture': {
                'name': 'Agriculture',
                'description': 'Agricultural development, fisheries support, and agrarian reform programs.',
                'icon': 'fas fa-seedling',
                'color': 'green',
                'ministries': ['mafar', 'MAFAR']
            },
            'social_services': {
                'name': 'Social Services',
                'description': 'Social protection, welfare programs, and support for vulnerable populations.',
                'icon': 'fas fa-hands-helping',
                'color': 'purple',
                'ministries': ['mssd', 'MSSD']
            },
            'infrastructure': {
                'name': 'Infrastructure',
                'description': 'Public works, transportation networks, and infrastructure development projects.',
                'icon': 'fas fa-road',
                'color': 'orange',
                'ministries': ['mpwh', 'MPWH', 'motc', 'MOTC']
            },
            'economic_development': {
                'name': 'Economic Development',
                'description': 'Trade promotion, industry development, tourism, and employment opportunities.',
                'icon': 'fas fa-chart-line',
                'color': 'indigo',
                'ministries': ['mtit', 'MTIT', 'mle', 'MLE']
            }
        }
    
    def _get_program_sector(self, ministry_code, sector_mapping):
        """Get sector information for a given ministry code."""
        for sector_code, sector_data in sector_mapping.items():
            if ministry_code in sector_data['ministries']:
                return {
                    'code': sector_code,
                    'name': sector_data['name'],
                    'icon': sector_data['icon'],
                    'color': sector_data['color']
                }
        return None
    
    def _format_budget(self, budget):
        """Format budget for display."""
        if not budget or budget == 0:
            return "Budget TBD"
        
        if budget >= 1_000_000_000:
            return f"₱{budget / 1_000_000_000:.1f}B"
        elif budget >= 1_000_000:
            return f"₱{budget / 1_000_000:.1f}M"
        elif budget >= 1_000:
            return f"₱{budget / 1_000:.1f}K"
        else:
            return f"₱{budget:,.0f}"

class MobileServiceView(View):
    """Mobile-optimized service view."""
    
    def get(self, request):
        # Detect if mobile device
        is_mobile = self.is_mobile_device(request)
        
        if is_mobile:
            return render(request, 'mobile/services.html')
        else:
            return redirect('services')
    
    def is_mobile_device(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_agents = ['android', 'iphone', 'ipad', 'mobile']
        return any(agent in user_agent for agent in mobile_agents)

class OfflineFormView(View):
    """Offline form for field registration."""
    
    def get(self, request):
        return render(request, 'mobile/offline_form.html')

@csrf_exempt
def mobile_sync_api(request):
    """API endpoint for syncing offline mobile data."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, 405)
    
    try:
        data = json.loads(request.body)
        
        # Create constituent record
        constituent = Constituent.objects.create(
            full_name=data.get('name'),
            contact_number=data.get('contact'),
            birth_date=data.get('birthdate'),
            municipality=data.get('municipality'),
            barangay=data.get('barangay'),
            complete_address=data.get('address'),
            created_by=request.user if request.user.is_authenticated else None
        )
        
        # Handle service request if provided
        if data.get('service_type'):
            # Create service request/referral
            from apps.referrals.models import Referral
            
            service = Service.objects.filter(
                service_type=data.get('service_type')
            ).first()
            
            if service:
                referral = Referral.objects.create(
                    constituent=constituent,
                    service=service,
                    description=data.get('description', ''),
                    urgency_level=data.get('urgency', 'normal'),
                    created_by=request.user if request.user.is_authenticated else None
                )
        
        return JsonResponse({
            'success': True,
            'constituent_id': constituent.id,
            'message': 'Data synchronized successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, 400)

def offline_page(request):
    """Offline fallback page."""
    return render(request, 'core/offline.html')

def service_worker(request):
    """Serve the service worker file."""
    sw_path = settings.STATICFILES_DIRS[0] / 'js' / 'service-worker.js'
    with open(sw_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, 'application/javascript')

def manifest(request):
    """Serve the PWA manifest file."""
    manifest_path = settings.STATICFILES_DIRS[0] / 'manifest.json'
    with open(manifest_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, 'application/json')

class AboutPageView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add contact form with default subject for MP office contact
        context['contact_form'] = ContactForm(default_subject='feedback')

        # Impact stats for About page
        context['impact_stats'] = {
            'registered_members': FahanieCaresMember.objects.count(),
            'active_chapters': Chapter.objects.filter(status='active').count(),
            'community_events': MinistryProgram.objects.filter(program_source='fahaniecares', is_public=True).count(),
            'volunteer_hours': ChapterMembership.objects.filter(is_volunteer=True, status='active').aggregate(total_hours=Sum('volunteer_hours'))['total_hours'] or 0
        }
        return context
    
    def post(self, request, *args, **kwargs):
        # Process contact form submission from About Us page
        contact_form = ContactForm(request.POST, default_subject='feedback')
        
        if contact_form.is_valid():
            # Save the contact form submission
            submission = contact_form.save(commit=False)
            submission.form_source = 'about_page_mp_office'
            submission.save()
            
            context = self.get_context_data(**kwargs)
            context['message'] = "Thank you for contacting MP Uy-Oyod's office. We will get back to you soon."
            context['message_type'] = 'success'
            context['contact_form'] = ContactForm(default_subject='feedback')  # Fresh form
            return render(request, self.template_name, context)
        else:
            # Form has errors
            context = self.get_context_data(**kwargs)
            context['contact_form'] = contact_form
            context['message'] = 'Please correct the errors below.'
            context['message_type'] = 'error'
            return render(request, self.template_name, context)

class PublicChaptersView(TemplateView):
    """Public chapters overview page - accessible to all."""
    template_name = 'core/chapters.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chapters'
        context['contact_form'] = ContactForm()
        context['message'] = None
        context['message_type'] = None
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle contact form submission for starting a new chapter."""
        context = self.get_context_data(**kwargs)
        contact_form = ContactForm(request.POST)
        
        if contact_form.is_valid():
            try:
                # Save the form submission with proper source tracking
                submission = contact_form.save(commit=False)
                submission.form_source = 'start_new_chapter_form'
                submission.subject = 'chapter'  # Ensure subject is set to chapter
                submission.save()
                
                context['message'] = "Thank you for your interest in starting a new chapter! Our team will contact you soon."
                context['message_type'] = 'success'
                context['contact_form'] = ContactForm()  # Reset form
            except Exception as e:
                context['message'] = "There was an error submitting your request. Please try again or contact us directly."
                context['message_type'] = 'error'
                context['contact_form'] = contact_form
        else:
            context['message'] = "Please correct the errors below and try again."
            context['message_type'] = 'error'
            context['contact_form'] = contact_form
            
        return render(request, self.template_name, context)


class ChaptersPageView(LoginRequiredMixin, TemplateView):
    """Database of Chapters view - for authorized users only."""
    template_name = 'core/database_chapters.html'
    login_url = reverse_lazy('login')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Security: Log access attempts
        logger.info(f"User {self.request.user.username} attempting to access Database of Chapters")
        
        # Check if user has appropriate role for database access
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            # Log unauthorized access attempt
            logger.warning(f"Unauthorized access attempt to Database of Chapters by user {self.request.user.username}")
            messages.error(self.request, "You do not have permission to access the Database of Chapters.")
            return redirect('home')
        
        # Log successful access
        logger.info(f"User {self.request.user.username} granted access to Database of Chapters")
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Page title and metadata
        context['title'] = 'Database of Chapters'
        
        # Get filter parameters
        current_filters = {
            'search': self.request.GET.get('search', ''),
            'tier': self.request.GET.get('tier', ''),
            'status': self.request.GET.get('status', ''),
            'location': self.request.GET.get('location', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'sort_by': self.request.GET.get('sort_by', '-created_at'),
        }
        context['current_filters'] = current_filters
        
        # Get chapters from the database
        chapters = Chapter.objects.all()
        
        # Apply filters
        if current_filters['search']:
            chapters = chapters.filter(
                Q(name__icontains=current_filters['search']) |
                Q(location__icontains=current_filters['search']) |
                Q(description__icontains=current_filters['search']) |
                Q(coordinator_name__icontains=current_filters['search'])
            )
        
        if current_filters['tier']:
            chapters = chapters.filter(tier=current_filters['tier'])
            
        if current_filters['status']:
            chapters = chapters.filter(status=current_filters['status'])
            
        if current_filters['location']:
            chapters = chapters.filter(location__icontains=current_filters['location'])
            
        # Date range filtering
        if current_filters['date_from']:
            try:
                date_from = datetime.strptime(current_filters['date_from'], '%Y-%m-%d').date()
                chapters = chapters.filter(created_at__gte=date_from)
            except ValueError:
                pass
                
        if current_filters['date_to']:
            try:
                date_to = datetime.strptime(current_filters['date_to'], '%Y-%m-%d').date()
                chapters = chapters.filter(created_at__lte=date_to)
            except ValueError:
                pass
        
        # Sorting
        if current_filters['sort_by']:
            chapters = chapters.order_by(current_filters['sort_by'])
        
        context['chapters'] = chapters
        
        # Statistics for dashboard
        context['stats'] = {
            'total_chapters': Chapter.objects.count(),
            'active_chapters': Chapter.objects.filter(status='active').count(),
            'provincial_chapters': Chapter.objects.filter(tier='provincial').count(),
            'municipal_chapters': Chapter.objects.filter(tier='municipal').count(),
        }
        
        # Get available filter options
        context['tier_choices'] = Chapter.TIER_CHOICES if hasattr(Chapter, 'TIER_CHOICES') else []
        context['status_choices'] = Chapter.STATUS_CHOICES if hasattr(Chapter, 'STATUS_CHOICES') else []
        
        # Import constituents model for relationship functionality
        from apps.constituents.models import Constituent, FahanieCaresMember
        
        # Get registrants that can be assigned to chapters
        context['unassigned_registrants'] = FahanieCaresMember.objects.filter(
            status='approved',
            assigned_chapter__isnull=True
        )[:10]  # Show recent 10 for quick assignment
        
        # Get active chapters for assignment dropdown
        context['active_chapters'] = Chapter.objects.filter(status='active').order_by('name')
        
        # Get chapter requests for the "New Chapter Requests" section
        from apps.communications.models import ContactFormSubmission
        from django.core.paginator import Paginator
        
        # Filter chapter requests
        chapter_requests = ContactFormSubmission.objects.filter(
            Q(subject='chapter') | Q(form_source='start_new_chapter_form')
        ).order_by('-submitted_at')
        
        # Handle pagination for chapter requests
        page_number = self.request.GET.get('requests_page', 1)
        paginator = Paginator(chapter_requests, 10)  # 10 items per page
        page_obj = paginator.get_page(page_number)
        
        context['chapter_requests'] = page_obj
        context['chapter_requests_count'] = chapter_requests.count()
        
        # Chapter requests statistics
        context['chapter_requests_stats'] = {
            'total': chapter_requests.count(),
            'new': chapter_requests.filter(status='new').count(),
            'in_progress': chapter_requests.filter(status='in_progress').count(),
            'resolved': chapter_requests.filter(status='resolved').count(),
            'closed': chapter_requests.filter(status='closed').count(),
        }
        
        return context


@method_decorator(login_required, name='dispatch')
class AssignChapterView(View):
    """
    AJAX view to assign approved registrants to chapters.
    Authorized roles: Superuser, MP, Chief of Staff, System Admin, and Coordinator
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has appropriate role for chapter assignment
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (request.user.is_superuser or 
                hasattr(request.user, 'user_type') and 
                request.user.user_type in allowed_roles):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, 403)
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle chapter assignment via AJAX POST request"""
        try:
            # Get data from request
            registrant_id = request.POST.get('registrant_id')
            chapter_id = request.POST.get('chapter_id')
            
            if not registrant_id or not chapter_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing registrant_id or chapter_id'
                }, 400)
            
            # Import models
            from apps.constituents.models import FahanieCaresMember
            from apps.chapters.models import Chapter
            
            # Get registrant and chapter
            try:
                registrant = FahanieCaresMember.objects.get(
                    id=registrant_id, 
                    status='approved',
                    assigned_chapter__isnull=True
                )
            except FahanieCaresMember.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Registrant not found or already assigned'
                }, 404)
            
            try:
                chapter = Chapter.objects.get(id=chapter_id, status='active')
            except Chapter.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Chapter not found or inactive'
                }, 404)
            
            # Assign registrant to chapter
            registrant.assigned_chapter = chapter
            registrant.chapter_assigned_date = timezone.now().date()
            registrant.chapter_assigned_by = request.user
            registrant.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{registrant.get_full_name()} assigned to {chapter.name}',
                'registrant_name': registrant.get_full_name(),
                'chapter_name': chapter.name,
                'assigned_date': registrant.chapter_assigned_date.strftime('%B %d, %Y')
            })
            
        except Exception as e:
            logger.error(f"Error in chapter assignment: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': 'An unexpected error occurred'
            }, 500)


class ContactPageView(TemplateView):
    """Contact page view."""
    template_name = 'core/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add contact form for general inquiries
        context['contact_form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        # Process contact form submission from Contact page
        contact_form = ContactForm(request.POST)
        
        if contact_form.is_valid():
            # Save the contact form submission
            submission = contact_form.save(commit=False)
            submission.form_source = 'contact_page'
            submission.save()
            
            context = self.get_context_data(**kwargs)
            context['message'] = 'Thank you for your message. We will get back to you soon.'
            context['message_type'] = 'success'
            context['contact_form'] = ContactForm()  # Fresh form
            return render(request, self.template_name, context)
        else:
            # Form has errors
            context = self.get_context_data(**kwargs)
            context['contact_form'] = contact_form
            context['message'] = 'Please correct the errors below.'
            context['message_type'] = 'error'
            return render(request, self.template_name, context)


class PartnerPageView(TemplateView):
    """Partnership page view."""
    template_name = "core/partner.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["partnership_form"] = PartnershipForm()
        return context
    
    def post(self, request, *args, **kwargs):
        partnership_form = PartnershipForm(request.POST)
        
        if partnership_form.is_valid():
            partnership_form.save()
            
            context = self.get_context_data(**kwargs)
            context["message"] = "Thank you for your partnership inquiry. Our team will review your application and get back to you soon."
            context["message_type"] = "success"
            context["partnership_form"] = PartnershipForm()  # Fresh form
            return render(request, self.template_name, context)
        else:
            context = self.get_context_data(**kwargs)
            context["partnership_form"] = partnership_form
            context["message"] = "Please correct the errors below."
            context["message_type"] = "error"
            return render(request, self.template_name, context)


class DonatePageView(TemplateView):
    """Donation page view."""
    template_name = "core/donate.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["donation_form"] = DonationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        donation_form = DonationForm(request.POST)
        
        if donation_form.is_valid():
            donation_form.save()
            
            context = self.get_context_data(**kwargs)
            context["message"] = "Thank you for your donation inquiry. Our team will contact you to finalize the donation process."
            context["message_type"] = "success"
            context["donation_form"] = DonationForm()  # Fresh form
            return render(request, self.template_name, context)
        else:
            context = self.get_context_data(**kwargs)
            context["donation_form"] = donation_form
            context["message"] = "Please correct the errors below."
            context["message_type"] = "error"
            return render(request, self.template_name, context)


class AnnouncementListView(ListView):
    """List all published announcements"""
    model = Announcement
    template_name = 'core/announcements.html'
    context_object_name = 'announcements'
    paginate_by = 12
    
    def get_queryset(self):
        return Announcement.objects.filter(status='published').order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Latest Updates'
        
        # Calculate statistics for the public page
        from django.utils import timezone
        from datetime import datetime
        
        # Get current month date range
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # All published announcements
        published_announcements = Announcement.objects.filter(status='published')
        
        # Statistics
        context['total_updates'] = published_announcements.count()
        context['this_month_count'] = published_announcements.filter(
            published_date__gte=current_month_start
        ).count()
        context['programs_count'] = published_announcements.filter(category='program').count()
        context['parliament_count'] = published_announcements.filter(category='parliament').count()
        
        return context


class AnnouncementDetailView(DetailView):
    """View individual announcement details."""
    model = Announcement
    template_name = 'core/announcement_detail.html'
    context_object_name = 'announcement'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Announcement.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        
        # Get related announcements
        context['related_announcements'] = Announcement.objects.filter(
            status='published',
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        
        return context


class TDIFProjectsView(TemplateView):
    """TDIF Projects view - Transitional Development Impact Fund with enhanced display."""
    template_name = 'core/tdif_projects.html'

class CompletedProgramsView(TemplateView):
    """View for displaying completed programs."""
    template_name = 'core/completed_programs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Completed Programs'
        context['description'] = 'A showcase of programs that have been successfully completed, leaving a lasting positive change in our communities.'

        # Get filter parameters
        current_filters = {
            'search': self.request.GET.get('search', ''),
            'ministry': self.request.GET.get('ministry', ''),
            'location': self.request.GET.get('location', ''),
            'sort_by': self.request.GET.get('sort', '-end_date'),
        }
        context['current_filters'] = current_filters

        # Fetch completed programs from the database
        completed_programs = MinistryProgram.objects.filter(
            status='completed',
            is_public=True,
            is_deleted=False,
            program_source__in=['fahaniecares', 'ministry'] # Include programs from these sources
        )

        # Apply filters
        if current_filters['search']:
            completed_programs = completed_programs.filter(
                Q(title__icontains=current_filters['search']) |
                Q(description__icontains=current_filters['search'])
            )
        if current_filters['ministry']:
            completed_programs = completed_programs.filter(ministry=current_filters['ministry'])
        if current_filters['location']:
            completed_programs = completed_programs.filter(geographic_coverage__icontains=current_filters['location'])

        # Apply sorting
        valid_sort_fields = ['-end_date', 'end_date', 'title', '-title', 'ministry', '-ministry']
        if current_filters['sort_by'] in valid_sort_fields:
            completed_programs = completed_programs.order_by(current_filters['sort_by'])
        else:
            completed_programs = completed_programs.order_by('-end_date') # Default sort

        program_list = []
        for program in completed_programs:
            program_list.append({
                'id': program.id,
                'title': program.title,
                'description': program.description[:200] + '...' if len(program.description) > 200 else program.description,
                'end_date': program.end_date,
                'geographic_coverage': program.geographic_coverage,
                'slug': program.slug,
                'ministry': program.get_ministry_display(),
            })
        
        context['completed_programs'] = program_list
        context['total_completed_programs'] = len(program_list)

        # Provide choices for filters
        context['ministry_choices'] = MinistryProgram.MINISTRIES
        # Get unique locations from completed programs for filter options
        context['location_choices'] = sorted(list(MinistryProgram.objects.filter(
            status='completed', is_public=True, is_deleted=False
        ).values_list('geographic_coverage', flat=True).distinct().exclude(geographic_coverage__isnull=True).exclude(geographic_coverage='')))
        
        # Preserve filter parameters in pagination/sort links
        filter_params = ''
        for key, value in self.request.GET.items():
            if key != 'page' and value:
                filter_params += f'&{key}={value}'
        context['filter_params'] = filter_params

        return context


class AccessibleMinistryProgramsView(TemplateView):
    """Ministry Programs view - curated programs with MP constituent access."""
    template_name = 'core/accessible_ministry_programs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ministry Programs data
        context['title'] = 'Ministry Programs'
        context['description'] = 'Curated selection of Bangsamoro ministry programs designed for easy access and streamlined application processes.'
        
        # Get query parameters for filtering and sorting - using sector instead of type
        current_sector = self.request.GET.get('sector', '')
        current_sort = self.request.GET.get('sort', '-start_date')
        
        # Get sector mapping
        sector_mapping = self._get_sector_mapping()
        
        try:
            # Get ministry programs using unified model
            programs = MinistryProgram.objects.filter(
                program_source='ministry',
                is_public=True,
                is_deleted=False,
                status__in=['active', 'pending_approval']
            )
            
            # Apply sector filtering if specified
            if current_sector and current_sector in sector_mapping:
                ministry_codes = sector_mapping[current_sector]['ministries']
                programs = programs.filter(ministry__in=ministry_codes)
            
            # Apply sorting
            if current_sort:
                programs = programs.order_by(current_sort)
            
            # Format programs for template compatibility
            formatted_programs = []
            for program in programs:
                try:
                    # Format budget for display
                    budget_display = ""
                    if program.total_budget:
                        if program.total_budget >= 1000000:
                            budget_display = f"₱{program.total_budget/1000000:.1f}M"
                        elif program.total_budget >= 1000:
                            budget_display = f"₱{program.total_budget/1000:.0f}K"
                        else:
                            budget_display = f"₱{program.total_budget:,.0f}"
                    
                    formatted_programs.append({
                        'id': program.id,
                        'title': program.title,
                        'description': program.description or program.objectives or "",
                        'category': program.get_ppa_type_display() if hasattr(program, 'get_ppa_type_display') else program.ppa_type.title(),
                        'status': program.get_status_display() if hasattr(program, 'get_status_display') else program.status.title(),
                        'priority': program.get_priority_level_display() if hasattr(program, 'get_priority_level_display') else program.priority_level.title(),
                        'is_featured': program.is_featured,
                        'eligibility': program.target_beneficiaries,
                        'application_deadline': None,  # Not available in this model
                        'geographic_coverage': program.geographic_coverage,
                        'budget_display': budget_display,
                        'ministry': program.get_ministry_display() if hasattr(program, 'get_ministry_display') else program.ministry.upper(),
                        'slug': program.slug, # Add slug for detail page redirection
                    })
                    
                except Exception as format_error:
                    # Log the error but continue processing other programs
                    logger.error(f"Error formatting ministry program {program.id}: {format_error}")
                    continue
            
            context['programs'] = formatted_programs
            
        except Exception as e:
            # Fallback if ministry programs model is not available
            context['programs'] = []
        
        # Prepare sector data for filters
        sectors = []
        for sector_code, sector_data in sector_mapping.items():
            count = len([p for p in formatted_programs if self._get_program_sector(
                p.get('ministry', '').lower().replace(' ', '').replace('&', '').replace('.', ''), 
                sector_mapping
            ) and self._get_program_sector(
                p.get('ministry', '').lower().replace(' ', '').replace('&', '').replace('.', ''), 
                sector_mapping
            )['code'] == sector_code])
            if count > 0:  # Only include sectors with programs
                sectors.append({
                    'code': sector_code,
                    'name': sector_data['name'],
                    'icon': sector_data['icon'],
                    'color': sector_data['color'],
                    'count': count
                })

        # Enhanced filtering and sorting context
        context['sectors'] = sectors
        context['current_sector'] = current_sector
        context['current_sort'] = current_sort
        context['total_programs'] = len(context['programs'])
        
        # Program statistics
        context['program_stats'] = {
            'total': len(context['programs']),
            'active': sum(1 for p in context['programs'] if 'Active' in p['status']),
            'featured': sum(1 for p in context['programs'] if p['is_featured']),
        }
        
        # URL for empty state template
        from django.urls import reverse
        context['programs_url'] = reverse('programs')
        
        # Legacy accessible_programs for backward compatibility
        context['accessible_programs'] = context['programs'][:12]
        
        # Program categories for accessible ministry programs
        context['program_categories'] = [
            {
                'name': 'Labor & Employment',
                'code': 'MOLE',
                'icon': 'fas fa-briefcase',
                'description': 'Job placement, skills training, and livelihood programs',
                'color': 'blue'
            },
            {
                'name': 'Health Services',
                'code': 'MOH',
                'icon': 'fas fa-heartbeat',
                'description': 'Healthcare assistance and medical support programs',
                'color': 'red'
            },
            {
                'name': 'Social Services',
                'code': 'MSSD',
                'icon': 'fas fa-hands-helping',
                'description': 'Social assistance and community development programs',
                'color': 'green'
            },
            {
                'name': 'Public Works',
                'code': 'MPWH',
                'icon': 'fas fa-hammer',
                'description': 'Infrastructure and construction-related programs',
                'color': 'orange'
            },
            {
                'name': 'Education',
                'code': 'MBHTE',
                'icon': 'fas fa-graduation-cap',
                'description': 'Educational assistance and scholarship programs',
                'color': 'purple'
            },
            {
                'name': 'Agriculture',
                'code': 'MAFAR',
                'icon': 'fas fa-seedling',
                'description': 'Agricultural development and farming support programs',
                'color': 'teal'
            }
        ]
        
        # Add contact form for program inquiries
        context['contact_form'] = ContactForm(default_subject='ministry_program_inquiry')
        
        return context
    
    def _get_sector_mapping(self):
        """Define sector to ministry mapping with visual attributes."""
        return {
            'health': {
                'name': 'Health',
                'description': 'Healthcare services, medical programs, and public health initiatives.',
                'icon': 'fas fa-heartbeat',
                'color': 'green',
                'ministries': ['moh', 'MOH']
            },
            'education': {
                'name': 'Education',
                'description': 'Educational programs, training initiatives, and skills development.',
                'icon': 'fas fa-graduation-cap',
                'color': 'blue',
                'ministries': ['mbasiced', 'mhe', 'MOE', 'TESDA']
            },
            'agriculture': {
                'name': 'Agriculture',
                'description': 'Agricultural development, fisheries support, and agrarian reform programs.',
                'icon': 'fas fa-seedling',
                'color': 'green',
                'ministries': ['mafar', 'MAFAR']
            },
            'social_services': {
                'name': 'Social Services',
                'description': 'Social protection, welfare programs, and support for vulnerable populations.',
                'icon': 'fas fa-hands-helping',
                'color': 'purple',
                'ministries': ['mssd', 'MSSD']
            },
            'infrastructure': {
                'name': 'Infrastructure',
                'description': 'Public works, transportation networks, and infrastructure development projects.',
                'icon': 'fas fa-road',
                'color': 'orange',
                'ministries': ['mpwh', 'MPWH', 'motc', 'MOTC']
            },
            'economic_development': {
                'name': 'Economic Development',
                'description': 'Trade promotion, industry development, tourism, and employment opportunities.',
                'icon': 'fas fa-chart-line',
                'color': 'indigo',
                'ministries': ['mtit', 'MTIT', 'mle', 'MLE']
            }
        }
    
    def _get_program_sector(self, ministry_code, sector_mapping):
        """Get sector information for a given ministry code."""
        for sector_code, sector_data in sector_mapping.items():
            if ministry_code in sector_data['ministries']:
                return {
                    'code': sector_code,
                    'name': sector_data['name'],
                    'icon': sector_data['icon'],
                    'color': sector_data['color']
                }
        return None
    
    def post(self, request, *args, **kwargs):
        # Process contact form submission for ministry program inquiries
        contact_form = ContactForm(request.POST, default_subject='ministry_program_inquiry')
        
        if contact_form.is_valid():
            # Save the contact form submission
            submission = contact_form.save(commit=False)
            submission.form_source = 'accessible_ministry_programs_page'
            submission.save()
            
            context = self.get_context_data(**kwargs)
            context['message'] = 'Thank you for your ministry program inquiry. Our staff will assist you with program access and applications.'
            context['message_type'] = 'success'
            context['contact_form'] = ContactForm(default_subject='ministry_program_inquiry')  # Fresh form
            return render(request, self.template_name, context)
        else:
            # Form has errors
            context = self.get_context_data(**kwargs)
            context['contact_form'] = contact_form
            context['message'] = 'Please correct the errors below.'
            context['message_type'] = 'error'
            return render(request, self.template_name, context)


class DatabasePartnersView(TemplateView):
    """Database of Partners view - for authorized users only."""
    template_name = 'core/database_partners.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Check if user has appropriate role
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Page title and metadata
        context['title'] = 'Database of Partners'
        
        # Get filter parameters
        current_filters = {
            'search': self.request.GET.get('search', ''),
            'partner_type': self.request.GET.get('partner_type', ''),
            'status': self.request.GET.get('status', ''),
            'sector_focus': self.request.GET.get('sector_focus', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'sort_by': self.request.GET.get('sort_by', '-submitted_at'),
        }
        context['current_filters'] = current_filters
        
        # Get partnership submissions from the database
        partners = PartnershipSubmission.objects.all()
        
        # Apply filters
        if current_filters['search']:
            partners = partners.filter(
                Q(organization_name__icontains=current_filters['search']) |
                Q(contact_person__icontains=current_filters['search']) |
                Q(email__icontains=current_filters['search'])
            )
        
        if current_filters['partner_type']:
            partners = partners.filter(partnership_type=current_filters['partner_type'])
        
        if current_filters['status']:
            partners = partners.filter(status=current_filters['status'])
        
        if current_filters['date_from']:
            partners = partners.filter(submitted_at__date__gte=current_filters['date_from'])
        
        # Apply sorting
        if current_filters['sort_by']:
            partners = partners.order_by(current_filters['sort_by'])
        
        # Statistics
        context['total_partners'] = partners.count()
        context['active_count'] = partners.filter(status='approved').count()
        context['pending_count'] = partners.filter(status='new').count()
        
        # This month's count
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['this_month_count'] = partners.filter(submitted_at__gte=first_day_of_month).count()
        
        # Paginate results
        context['partners'] = partners
        
        # User permissions
        context['user_role'] = self.request.user.user_type if hasattr(self.request.user, 'user_type') else 'superuser'
        context['can_export'] = self.request.user.is_superuser or context['user_role'] in ['mp', 'chief_of_staff']
        
        return context


class DatabaseStaffView(TemplateView):
    """Database of Staff view - for authorized users only."""
    template_name = 'core/database_staff.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Check if user has appropriate role
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Page title and metadata
        context['title'] = 'Database of Staff'
        
        # Get filter parameters
        current_filters = {
            'search': self.request.GET.get('search', ''),
            'division': self.request.GET.get('division', ''),
            'employment_status': self.request.GET.get('employment_status', ''),
            'status': self.request.GET.get('status', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'sort_by': self.request.GET.get('sort_by', '-date_hired'),
        }
        context['current_filters'] = current_filters
        
        # Import Staff model
        from apps.staff.models import Staff
        
        # Get staff members from the database
        staff_members = Staff.objects.filter(is_active=True)
        
        # Apply filters
        if current_filters['search']:
            staff_members = staff_members.filter(
                Q(full_name__icontains=current_filters['search']) |
                Q(email__icontains=current_filters['search']) |
                Q(position__icontains=current_filters['search']) |
                Q(phone_number__icontains=current_filters['search'])
            )
        
        if current_filters['division']:
            staff_members = staff_members.filter(division=current_filters['division'])
        
        if current_filters['employment_status']:
            staff_members = staff_members.filter(employment_status=current_filters['employment_status'])
        
        if current_filters['status']:
            # Convert status filter to is_active field
            if current_filters['status'] == 'active':
                staff_members = staff_members.filter(is_active=True)
            elif current_filters['status'] == 'inactive':
                staff_members = staff_members.filter(is_active=False)
        
        if current_filters['date_from']:
            staff_members = staff_members.filter(date_hired__gte=current_filters['date_from'])
        
        if current_filters['date_to']:
            staff_members = staff_members.filter(date_hired__lte=current_filters['date_to'])
        
        # Apply sorting
        if current_filters['sort_by']:
            staff_members = staff_members.order_by(current_filters['sort_by'])
        
        # Statistics
        context['total_staff'] = staff_members.count()
        context['active_count'] = staff_members.filter(is_active=True).count()
        context['contractual_count'] = staff_members.filter(employment_status='contractual').count()
        context['coterminous_count'] = staff_members.filter(employment_status='coterminous').count()
        
        # This month's hires
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['this_month_count'] = staff_members.filter(date_hired__gte=first_day_of_month).count()
        
        # Recent hires (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        context['recent_hires_count'] = staff_members.filter(date_hired__gte=thirty_days_ago).count()
        
        # Paginate results
        context['staff_members'] = staff_members
        
        # User permissions
        context['user_role'] = self.request.user.user_type if hasattr(self.request.user, 'user_type') else 'superuser'
        context['can_export'] = self.request.user.is_superuser or context['user_role'] in ['mp', 'chief_of_staff']
        
        # Division choices for filter
        context['division_choices'] = [
            ('legislative_affairs', 'Legislative Affairs'),
            ('administrative_affairs', 'Administrative Affairs'),
            ('communications', 'Communications'),
            ('it_unit', 'IT Unit'),
            ('mp_office', "MP Uy-Oyod's Office"),
        ]
        
        # Employment status choices for filter
        context['employment_status_choices'] = [
            ('contractual', 'Contractual'),
            ('coterminous', 'Coterminous'),
            ('consultant', 'Consultant'),
            ('intern', 'Intern'),
            ('volunteer', 'Volunteer'),
        ]
        
        # Status choices for filter (based on is_active field)
        context['status_choices'] = [
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ]
        
        return context


class DatabaseDonorsView(TemplateView):
    """Database of Donors view - for authorized users only."""
    template_name = 'core/database_donors.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Check if user has appropriate role
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Page title and metadata
        context['title'] = 'Database of Donors'
        
        # Get filter parameters
        current_filters = {
            'search': self.request.GET.get('search', ''),
            'donor_type': self.request.GET.get('donor_type', ''),
            'contribution_type': self.request.GET.get('contribution_type', ''),
            'status': self.request.GET.get('status', ''),
            'amount_range': self.request.GET.get('amount_range', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'sort_by': self.request.GET.get('sort_by', '-submitted_at'),
        }
        context['current_filters'] = current_filters
        
        # Get donation submissions from the database
        donors = DonationSubmission.objects.all()
        
        # Apply filters
        if current_filters['search']:
            donors = donors.filter(
                Q(donor_name__icontains=current_filters['search']) |
                Q(email__icontains=current_filters['search'])
            )
        
        if current_filters['donor_type']:
            donors = donors.filter(donor_type=current_filters['donor_type'])
        
        if current_filters['contribution_type']:
            donors = donors.filter(donation_type=current_filters['contribution_type'])
        
        if current_filters['status']:
            donors = donors.filter(status=current_filters['status'])
        
        if current_filters['date_from']:
            donors = donors.filter(submitted_at__date__gte=current_filters['date_from'])
        
        if current_filters['date_to']:
            donors = donors.filter(submitted_at__date__lte=current_filters['date_to'])
        
        # Apply sorting
        if current_filters['sort_by']:
            donors = donors.order_by(current_filters['sort_by'])
        
        # Statistics
        context['total_donors'] = donors.count()
        context['active_donors'] = donors.filter(status='completed').count()
        
        # Calculate total amount
        from django.db.models import Sum
        total_amount = donors.aggregate(total=Sum('amount'))['total'] or 0
        context['total_amount'] = total_amount
        
        # This month's amount
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['this_month_amount'] = donors.filter(
            submitted_at__gte=first_day_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Paginate results
        context['donors'] = donors
        
        # User permissions
        context['user_role'] = self.request.user.user_type if hasattr(self.request.user, 'user_type') else 'superuser'
        context['can_export'] = self.request.user.is_superuser or context['user_role'] in ['mp', 'chief_of_staff']
        
        return context


class DatabaseUpdatesView(ListView):
    """Database of Updates view - for Information Officers, Coordinators, and System Admin."""
    model = Announcement
    template_name = 'core/database_updates.html'
    context_object_name = 'announcements'
    paginate_by = 20
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Check if user has appropriate role
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator', 'information_officer']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Announcement.objects.all()
        
        # Apply filters
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search)
            )
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        is_featured = self.request.GET.get('is_featured')
        if is_featured == 'yes':
            queryset = queryset.filter(is_featured=True)
        elif is_featured == 'no':
            queryset = queryset.filter(is_featured=False)
        
        created_by = self.request.GET.get('created_by')
        if created_by:
            queryset = queryset.filter(created_by__id=created_by)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', '-published_date')
        if sort_by:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        announcements = Announcement.objects.all()
        context['total_announcements'] = announcements.count()
        context['published_count'] = announcements.filter(status='published').count()
        context['draft_count'] = announcements.filter(status='draft').count()
        context['featured_count'] = announcements.filter(is_featured=True).count()
        
        # This month's announcements
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['this_month_count'] = announcements.filter(created_at__gte=first_day_of_month).count()
        
        # Filter parameters for template
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'status': self.request.GET.get('status', ''),
            'is_featured': self.request.GET.get('is_featured', ''),
            'created_by': self.request.GET.get('created_by', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'sort_by': self.request.GET.get('sort_by', '-published_date'),
        }
        
        # Preserve filter parameters in pagination links
        filter_params = ''
        for key, value in self.request.GET.items():
            if key != 'page' and value:
                filter_params += f'&{key}={value}'
        context['filter_params'] = filter_params
        
        # Get authors for filter dropdown
        from django.contrib.auth import get_user_model
        User = get_user_model()
        context['authors'] = User.objects.filter(announcements_created__isnull=False).distinct()
        
        return context


class DatabaseAnnouncementCreateView(CreateView):
    """Create new announcement view."""
    model = Announcement
    template_name = 'core/database_announcement_form.html'
    fields = ['title', 'category', 'status', 'excerpt', 'content', 'image', 'is_featured']
    success_url = reverse_lazy('database_updates')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Check if user has appropriate role
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator', 'information_officer']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        
        # Set published date if status is published
        if form.instance.status == 'published' and not form.instance.published_date:
            form.instance.published_date = timezone.now()
        
        response = super().form_valid(form)
        messages.success(self.request, "Announcement created successfully!")
        return response

class DatabaseAnnouncementUpdateView(UpdateView):
    """Update existing announcement view."""
    model = Announcement
    template_name = 'core/database_announcement_form.html'
    fields = ['title', 'category', 'status', 'excerpt', 'content', 'image', 'is_featured']
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Check if user has appropriate role
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator', 'information_officer']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        # Set published date if status is published and it's not already set
        if form.instance.status == 'published' and not form.instance.published_date:
            form.instance.published_date = timezone.now()
        
        response = super().form_valid(form)
        messages.success(self.request, "Announcement updated successfully!")
        return response
    
    def get_success_url(self):
        return reverse_lazy('database_updates')

class DatabaseAnnouncementDeleteView(DeleteView):
    """Delete announcement view."""
    model = Announcement
    template_name = 'core/database_announcement_confirm_delete.html' # Create this template
    success_url = reverse_lazy('database_updates')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Check if user has appropriate role
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator', 'information_officer']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Announcement deleted successfully!")
        return response

class DatabaseContactMessagesView(LoginRequiredMixin, ListView):
    """
    Displays a list of contact form submissions for authorized users.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    model = ContactFormSubmission
    template_name = 'core/database_contact_messages.html'
    context_object_name = 'messages'
    paginate_by = 10
    login_url = reverse_lazy('login')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            messages.error(self.request, "You do not have permission to access this page.")
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = ContactFormSubmission.objects.all().order_by('-submitted_at')

        # Apply filters
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(message__icontains=search_query)
            )
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        source_filter = self.request.GET.get('source')
        if source_filter:
            queryset = queryset.filter(form_source=source_filter)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(submitted_at__date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(submitted_at__date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contact Messages Database'
        
        # Statistics
        total_messages = ContactFormSubmission.objects.count()
        new_messages = ContactFormSubmission.objects.filter(status='new').count()
        replied_messages = ContactFormSubmission.objects.filter(status='replied').count()
        
        context['total_messages'] = total_messages
        context['new_messages'] = new_messages
        context['replied_messages'] = replied_messages
        
        # Filter options for template
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'source': self.request.GET.get('source', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        
        # Status choices (assuming these are defined in your ContactFormSubmission model)
        context['status_choices'] = ContactFormSubmission.STATUS_CHOICES if hasattr(ContactFormSubmission, 'STATUS_CHOICES') else []
        
        # Form source choices (assuming these are defined in your ContactFormSubmission model)
        context['source_choices'] = ContactFormSubmission.FORM_SOURCE_CHOICES if hasattr(ContactFormSubmission, 'FORM_SOURCE_CHOICES') else []

        return context

class DatabaseContactMessageDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a single contact form submission.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    model = ContactFormSubmission
    template_name = 'core/database_contact_message_detail.html'
    context_object_name = 'message'
    pk_url_kwarg = 'pk' # Assuming primary key is used in URL

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            messages.error(self.request, "You do not have permission to access this page.")
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Mark message as 'read' if it's 'new'
        if obj.status == 'new':
            obj.status = 'read'
            obj.read_at = timezone.now()
            obj.save(update_fields=['status', 'read_at'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contact Message Details'
        return context

class ReplyToContactMessageView(LoginRequiredMixin, CreateView):
    """
    Allows authorized staff to compose and send an internal reply to a ContactFormSubmission.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    model = CommunicationMessage
    form_class = MessageComposeForm
    template_name = 'core/reply_contact_message_form.html' # New template for the reply form
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            messages.error(self.request, "You do not have permission to access this page.")
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        contact_submission = get_object_or_404(ContactFormSubmission, pk=self.kwargs['pk'])
        
        # Attempt to find a User object associated with the contact submission's email
        # This assumes that users in the system might have the same email as contact form submitters
        recipient_user = User.objects.filter(email=contact_submission.email).first()
        
        initial['recipient'] = recipient_user.pk if recipient_user else None
        initial['subject'] = f"Re: {contact_submission.subject} (Ref: #{contact_submission.pk})"
        # Format the datetime object using Python's strftime
        formatted_date = contact_submission.submitted_at.strftime('%B %d, %Y %H:%M')
        initial['content'] = f"\n\n--- Original Message ---\nFrom: {contact_submission.get_full_name()} <{contact_submission.email}>\nSubject: {contact_submission.subject}\nDate: {formatted_date}\n\n{contact_submission.message}"
        initial['message_type'] = 'email' # Default to email
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contact_submission = get_object_or_404(ContactFormSubmission, pk=self.kwargs['pk'])
        context['title'] = f"Reply to {contact_submission.get_full_name()}"
        context['contact_submission'] = contact_submission
        return context

    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = self.request.user # Assuming sender is the logged-in staff
        
        # Ensure recipient is a valid User object
        if not message.recipient:
            messages.error(self.request, "Could not find a registered user for this email. Please ensure the recipient is a registered user.")
            return self.form_invalid(form)

        message.save()
        
        # Trigger sending the message (assuming send_single_message handles actual email sending)
        from apps.communications.tasks import send_single_message
        send_single_message.delay(message.id)
        
        # Mark the original contact submission as replied
        contact_submission = get_object_or_404(ContactFormSubmission, pk=self.kwargs['pk'])
        contact_submission.status = 'replied'
        contact_submission.replied_at = timezone.now()
        contact_submission.save(update_fields=['status', 'replied_at'])
        
        messages.success(self.request, f"Reply sent to {contact_submission.get_full_name()} and message marked as replied.")
        return redirect(reverse('database_contact_message_detail', kwargs={'pk': contact_submission.pk}))

class MarkMessageReadView(LoginRequiredMixin, View):
    """
    Marks a contact message as 'read' via AJAX.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        return super().dispatch(*args, **kwargs)

    def post(self, request, pk):
        message = get_object_or_404(ContactFormSubmission, pk=pk)
        if message.status == 'new':
            message.status = 'read'
            message.read_at = timezone.now()
            message.save(update_fields=['status', 'read_at'])
            return JsonResponse({'success': True, 'status': 'read'})
        return JsonResponse({'success': False, 'status': message.status})

class MarkMessageRepliedView(LoginRequiredMixin, View):
    """
    Marks a contact message as 'replied' via AJAX.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        return super().dispatch(*args, **kwargs)

    def post(self, request, pk):
        message = get_object_or_404(ContactFormSubmission, pk=pk)
        if message.status in ['new', 'read', 'in_progress']:
            message.status = 'replied'
            message.replied_at = timezone.now()
            message.save(update_fields=['status', 'replied_at'])
            return JsonResponse({'success': True, 'status': 'replied'})
        return JsonResponse({'success': False, 'status': message.status})

class DatabaseContactMessageDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deletes a contact message.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    model = ContactFormSubmission
    template_name = 'core/database_contact_message_confirm_delete.html' # Create this template
    success_url = reverse_lazy('database_contact_messages')
    pk_url_kwarg = 'pk'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            messages.error(self.request, "You do not have permission to perform this action.")
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Contact message deleted successfully.")
        return super().form_valid(form)

class DatabaseContactMessagesExportView(LoginRequiredMixin, View):
    """
    Exports contact messages to a CSV file.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            messages.error(self.request, "You do not have permission to export data.")
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_messages.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Subject', 'Message', 'Status', 'Form Source', 'Submitted At'])

        messages = ContactFormSubmission.objects.all().order_by('-submitted_at')
        for message in messages:
            writer.writerow([
                message.id,
                message.name,
                message.email,
                message.subject,
                message.message,
                message.status,
                message.form_source,
                message.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        return response

# Placeholder views for missing views in urls.py
class DatabaseStaffCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html' # You might want to create a proper template for this
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Staff (Placeholder)'
        return context

class DatabaseStaffEditView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Staff (Placeholder)'
        return context

class DatabaseStaffDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Staff (Placeholder)'
        return context

class DatabasePPAsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/database_ppas.html'
    login_url = reverse_lazy('login')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        logger.info(f"User {self.request.user.username} attempting to access Database of PPAs")
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                hasattr(self.request.user, 'user_type') and 
                self.request.user.user_type in allowed_roles):
            logger.warning(f"Unauthorized access attempt to Database of PPAs by user {self.request.user.username}")
            messages.error(self.request, "You do not have permission to access the Database of PPAs.")
            return redirect('home')
        logger.info(f"User {self.request.user.username} granted access to Database of PPAs")
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Database of PPAs'
        
        # Determine if the user can edit/add/delete PPAs
        # Temporarily setting can_edit to True for demonstration purposes
        context['can_edit'] = True
        
        # Get all non-deleted PPAs
        ppas = MinistryProgram.objects.filter(is_deleted=False)

        # Apply filters
        current_filters = {
            'search': self.request.GET.get('search', ''),
            'ministry': self.request.GET.get('ministry', ''),
            'ppa_type': self.request.GET.get('ppa_type', ''),
            'program_source': self.request.GET.get('program_source', ''),
            'status': self.request.GET.get('status', ''),
            'priority': self.request.GET.get('priority', ''),
            'budget_range': self.request.GET.get('budget_range', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'sort_by': self.request.GET.get('sort_by', '-created_at'),
        }
        context['current_filters'] = current_filters

        if current_filters['search']:
            ppas = ppas.filter(Q(title__icontains=current_filters['search']) | Q(description__icontains=current_filters['search']))
        if current_filters['ministry']:
            ppas = ppas.filter(ministry=current_filters['ministry'])
        if current_filters['ppa_type']:
            ppas = ppas.filter(ppa_type=current_filters['ppa_type'])
        if current_filters['program_source']:
            ppas = ppas.filter(program_source=current_filters['program_source'])
        if current_filters['status']:
            ppas = ppas.filter(status=current_filters['status'])
        if current_filters['priority']:
            ppas = ppas.filter(priority_level=current_filters['priority'])
        if current_filters['date_from']:
            ppas = ppas.filter(start_date__gte=current_filters['date_from'])
        if current_filters['date_to']:
            ppas = ppas.filter(end_date__lte=current_filters['date_to'])
        
        # Sorting
        ppas = ppas.order_by(current_filters['sort_by'])

        # Statistics
        context['total_ppas'] = ppas.count()
        context['active_count'] = ppas.filter(status='active').count()
        context['planning_count'] = ppas.filter(status='draft').count()
        context['this_year_count'] = ppas.filter(start_date__year=timezone.now().year).count()
        total_budget = ppas.aggregate(Sum('total_budget'))['total_budget__sum'] or 0
        context['total_budget_display'] = f"₱{total_budget:,.2f}"

        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(ppas, 20) # Show 20 PPAs per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Add display values to each PPA object
        for ppa in page_obj:
            ppa.budget_display = f"₱{ppa.total_budget:,.2f}" if ppa.total_budget else "TBD"
            ppa.ministry_display = ppa.get_ministry_display()
            ppa.status_display = ppa.get_status_display()
            ppa.priority_display = ppa.get_priority_level_display()
            ppa.ppa_type_display = ppa.get_ppa_type_display()
            ppa.program_source_display = ppa.get_program_source_display()

        context['ppas'] = page_obj

        # Provide choices for filters in the modal/form
        context['ministry_choices'] = MinistryProgram.MINISTRIES
        context['ppa_type_choices'] = MinistryProgram.PPA_TYPES
        context['program_source_choices'] = MinistryProgram.PROGRAM_SOURCES
        context['status_choices'] = MinistryProgram.STATUS_CHOICES
        context['priority_choices'] = MinistryProgram.PRIORITY_LEVELS
        context['funding_sources_choices'] = MinistryProgram.FUNDING_SOURCES
        
        # Placeholder for current_filters to avoid errors
        context['current_filters'] = {
            'search': '', 'ministry': '', 'ppa_type': '', 'program_source': '',
            'status': '', 'priority': '', 'budget_range': '', 'date_from': '',
            'date_to': '', 'sort_by': '-created_at',
        }
        
        # Placeholder for budget ranges (if needed for filter dropdown)
        context['budget_ranges'] = [
            ('0-100000', '₱0 - ₱100K'),
            ('100001-1000000', '₱100K - ₱1M'),
            ('1000001-10000000', '₱1M - ₱10M'),
            ('10000001-100000000', '₱10M - ₱100M'),
            ('100000001-1000000000', '₱100M - ₱1B'),
            ('1000000001-above', '₱1B+'),
        ]
        
        return context
    
    def post(self, request, *args, **kwargs):
        from apps.services.forms import MinistryProgramForm # Import the form
        
        action = request.POST.get('action')
        ppa_id = request.POST.get('ppa_id')
        
        if action == 'create':
            form = MinistryProgramForm(request.POST)
        elif action == 'update':
            try:
                instance = MinistryProgram.objects.get(id=ppa_id)
                form = MinistryProgramForm(request.POST, instance=instance)
            except MinistryProgram.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'PPA not found for update.'}, status=404)
        elif action == 'delete':
            try:
                instance = MinistryProgram.objects.get(id=ppa_id)
                instance.is_deleted = True # Soft delete
                instance.save()
                messages.success(request, f"PPA '{instance.title}' marked as deleted successfully.")
                return JsonResponse({'success': True, 'message': 'PPA deleted successfully.'})
            except MinistryProgram.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'PPA not found for deletion.'}, status=404)
            except Exception as e:
                logger.error(f"Error deleting PPA {ppa_id}: {e}")
                return JsonResponse({'success': False, 'error': f'An error occurred during deletion: {e}'}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action.'}, status=400)

        if form.is_valid():
            ppa = form.save(commit=False)
            # Set created_by for new PPAs
            if action == 'create':
                ppa.created_by = request.user
            ppa.save()
            messages.success(request, f"PPA '{ppa.title}' saved successfully.")
            return JsonResponse({'success': True, 'message': 'PPA saved successfully.', 'ppa_id': ppa.id})
        else:
            # Log form errors for debugging
            logger.error(f"PPA Form Errors: {form.errors.as_json()}")
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)


class TDIFProjectDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'TDIF Project Detail (Placeholder)'
        return context

@login_required
def faqs_view(request):
    return render(request, 'core/placeholder.html', {'title': 'FAQs (Placeholder)'})

@login_required
def health_check(request):
    return JsonResponse({'status': 'ok'})

@login_required
def health_detailed(request):
    return JsonResponse({'status': 'ok', 'details': 'All systems operational'})

@login_required
def readiness_check(request):
    return JsonResponse({'status': 'ready'})

@login_required
def metrics_endpoint(request):
    return JsonResponse({'metrics': 'data'})

@login_required
def test_icons(request):
    return render(request, 'core/placeholder.html', {'title': 'Test Icons (Placeholder)'})

@login_required
def test_radio(request):
    return render(request, 'core/placeholder.html', {'title': 'Test Radio (Placeholder)'})

@login_required
def csrf_debug(request):
    return render(request, 'core/placeholder.html', {'title': 'CSRF Debug (Placeholder)'})

@login_required
def monitoring_dashboard(request):
    return render(request, 'core/placeholder.html', {'title': 'Monitoring Dashboard (Placeholder)'})

class ChapterRequestDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chapter Request Detail (Placeholder)'
        return context

class ChapterRequestUpdateStatusView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chapter Request Update Status (Placeholder)'
        return context

class ChapterRequestAssignView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chapter Request Assign (Placeholder)'
        return context

class ChapterRequestDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chapter Request Delete (Placeholder)'
        return context

class ChapterRequestNotesView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chapter Request Notes (Placeholder)'
        return context

class StaffApplicationListView(LoginRequiredMixin, TemplateView):
    template_name = 'core/placeholder.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Staff Application List (Placeholder)'
        return context

User = get_user_model() # Get the active User model

class DatabaseMembersView(LoginRequiredMixin, TemplateView):
    """
    Displays a list of FahanieCares members for authorized users.
    Accessible to Superuser, MP, Chief of Staff, Admin, and Coordinator roles.
    """
    template_name = 'core/database_members.html'
    login_url = reverse_lazy('login')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        allowed_roles = ['superuser', 'mp', 'chief_of_staff', 'admin', 'coordinator']
        if not (self.request.user.is_superuser or 
                (hasattr(self.request.user, 'user_type') and self.request.user.user_type in allowed_roles)):
            messages.error(self.request, "You do not have permission to access this page.")
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Database of Members'

        # Get filter parameters
        current_filters = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'sex': self.request.GET.get('sex', ''),
            'sector': self.request.GET.get('sector', ''),
            'municipality': self.request.GET.get('municipality', ''),
            'chapter': self.request.GET.get('chapter', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'sort_by': self.request.GET.get('sort_by', '-created_at'),
        }
        context['current_filters'] = current_filters

        # Get members from the database
        members = FahanieCaresMember.objects.all()

        # Apply filters
        if current_filters['search']:
            members = members.filter(
                Q(first_name__icontains=current_filters['search']) |
                Q(last_name__icontains=current_filters['search']) |
                Q(email__icontains=current_filters['search']) |
                Q(contact_number__icontains=current_filters['search']) |
                Q(address_municipality__icontains=current_filters['search']) |
                Q(address_barangay__icontains=current_filters['search'])
            )
        
        if current_filters['status']:
            members = members.filter(status=current_filters['status'])
        
        if current_filters['sex']:
            members = members.filter(sex=current_filters['sex'])
        
        if current_filters['sector']:
            members = members.filter(sector=current_filters['sector'])
        
        if current_filters['municipality']:
            members = members.filter(address_municipality=current_filters['municipality'])
        
        if current_filters['chapter']:
            members = members.filter(assigned_chapter__id=current_filters['chapter'])
        
        if current_filters['date_from']:
            members = members.filter(created_at__date__gte=current_filters['date_from'])
        
        if current_filters['date_to']:
            members = members.filter(created_at__date__lte=current_filters['date_to'])

        # Apply sorting
        if current_filters['sort_by']:
            members = members.order_by(current_filters['sort_by'])

        # Statistics
        context['total_members'] = members.count()
        context['approved_members'] = members.filter(status='approved').count()
        context['pending_members'] = members.filter(status='pending').count()
        
        # This month's registrations
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['this_month_registrations'] = members.filter(created_at__gte=first_day_of_month).count()

        # Paginate results
        from django.core.paginator import Paginator
        paginator = Paginator(members, 20) # Show 20 members per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['members'] = page_obj

        # Filter options for template
        context['status_choices'] = FahanieCaresMember.STATUS_CHOICES if hasattr(FahanieCaresMember, 'STATUS_CHOICES') else []
        context['sex_choices'] = FahanieCaresMember.SEX_CHOICES if hasattr(FahanieCaresMember, 'SEX_CHOICES') else []
        context['sector_choices'] = FahanieCaresMember.SECTOR_CHOICES if hasattr(FahanieCaresMember, 'SECTOR_CHOICES') else []
        context['municipality_choices'] = FahanieCaresMember.MUNICIPALITY_CHOICES if hasattr(FahanieCaresMember, 'MUNICIPALITY_CHOICES') else []
        context['chapter_choices'] = Chapter.objects.all().order_by('name') # Assuming Chapter model is available

        return context

class MemberBulkRegistrationView(LoginRequiredMixin, TemplateView):
    template_name = 'core/bulk_member_registration.html'
    login_url = reverse_lazy('login')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Restrict access to superusers and admins
        allowed_roles = ['superuser', 'admin'] # Adjust roles as needed
        if not (self.request.user.is_superuser or
                (hasattr(self.request.user, 'user_type') and self.request.user.user_type in allowed_roles)):
            messages.error(self.request, "You do not have permission to access this page.")
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Bulk Member Registration'
        if self.request.POST:
            context['formset'] = FahanieCaresMemberFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = FahanieCaresMemberFormSet()
        return context

    def post(self, request, *args, **kwargs):
        formset = FahanieCaresMemberFormSet(request.POST, request.FILES)
        if formset.is_valid():
            registered_count = 0
            registered_members_info = [] # Initialize list to store info of successfully registered members

            with transaction.atomic():
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        try:
                            # Generate a unique username (e.g., from email or a random string)
                            username = form.cleaned_data['first_name'].lower() # Set username to first name
                            # Ensure username is unique
                            counter = 1
                            original_username = username
                            while User.objects.filter(username=username).exists():
                                username = f"{original_username}{counter}"
                                counter += 1

                            temp_password = 'fahaniecares123' # Set fixed password

                            # Create a new User instance
                            new_user = User.objects.create_user(
                                username=username,
                                email=form.cleaned_data['email'],
                                password=temp_password, # Set temporary password
                                first_name=form.cleaned_data['first_name'],
                                last_name=form.cleaned_data['last_name'],
                                user_type='member', # Assign 'member' user type
                                is_active=True # Automatically activate
                            )
                            new_user.save()

                            # Create FahanieCaresMember instance
                            member = form.save(commit=False)
                            member.user = new_user
                            # Use the status from the form, defaulting to 'pending' if not provided
                            member.status = form.cleaned_data.get('status', 'pending')
                            member.save() # The model's save method will generate the permanent member_id

                            registered_members_info.append({
                                'first_name': member.first_name,
                                'last_name': member.last_name,
                                'username': new_user.username,
                                'password': temp_password # Include password as requested
                            })
                            registered_count += 1
                        except ValidationError as e:
                            messages.error(request, f"Error registering {form.cleaned_data.get('first_name')} {form.cleaned_data.get('last_name')}: {e.message}")
                            # Re-render the formset with errors
                            context = self.get_context_data()
                            context['formset'] = formset
                            return self.render_to_response(context)
                        except Exception as e:
                            messages.error(request, f"An unexpected error occurred while registering a member: {e}")
                            # Re-render the formset with errors
                            context = self.get_context_data()
                            context['formset'] = formset
                            return self.render_to_response(context)

            if registered_count > 0:
                messages.success(request, f"{registered_count} members registered successfully and are now pending for approval.")
                context = self.get_context_data()
                context['registered_members_info'] = registered_members_info
                context['message'] = f"{registered_count} members registered successfully and are now pending for approval."
                context['message_type'] = 'success'
                return self.render_to_response(context)
            else:
                messages.info(request, "No new members were registered.")
                return redirect('database_members_list') # Still redirect if no new members
        else:
            messages.error(request, "Please correct the errors below.")
            context = self.get_context_data()
            context['formset'] = formset
            return self.render_to_response(context)
