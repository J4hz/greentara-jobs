from django.contrib import admin
from django.utils.html import format_html
from .models import Job, Application, SiteContent


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'salary', 'contract', 'status_badge', 'applications_count', 'created_at']
    list_filter = ['location', 'created_at', 'expiry_date', 'is_active']
    search_fields = ['title', 'location', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'applications_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'location', 'salary', 'contract', 'icon')
        }),
        ('Job Details', {
            'fields': ('description', 'responsibilities', 'requirements', 'benefits')
        }),
        ('Workplace', {
            'fields': ('workplace_photos',),
            'description': 'Upload workplace photos as JSON array of URLs'
        }),
        ('Status', {
            'fields': ('is_active', 'expiry_date', 'created_at')
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_expired:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Expired</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
        )
    status_badge.short_description = 'Status'
    
    def applications_count(self, obj):
        count = obj.applications.count()
        return format_html(
            '<strong style="color: #0a8a43;">{} application{}</strong>',
            count,
            's' if count != 1 else ''
        )
    applications_count.short_description = 'Applications Received'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'job_title', 'email', 'phone', 'age', 'gender', 'kcse_grade', 'applied_date']
    list_filter = ['gender', 'kcse_grade', 'applied_at', 'job__location']
    search_fields = ['full_name', 'email', 'phone', 'job_title', 'job__title']
    date_hierarchy = 'applied_at'
    readonly_fields = ['applied_at', 'job_link']
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Demographics', {
            'fields': ('age', 'gender', 'kcse_grade')
        }),
        ('Job Application', {
            'fields': ('job', 'job_title', 'job_link', 'applied_at')
        }),
        ('Documents', {
            'fields': ('documents',),
            'description': 'Uploaded documents and files'
        }),
    )
    
    def applied_date(self, obj):
        return obj.applied_at.strftime('%Y-%m-%d %H:%M')
    applied_date.short_description = 'Applied At'
    applied_date.admin_order_field = 'applied_at'
    
    def job_link(self, obj):
        if obj.job:
            url = f'/django-admin/jobs/job/{obj.job.id}/change/'
            return format_html('<a href="{}" target="_blank">View Job Details</a>', url)
        return '-'
    job_link.short_description = 'Job Details'
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('job')


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'updated_at']
    search_fields = ['key', 'value']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('key', 'value')
        }),
        ('Metadata', {
            'fields': ('updated_at',)
        }),
    )
    
    def value_preview(self, obj):
        """Show preview of value (first 50 characters)"""
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_preview.short_description = 'Value'
    
    def has_add_permission(self, request):
        """Allow adding new content items"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of core content items"""
        if obj and obj.key in ['site_name', 'hero_title', 'contact_email', 'contact_phone']:
            return False
        return True


# Customize admin site
admin.site.site_header = '🌿 Green Tara Administration'
admin.site.site_title = 'Green Tara Admin'
admin.site.index_title = 'Job Portal Management'