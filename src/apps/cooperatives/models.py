from django.db import models
from django.contrib.auth import get_user_model
from apps.constituents.models import FahanieCaresMember

User = get_user_model()

class Cooperative(models.Model):
    COOPERATIVE_TYPE_CHOICES = [
        ('Agricultural', 'Agricultural'),
        ('Consumer', 'Consumer'),
        ('Credit', 'Credit'),
        ('Housing', 'Housing'),
        ('Transport', 'Transport'),
        ('Fishery', 'Fishery'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Dissolved', 'Dissolved'),
    ]

    name = models.CharField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    cooperative_type = models.CharField(max_length=50, choices=COOPERATIVE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    address = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    date_established = models.DateField()
    date_registered = models.DateField(blank=True, null=True)
    
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_cooperatives')
    
    description = models.TextField(blank=True, null=True)
    total_members = models.PositiveIntegerField(default=0)
    
    registration_certificate = models.FileField(upload_to='cooperatives/documents/', blank=True, null=True)
    articles_of_cooperation = models.FileField(upload_to='cooperatives/documents/', blank=True, null=True)
    bylaws = models.FileField(upload_to='cooperatives/documents/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CooperativeMembership(models.Model):
    POSITION_CHOICES = [
        ('President', 'President'),
        ('Vice President', 'Vice President'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Board Member', 'Board Member'),
        ('Regular Member', 'Regular Member'),
        ('Committee Chair', 'Committee Chair'),
        ('Committee Member', 'Committee Member'),
    ]

    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name='memberships')
    fahaniecares_member = models.ForeignKey(FahanieCaresMember, on_delete=models.CASCADE, related_name='cooperative_memberships')
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    
    date_joined = models.DateField()
    date_appointed = models.DateField(blank=True, null=True)
    term_start = models.DateField(blank=True, null=True)
    term_end = models.DateField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_founding_member = models.BooleanField(default=False)
    
    membership_number = models.CharField(max_length=50, blank=True, null=True)
    shares_owned = models.PositiveIntegerField(default=0)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cooperative', 'fahaniecares_member', 'position')

    def __str__(self):
        return f"{self.fahaniecares_member} - {self.position} at {self.cooperative}"

class CooperativeOfficer(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name='officers')
    fahaniecares_member = models.ForeignKey(FahanieCaresMember, on_delete=models.CASCADE, related_name='cooperative_officer_positions')
    position = models.CharField(max_length=50, choices=CooperativeMembership.POSITION_CHOICES)
    
    date_joined = models.DateField()
    date_appointed = models.DateField(blank=True, null=True)
    term_start = models.DateField(blank=True, null=True)
    term_end = models.DateField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cooperative', 'fahaniecares_member', 'position')

    def __str__(self):
        return f"{self.fahaniecares_member} - {self.position} (Officer) at {self.cooperative}"
