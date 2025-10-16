from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import Job, Application, SiteContent


# Public Views
def index(request):
    """Serve the main index.html page"""
    return render(request, 'index.html')


def admin_page(request):
    """Serve the admin dashboard"""
    return render(request, 'admin.html')


def login_page(request):
    """Serve the login page"""
    return render(request, 'login.html')


# API Endpoints
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'OK',
        'message': 'Green Tara API is running'
    })


@require_http_methods(["GET"])
def get_jobs(request):
    """Get all jobs with optional filtering"""
    search = request.GET.get('search', '')
    location = request.GET.get('location', '')
    active_only = request.GET.get('active_only', 'false') == 'true'
    
    jobs = Job.objects.all()
    
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(location__icontains=search) |
            Q(description__icontains=search)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if active_only:
        jobs = jobs.filter(
            Q(expiry_date__isnull=True) |
            Q(expiry_date__gte=timezone.now().date())
        )
    
    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'location': job.location,
        'salary': job.salary,
        'contract': job.contract,
        'icon': job.icon,
        'description': job.description,
        'responsibilities': job.responsibilities,
        'requirements': job.requirements,
        'benefits': job.benefits,
        'expiry_date': job.expiry_date.isoformat() if job.expiry_date else None,
        'workplace_photos': job.workplace_photos,
        'created_at': job.created_at.isoformat()
    } for job in jobs]
    
    return JsonResponse(jobs_data, safe=False)


@require_http_methods(["GET"])
def get_job(request, job_id):
    """Get single job details"""
    job = get_object_or_404(Job, id=job_id)
    
    job_data = {
        'id': job.id,
        'title': job.title,
        'location': job.location,
        'salary': job.salary,
        'contract': job.contract,
        'icon': job.icon,
        'description': job.description,
        'responsibilities': job.responsibilities,
        'requirements': job.requirements,
        'benefits': job.benefits,
        'expiry_date': job.expiry_date.isoformat() if job.expiry_date else None,
        'workplace_photos': job.workplace_photos,
        'created_at': job.created_at.isoformat()
    }
    
    return JsonResponse(job_data)


@csrf_exempt
@require_http_methods(["POST"])
def submit_application(request):
    """Submit job application"""
    try:
        data = json.loads(request.body)
        
        job_id = data.get('jobId')
        email = data.get('email')
        
        # Check for duplicate application
        if Application.objects.filter(job_id=job_id, email=email).exists():
            existing = Application.objects.get(job_id=job_id, email=email)
            return JsonResponse({
                'error': 'You have already applied for this position',
                'alreadyApplied': True,
                'appliedDate': existing.applied_at.isoformat()
            }, status=409)
        
        # Create application
        application = Application.objects.create(
            job_id=job_id,
            job_title=data.get('jobTitle'),
            full_name=data.get('fullName'),
            email=email,
            phone=data.get('phone'),
            age=data.get('age'),
            gender=data.get('gender'),
            kcse_grade=data.get('kcseGrade'),
            documents=data.get('documents')
        )
        
        # Send confirmation email
        email_sent = send_application_confirmation(
            application.email,
            application.full_name,
            application.job_title
        )
        
        # Send admin notification
        send_admin_notification(
            application.full_name,
            application.job_title,
            application.email,
            application.phone
        )
        
        return JsonResponse({
            'id': application.id,
            'message': 'Application submitted successfully',
            'emailSent': email_sent
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def check_application(request, job_id, email):
    """Check if email has already applied for job"""
    exists = Application.objects.filter(job_id=job_id, email=email).exists()
    
    if exists:
        application = Application.objects.get(job_id=job_id, email=email)
        return JsonResponse({
            'hasApplied': True,
            'appliedDate': application.applied_at.isoformat()
        })
    
    return JsonResponse({'hasApplied': False})


@require_http_methods(["GET"])
def get_site_content(request):
    """Get all site content"""
    content = SiteContent.objects.all()
    content_dict = {item.key: item.value for item in content}
    return JsonResponse(content_dict)


# Admin Endpoints (require authentication)
@csrf_exempt
@require_http_methods(["POST"])
def admin_login(request):
    """Admin login"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'username': user.username
            })
        else:
            return JsonResponse({
                'error': 'Invalid username or password'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def admin_logout(request):
    """Admin logout"""
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logged out successfully'
    })


@require_http_methods(["GET"])
def admin_check(request):
    """Check admin session"""
    if request.user.is_authenticated and request.user.is_staff:
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username
        })
    return JsonResponse({'authenticated': False})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def change_password(request):
    """Change admin password"""
    try:
        data = json.loads(request.body)
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not request.user.check_password(current_password):
            return JsonResponse({
                'error': 'Current password is incorrect'
            }, status=401)
        
        if len(new_password) < 6:
            return JsonResponse({
                'error': 'New password must be at least 6 characters long'
            }, status=400)
        
        request.user.set_password(new_password)
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_applications(request):
    """Get all applications (admin only)"""
    applications = Application.objects.all()
    
    apps_data = [{
        'id': app.id,
        'job_id': app.job_id,
        'job_title': app.job_title,
        'full_name': app.full_name,
        'email': app.email,
        'phone': app.phone,
        'age': app.age,
        'gender': app.gender,
        'kcse_grade': app.kcse_grade,
        'applied_at': app.applied_at.isoformat()
    } for app in applications]
    
    return JsonResponse(apps_data, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_job(request):
    """Create new job (admin only)"""
    try:
        data = json.loads(request.body)
        
        job = Job.objects.create(
            title=data.get('title'),
            location=data.get('location'),
            salary=data.get('salary'),
            contract=data.get('contract'),
            icon=data.get('icon'),
            description=data.get('description'),
            responsibilities=data.get('responsibilities'),
            requirements=data.get('requirements'),
            benefits=data.get('benefits'),
            expiry_date=data.get('expiry_date'),
            workplace_photos=data.get('workplace_photos')
        )
        
        return JsonResponse({
            'id': job.id,
            'message': 'Job created successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def update_job(request, job_id):
    """Update job (admin only)"""
    try:
        job = get_object_or_404(Job, id=job_id)
        data = json.loads(request.body)
        
        job.title = data.get('title', job.title)
        job.location = data.get('location', job.location)
        job.salary = data.get('salary', job.salary)
        job.contract = data.get('contract', job.contract)
        job.icon = data.get('icon', job.icon)
        job.description = data.get('description', job.description)
        job.responsibilities = data.get('responsibilities', job.responsibilities)
        job.requirements = data.get('requirements', job.requirements)
        job.benefits = data.get('benefits', job.benefits)
        job.expiry_date = data.get('expiry_date', job.expiry_date)
        job.workplace_photos = data.get('workplace_photos', job.workplace_photos)
        job.save()
        
        return JsonResponse({'message': 'Job updated successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_job(request, job_id):
    """Delete job (admin only)"""
    try:
        job = get_object_or_404(Job, id=job_id)
        job.delete()
        return JsonResponse({'message': 'Job deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def update_site_content(request, key):
    """Update site content (admin only)"""
    try:
        data = json.loads(request.body)
        value = data.get('value')
        
        SiteContent.set_content(key, value)
        
        return JsonResponse({'message': 'Content updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_analytics(request):
    """Get analytics data (admin only)"""
    today = timezone.now().date()
    
    analytics = {
        'totalJobs': Job.objects.count(),
        'activeJobs': Job.objects.filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gte=today)
        ).count(),
        'totalApplications': Application.objects.count(),
        'monthlyApplications': Application.objects.filter(
            applied_at__month=today.month,
            applied_at__year=today.year
        ).count(),
        'weeklyApplications': Application.objects.filter(
            applied_at__gte=today - timedelta(days=7)
        ).count(),
        'todayApplications': Application.objects.filter(
            applied_at__date=today
        ).count(),
    }
    
    analytics['expiredJobs'] = analytics['totalJobs'] - analytics['activeJobs']
    analytics['avgApplicationsPerJob'] = round(
        analytics['totalApplications'] / analytics['totalJobs'], 1
    ) if analytics['totalJobs'] > 0 else 0
    
    # Gender distribution
    analytics['genderDistribution'] = list(
        Application.objects.values('gender')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Age distribution
    from django.db.models import Case, When, Value, CharField
    analytics['ageDistribution'] = list(
        Application.objects.annotate(
            age_group=Case(
                When(age__gte=18, age__lte=25, then=Value('18-25')),
                When(age__gte=26, age__lte=35, then=Value('26-35')),
                When(age__gte=36, age__lte=45, then=Value('36-45')),
                When(age__gte=46, age__lte=55, then=Value('46-55')),
                When(age__gte=56, then=Value('56+')),
                default=Value('Unknown'),
                output_field=CharField()
            )
        )
        .values('age_group')
        .annotate(count=Count('id'))
        .order_by('age_group')
    )
    
    # Applications by job
    analytics['applicationsByJob'] = list(
        Application.objects.values('job_title')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Applications over time (last 30 days)
    from django.db.models.functions import TruncDate
    analytics['applicationsOverTime'] = list(
        Application.objects.filter(
            applied_at__gte=today - timedelta(days=30)
        )
        .annotate(date=TruncDate('applied_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    return JsonResponse(analytics)


# Helper functions for email
def send_application_confirmation(email, name, job_title):
    """Send confirmation email to applicant"""
    try:
        subject = f'Application Received - {job_title}'
        message = f'''
        Dear {name},
        
        Thank you for applying to the {job_title} position at Green Tara.
        
        We have successfully received your application and our team will review it carefully.
        If your qualifications match our requirements, we will contact you within the next few days.
        
        Best regards,
        Green Tara Recruitment Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'Email error: {e}')
        return False


def send_admin_notification(name, job_title, email, phone):
    """Send notification to admin"""
    try:
        subject = f'🔔 New Application: {job_title}'
        message = f'''
        New application received!
        
        Applicant: {name}
        Position: {job_title}
        Email: {email}
        Phone: {phone}
        
        Login to admin dashboard to view details.
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f'Admin notification error: {e}')
        return False
    from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to Green Tara Jobs!</h1>")
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def admin_dashboard(request):
    return render(request, 'admin.html')