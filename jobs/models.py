from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

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
    expiry_date = models.DateField(blank=True, null=True)
    workplace_photos = models.JSONField(blank=True, null=True)  # Store as JSON array
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False


class Application(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    ]
    
    KCSE_CHOICES = [
        ('A', 'A'), ('A-', 'A-'), ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('D+', 'D+'), ('D', 'D'),
        ('D-', 'D-'), ('E', 'E'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    job_title = models.CharField(max_length=200)  # Store for historical reference
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    age = models.IntegerField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    kcse_grade = models.CharField(max_length=5, choices=KCSE_CHOICES)
    documents = models.JSONField(blank=True, null=True)  # Store file paths as JSON
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'email']  # Prevent duplicate applications
    
    def __str__(self):
        return f"{self.full_name} - {self.job_title}"


class SiteContent(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Content'
        verbose_name_plural = 'Site Content'
    
    def __str__(self):
        return self.key
    
    @classmethod
    def get_content(cls, key, default=''):
        """Helper method to get content by key"""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_content(cls, key, value):
        """Helper method to set content"""
        obj, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': value}
        )
        return obj