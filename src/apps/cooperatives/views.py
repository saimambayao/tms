from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages # Import messages
from django.views.generic.edit import FormMixin
from .models import Cooperative, CooperativeMembership, CooperativeOfficer
from .forms import CooperativeRegistrationForm, CooperativeOfficerForm, BulkOfficerRegistrationForm, EnhancedOfficerRegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Public Views
class CooperativeListView(ListView):
    model = Cooperative
    template_name = 'cooperatives/cooperative_list.html'
    context_object_name = 'cooperatives'
    queryset = Cooperative.objects.filter(status='Active')

class CooperativeDetailView(DetailView):
    model = Cooperative
    template_name = 'cooperatives/cooperative_detail.html'
    context_object_name = 'cooperative'

# Staff/Admin Views
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class CooperativeRegistrationView(StaffRequiredMixin, CreateView):
    model = Cooperative
    form_class = CooperativeRegistrationForm
    template_name = 'cooperatives/cooperative_registration.html'
    success_url = reverse_lazy('cooperatives:cooperative-list')

    def form_valid(self, form):
        form.instance.registered_by = self.request.user
        form.instance.status = 'Pending' # Set status to Pending
        messages.success(self.request, "Cooperative registered successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

class CooperativeUpdateView(StaffRequiredMixin, UpdateView):
    model = Cooperative
    form_class = CooperativeRegistrationForm
    template_name = 'cooperatives/cooperative_registration.html'
    success_url = reverse_lazy('cooperatives:cooperative-dashboard')

class CooperativeDeleteView(StaffRequiredMixin, DeleteView):
    model = Cooperative
    template_name = 'cooperatives/cooperative_confirm_delete.html'
    success_url = reverse_lazy('cooperatives:cooperative-dashboard')

class CooperativeOfficerManagementView(StaffRequiredMixin, FormMixin, DetailView):
    model = Cooperative
    template_name = 'cooperatives/cooperative_officer_management.html'
    context_object_name = 'cooperative'
    form_class = CooperativeOfficerForm

    def get_success_url(self):
        return reverse('cooperatives:cooperative-officer-management', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['officers'] = CooperativeOfficer.objects.filter(cooperative=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        officer = form.save(commit=False)
        officer.cooperative = self.object
        officer.save()
        messages.success(self.request, "Officer added successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))

class BulkOfficerRegistrationView(StaffRequiredMixin, CreateView):
    form_class = BulkOfficerRegistrationForm
    template_name = 'cooperatives/bulk_officer_registration.html'
    success_url = reverse_lazy('cooperatives:cooperative-list')

class CooperativeDashboardView(StaffRequiredMixin, ListView):
    model = Cooperative
    template_name = 'cooperatives/cooperative_dashboard.html'
    context_object_name = 'cooperatives'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate statistics
        cooperatives = Cooperative.objects.all()

        # Total cooperatives
        context['total_cooperatives'] = cooperatives.count()

        # Active cooperatives
        context['active_cooperatives'] = cooperatives.filter(status='Active').count()

        # Total members (from cooperative memberships)
        from .models import CooperativeMembership
        context['total_members'] = CooperativeMembership.objects.filter(is_active=True).count()

        # Pending registrations (cooperatives with pending status)
        context['pending_registrations'] = cooperatives.filter(status='Pending').count()

        return context

class EnhancedOfficerRegistrationView(StaffRequiredMixin, FormMixin, DetailView):
    """
    View for registering a new FahanieCares member and making them a cooperative officer
    """
    model = Cooperative
    template_name = 'cooperatives/enhanced_officer_registration.html'
    context_object_name = 'cooperative'
    form_class = EnhancedOfficerRegistrationForm

    def get_success_url(self):
        return reverse('cooperatives:cooperative-officer-management', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        try:
            officer, member = form.save(cooperative=self.object, user=self.request.user)
            messages.success(
                self.request, 
                f"Successfully registered {member.get_full_name()} as a FahanieCares member and {officer.position} for {self.object.name}!"
            )
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error creating officer: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))

class CooperativeOfficerDeleteView(StaffRequiredMixin, DeleteView):
    model = CooperativeOfficer
    template_name = 'cooperatives/cooperative_confirm_delete.html'

    def get_object(self, queryset=None):
        cooperative_pk = self.kwargs.get('cooperative_pk')
        officer_pk = self.kwargs.get('officer_pk')
        return get_object_or_404(CooperativeOfficer, pk=officer_pk, cooperative__pk=cooperative_pk)

    def get_success_url(self):
        cooperative_pk = self.kwargs.get('cooperative_pk')
        messages.success(self.request, "Officer removed successfully!")
        return reverse_lazy('cooperatives:cooperative-officer-management', kwargs={'pk': cooperative_pk})

# API Views will be added later
