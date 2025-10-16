from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('admin/', views.admin_page, name='admin_page'),
    path('login/', views.login_page, name='login_page'),
    
    # Public API endpoints
    path('api/health/', views.health_check, name='health_check'),
    path('api/jobs/', views.get_jobs, name='get_jobs'),
    path('api/jobs/<int:job_id>/', views.get_job, name='get_job'),
    path('api/applications/submit/', views.submit_application, name='submit_application'),
    path('api/applications/check/<int:job_id>/<str:email>/', views.check_application, name='check_application'),
    path('api/content/', views.get_site_content, name='get_site_content'),
    
    # Admin API endpoints
    path('api/admin/login/', views.admin_login, name='admin_login'),
    path('api/admin/logout/', views.admin_logout, name='admin_logout'),
    path('api/admin/check/', views.admin_check, name='admin_check'),
    path('api/admin/change-password/', views.change_password, name='change_password'),
    path('api/admin/applications/', views.get_applications, name='get_applications'),
    path('api/admin/jobs/create/', views.create_job, name='create_job'),
    path('api/admin/jobs/<int:job_id>/update/', views.update_job, name='update_job'),
    path('api/admin/jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('api/admin/content/<str:key>/', views.update_site_content, name='update_site_content'),
    path('api/admin/analytics/', views.get_analytics, name='get_analytics'),
]