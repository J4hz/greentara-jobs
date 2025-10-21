from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Serve HTML pages
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('dashboard/', TemplateView.as_view(template_name='admin.html'), name='admin_page'),
    
    # Health check
    path('api/health', views.health_check, name='health'),
    
    # Public API - Jobs
    path('api/jobs', views.get_jobs, name='get_jobs'),
    path('api/jobs/<int:job_id>', views.get_job, name='get_job'),
    
    # Public API - Applications
    path('api/applications', views.submit_application, name='submit_application'),
    path('api/check-application/<int:job_id>/<str:email>', views.check_application, name='check_application'),
    
    # Public API - Content
    path('api/content', views.get_site_content, name='get_site_content'),
    
    # Admin API - Auth
    path('api/admin/login', views.admin_login, name='admin_login'),
    path('api/admin/logout', views.admin_logout, name='admin_logout'),
    path('api/admin/check', views.admin_check, name='admin_check'),
    path('api/admin/change-password', views.change_password, name='change_password'),
    
    # Admin API - Applications
    path('api/admin/applications', views.get_applications, name='get_applications'),
    
    # Admin API - Jobs
    path('api/admin/jobs/create', views.create_job, name='create_job'),
    path('api/admin/jobs/<int:job_id>/update', views.update_job, name='update_job'),
    path('api/admin/jobs/<int:job_id>/delete', views.delete_job, name='delete_job'),
    
    # Admin API - Content
    path('api/admin/content/<str:key>', views.update_site_content, name='update_site_content'),
    
    # Admin API - Analytics
    path('api/admin/analytics', views.get_analytics, name='get_analytics'),
]