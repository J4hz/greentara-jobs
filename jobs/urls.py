from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Pages
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('dashboard/', TemplateView.as_view(template_name='admin.html'), name='admin_page'),
    
    # API - Add both with AND without trailing slash
    path('api/health', views.health_check, name='health'),
    path('api/health/', views.health_check),
    
    path('api/jobs', views.get_jobs, name='get_jobs'),
    path('api/jobs/', views.get_jobs),
    
    path('api/jobs/<int:job_id>', views.get_job, name='get_job'),
    path('api/jobs/<int:job_id>/', views.get_job),
    
    path('api/applications', views.submit_application, name='submit_application'),
    path('api/applications/', views.submit_application),
    
    path('api/check-application/<int:job_id>/<str:email>', views.check_application),
    path('api/check-application/<int:job_id>/<str:email>/', views.check_application, name='check_application'),
    
    path('api/content', views.get_site_content, name='get_site_content'),
    path('api/content/', views.get_site_content),
    
    # Admin API
    path('api/admin/login', views.admin_login),
    path('api/admin/login/', views.admin_login, name='admin_login'),
    
    path('api/admin/logout', views.admin_logout),
    path('api/admin/logout/', views.admin_logout, name='admin_logout'),
    
    path('api/admin/check', views.admin_check),
    path('api/admin/check/', views.admin_check, name='admin_check'),
    
    # ... rest of your URLs with both versions
]