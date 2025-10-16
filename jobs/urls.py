
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Homepage
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Your custom admin
]