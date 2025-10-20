# CREATE OR REPLACE admin.py in your Django app

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Job, Application, SiteContent
import csv
from django.http import HttpResponse


# ============================================
# JOB ADMIN
# ============================================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'salary', 'contract', 'expiry_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'location', 'created_at']
    search_fields = ['title', 'location', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'location', 'salary', 'contract', 'icon')
        }),
        ('Job Details', {
            'fields': ('description', 'responsibilities', 'requirements', 'benefits')
        }),
        ('Media', {
            'fields': ('workplace_photos',),
            'description': 'Upload workplace photos (optional)'
        }),
        ('Settings', {
            'fields': ('expiry_date', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


# ============================================
# APPLICATION ADMIN - This is the main one!
# ============================================

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'full_name',
        'job_title',
        'email',
        'phone',
        'age',
        'gender',
        'kcse_grade',
        'status_badge',
        'applied_at',
        'view_documents_button',
        'status'
    ]
    
    list_filter = [
        'status',
        'gender',
        'job_title',
        'applied_at',
        'kcse_grade'
    ]
    
    search_fields = [
        'full_name',
        'email',
        'phone',
        'job_title'
    ]
    
    list_editable = ['status']
    
    ordering = ['-applied_at']
    
    readonly_fields = [
        'job_id',
        'job_title',
        'applied_at',
        'view_cv',
        'view_id_document',
        'view_certificate',
        'view_additional_docs'
    ]
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job_id', 'job_title', 'applied_at', 'status')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone', 'age', 'gender', 'kcse_grade')
        }),
        ('Uploaded Documents', {
            'fields': ('view_cv', 'view_id_document', 'view_certificate', 'view_additional_docs'),
            'description': 'Click the links below to download documents'
        }),
        ('Admin Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_reviewed',
        'mark_as_shortlisted',
        'mark_as_rejected',
        'export_to_csv'
    ]
    
    # Custom display methods
    def status_badge(self, obj):
        """Show colored status badge"""
        colors = {
            'pending': '#FF9800',
            'reviewed': '#2196F3',
            'shortlisted': '#4CAF50',
            'rejected': '#f44336'
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; '
            'border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def view_documents_button(self, obj):
        """Button to view all documents"""
        if obj.cv_document or obj.id_document:
            return format_html(
                '<a class="button" href="#" onclick="alert(\'Scroll down to Documents section\'); '
                'return false;">📁 View Documents</a>'
            )
        return '—'
    view_documents_button.short_description = 'Documents'
    
    # Document download links
    def view_cv(self, obj):
        """Download link for CV"""
        if obj.cv_document:
            return format_html(
                '<a href="{}" target="_blank" class="button" '
                'style="background: #0a8a43; color: white; padding: 8px 15px; '
                'text-decoration: none; border-radius: 4px; display: inline-block;">'
                '📄 Download CV/Resume</a>',
                obj.cv_document.url
            )
        return format_html('<span style="color: #999;">Not uploaded</span>')
    view_cv.short_description = 'CV/Resume'
    
    def view_id_document(self, obj):
        """Download link for ID"""
        if obj.id_document:
            return format_html(
                '<a href="{}" target="_blank" class="button" '
                'style="background: #2196F3; color: white; padding: 8px 15px; '
                'text-decoration: none; border-radius: 4px; display: inline-block;">'
                '🪪 Download ID/Passport</a>',
                obj.id_document.url
            )
        return format_html('<span style="color: #999;">Not uploaded</span>')
    view_id_document.short_description = 'ID/Passport'
    
    def view_certificate(self, obj):
        """Download link for certificate"""
        if obj.certificate_document:
            return format_html(
                '<a href="{}" target="_blank" class="button" '
                'style="background: #FF9800; color: white; padding: 8px 15px; '
                'text-decoration: none; border-radius: 4px; display: inline-block;">'
                '📜 Download Certificate</a>',
                obj.certificate_document.url
            )
        return format_html('<span style="color: #999;">Optional - Not provided</span>')
    view_certificate.short_description = 'KCSE Certificate'
    
    def view_additional_docs(self, obj):
        """Download links for additional documents"""
        if obj.additional_documents:
            docs = obj.additional_documents.split(',')
            links = []
            for i, doc in enumerate(docs, 1):
                links.append(format_html(
                    '<a href="{}" target="_blank" class="button" '
                    'style="background: #9C27B0; color: white; padding: 8px 15px; '
                    'text-decoration: none; border-radius: 4px; display: inline-block; '
                    'margin-right: 5px; margin-bottom: 5px;">'
                    '📎 Document {}</a>',
                    doc.strip(), i
                ))
            return format_html('<div style="display: flex; flex-wrap: wrap; gap: 5px;">{}</div>', 
                             format_html(''.join(str(link) for link in links)))
        return format_html('<span style="color: #999;">None uploaded</span>')
    view_additional_docs.short_description = 'Additional Documents'
    
    # Bulk actions
    def mark_as_reviewed(self, request, queryset):
        """Mark selected applications as reviewed"""
        updated = queryset.update(status='reviewed')
        self.message_user(request, f'{updated} application(s) marked as reviewed.')
    mark_as_reviewed.short_description = '✅ Mark as Reviewed'
    
    def mark_as_shortlisted(self, request, queryset):
        """Mark selected applications as shortlisted"""
        updated = queryset.update(status='shortlisted')
        self.message_user(request, f'{updated} application(s) marked as shortlisted.')
    mark_as_shortlisted.short_description = '⭐ Mark as Shortlisted'
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected applications as rejected"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} application(s) marked as rejected.')
    mark_as_rejected.short_description = '❌ Mark as Rejected'
    
    def export_to_csv(self, request, queryset):
        """Export selected applications to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Job Title', 'Email', 'Phone', 'Age', 
            'Gender', 'KCSE Grade', 'Status', 'Applied Date'
        ])
        
        for app in queryset:
            writer.writerow([
                app.id,
                app.full_name,
                app.job_title,
                app.email,
                app.phone,
                app.age,
                app.gender,
                app.kcse_grade,
                app.status,
                app.applied_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_to_csv.short_description = '📥 Export to CSV'
    
    # Custom admin page title
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


# ============================================
# SITE CONTENT ADMIN
# ============================================

@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'contact_phone', 'updated_at']
    
    fieldsets = (
        ('Site Branding', {
            'fields': ('site_name', 'site_logo')
        }),
        ('Homepage Content', {
            'fields': ('hero_title', 'hero_subtitle', 'about_text')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one site content instance
        return not SiteContent.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False


# ============================================
# CUSTOMIZE ADMIN SITE
# ============================================

admin.site.site_header = "🌿 Green Tara Admin"
admin.site.site_title = "Green Tara Admin"
admin.site.index_title = "Job Management Dashboard"