from django.db import models


class Job(models.Model):
    """Job posting model"""
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary = models.CharField(max_length=100)
    contract = models.CharField(max_length=100)
    icon = models.URLField(blank=True, null=True)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField()
    workplace_photos = models.TextField(blank=True, null=True)  # JSON array of photo URLs
    expiry_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self):
        return f"{self.title} - {self.location}"


class Application(models.Model):
    """Job application model with file uploads"""
    
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
    additional_documents = models.TextField(null=True, blank=True)  # Comma-separated paths
    
    # Status & Notes
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text='Internal admin notes')
    
    # Metadata
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job_id', 'email']
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