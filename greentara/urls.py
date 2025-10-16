
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django's built-in admin
    path('', include('jobs.urls')),  # Your custom pages
]