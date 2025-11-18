from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from .utils import safe_media_upload


class Announcement(models.Model):
    """
    News and announcements for the #FahanieCares platform
    """
    CATEGORY_CHOICES = (
        ('news', 'News'),
        ('event', 'Event'),
        ('parliament', 'Parliament'),
        ('program', 'Program'),
        ('update', 'Update'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=300, help_text="Brief description for listing pages")
    content = models.TextField(help_text="Full announcement content")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    image = models.ImageField(upload_to=safe_media_upload, null=True, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements_created'
    )
    published_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('announcement_detail', kwargs={'slug': self.slug})
    
    def get_category_color(self):
        """Return CSS class for category badge"""
        colors = {
            'news': 'info',
            'event': 'warning', 
            'parliament': 'success',
            'program': 'primary',
            'update': 'secondary',
        }
        return colors.get(self.category, 'primary')


class ContactFormSubmission(models.Model):
    """
    Model to store submissions from the contact form.
    """
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Form Submission'
        verbose_name_plural = 'Contact Form Submissions'

    def __str__(self):
        return f"Message from {self.sender_name} - {self.subject}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def mark_as_replied(self):
        if not self.is_replied:
            self.is_replied = True
            self.replied_at = timezone.now()
            self.save()
