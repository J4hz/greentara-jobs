# The issue is you're saving the PATH string instead of the FILE object.
# Django's FileField expects a FILE object, not a string path.

# ============================================
# FIXED models.py - No duplicate fields
# ============================================

from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary = models.CharField(max_length=100)
    contract = models.CharField(max_length=100)
    icon = models.URLField(blank=True, null=True)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField()
    workplace_photos = models.JSONField(blank=True, null=True, default=list)
    expiry_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self):
        return f"{self.title} - {self.location}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic Info
    job_id = models.IntegerField()
    job_title = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=50)
    kcse_grade = models.CharField(max_length=10)
    
    # Documents
    cv_document = models.FileField(upload_to='applications/cv/', null=True, blank=True)
    id_document = models.FileField(upload_to='applications/id/', null=True, blank=True)
    certificate_document = models.FileField(upload_to='applications/certificates/', null=True, blank=True)
    additional_documents = models.TextField(null=True, blank=True)
    
    # Status and Notes
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    # Metadata (NO DUPLICATES)
    applied_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
    
    def __str__(self):
        return f"{self.full_name} - {self.job_title} ({self.status})"
    
    def get_additional_docs_list(self):
        """Return list of additional document paths"""
        if self.additional_documents:
            return [doc.strip() for doc in self.additional_documents.split(',')]
        return []


class SiteContent(models.Model):
    """Site content configuration"""
    site_name = models.CharField(max_length=200, default='Green Tara')
    site_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    hero_title = models.CharField(max_length=500, default='Connecting Kenyans to trusted job opportunities')
    hero_subtitle = models.TextField(default='Browse verified listings locally and in Qatar')
    about_text = models.TextField(default='Green Tara helps job seekers connect to verified opportunities')
    contact_email = models.EmailField(default='info@greentara.co.ke')
    contact_phone = models.CharField(max_length=50, default='+254 700 123 456')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Content'
        verbose_name_plural = 'Site Content'
    
    def __str__(self):
        return self.site_name


# ============================================
# THEME CUSTOMIZATION MODELS
# ============================================

class SiteSettings(models.Model):
    """
    Site theme and branding settings.
    Singleton model - only one instance should exist.
    """
    from django.core.validators import RegexValidator
    
    # Theme Colors (Hex color validator)
    color_validator = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='Enter a valid hex color (e.g., #1e40af)'
    )
    
    primary_color = models.CharField(
        max_length=7,
        default='#1e40af',
        validators=[color_validator],
        help_text='Main brand color (e.g., #1e40af for blue)'
    )
    
    primary_dark_color = models.CharField(
        max_length=7,
        default='#1e3a8a',
        validators=[color_validator],
        help_text='Darker shade of primary color for hovers'
    )
    
    background_color = models.CharField(
        max_length=7,
        default='#dbeafe',
        validators=[color_validator],
        help_text='Page background color'
    )
    
    header_background = models.CharField(
        max_length=7,
        default='#3b82f6',
        validators=[color_validator],
        help_text='Header and footer background color'
    )
    
    gradient_start = models.CharField(
        max_length=7,
        default='#2563eb',
        validators=[color_validator],
        help_text='Gradient start color (for buttons, modals)'
    )
    
    gradient_end = models.CharField(
        max_length=7,
        default='#1d4ed8',
        validators=[color_validator],
        help_text='Gradient end color'
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Site Theme Settings"
        verbose_name_plural = "Site Theme Settings"
    
    def __str__(self):
        return "Site Theme Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        if not self.pk and SiteSettings.objects.exists():
            existing = SiteSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def get_theme_dict(self):
        """Return theme colors as a dictionary for API responses"""
        return {
            'primary': self.primary_color,
            'primary_dark': self.primary_dark_color,
            'background': self.background_color,
            'header_bg': self.header_background,
            'gradient_start': self.gradient_start,
            'gradient_end': self.gradient_end,
        }


class ColorPreset(models.Model):
    """Pre-defined color schemes for quick theme switching"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    primary_color = models.CharField(max_length=7)
    primary_dark_color = models.CharField(max_length=7)
    background_color = models.CharField(max_length=7)
    header_background = models.CharField(max_length=7)
    gradient_start = models.CharField(max_length=7)
    gradient_end = models.CharField(max_length=7)
    
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Color Preset"
        verbose_name_plural = "Color Presets"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def apply_to_site(self):
        """Apply this preset to the main site settings"""
        settings = SiteSettings.get_settings()
        settings.primary_color = self.primary_color
        settings.primary_dark_color = self.primary_dark_color
        settings.background_color = self.background_color
        settings.header_background = self.header_background
        settings.gradient_start = self.gradient_start
        settings.gradient_end = self.gradient_end
        settings.save()
        
        # Mark this preset as active
        ColorPreset.objects.update(is_active=False)
        self.is_active = True
        self.save()
