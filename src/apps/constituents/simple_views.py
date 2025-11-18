from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .simple_forms import SimpleMemberRegistrationForm


class SimpleMemberRegistrationView(CreateView):
    """
    Emergency simplified registration view
    """
    form_class = SimpleMemberRegistrationForm
    template_name = 'constituents/simple_registration.html'
    success_url = reverse_lazy('registration_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            'Your registration has been submitted successfully! '
            'You can complete your profile details after approval.'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Quick Registration - #FahanieCares'
        return context