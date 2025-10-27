# ============================================
# FIXED views.py - Proper File Upload Handling
# ============================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import json


# ============================================
# SUBMIT APPLICATION - FIXED VERSION
# ============================================

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def submit_application(request):
    """Submit job application with file uploads"""
    
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        from .models import Application
        
        # Get form data
        data = {
            'jobId': request.POST.get('jobId'),
            'jobTitle': request.POST.get('jobTitle'),
            'fullName': request.POST.get('fullName'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'age': request.POST.get('age'),
            'gender': request.POST.get('gender'),
            'kcseGrade': request.POST.get('kcseGrade'),
        }
        
        print("=" * 60)
        print("📥 NEW APPLICATION RECEIVED")
        print("=" * 60)
        print(f"Name: {data['fullName']}")
        print(f"Email: {data['email']}")
        print(f"Job: {data['jobTitle']} (ID: {data['jobId']})")
        print(f"Files uploaded: {list(request.FILES.keys())}")
        print("=" * 60)
        
        # Validate required fields
        required = ['jobId', 'jobTitle', 'fullName', 'email', 'phone', 'age', 'gender', 'kcseGrade']
        missing = [f for f in required if not data.get(f)]
        
        if missing:
            return JsonResponse({
                'error': f'Missing required fields: {", ".join(missing)}'
            }, status=400)
        
        # Check for duplicate application
        existing = Application.objects.filter(
            job_id=data['jobId'],
            email=data['email']
        ).first()
        
        if existing:
            print(f"⚠️ Duplicate application detected from {data['email']}")
            return JsonResponse({
                'error': 'You have already applied for this position',
                'appliedDate': existing.applied_at.isoformat()
            }, status=409)
        
        # Get uploaded files
        cv_file = request.FILES.get('cv')
        id_file = request.FILES.get('id_document')
        cert_file = request.FILES.get('certificate')
        
        # Validate required files
        if not cv_file:
            return JsonResponse({'error': 'CV/Resume is required'}, status=400)
        if not id_file:
            return JsonResponse({'error': 'ID/Passport document is required'}, status=400)
        
        # Validate file sizes (5MB max)
        for file in [cv_file, id_file, cert_file]:
            if file and file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'error': f'{file.name} is too large. Maximum size is 5MB per file.'
                }, status=400)
        
      
        application = Application.objects.create(
            job_id=int(data['jobId']),
            job_title=data['jobTitle'],
            full_name=data['fullName'],
            email=data['email'],
            phone=data['phone'],
            age=int(data['age']),
            gender=data['gender'],
            kcse_grade=data['kcseGrade'],
            cv_document=cv_file,
            id_document=id_file,
            certificate_document=cert_file if cert_file else None,  # Pass file object
            status='pending'
        )
        
        print(f"✅ Application saved successfully! ID: {application.id}")
        
        # Send confirmation email
        email_sent = False
        try:
            email_sent = send_confirmation_email(
                applicant_email=data['email'],
                applicant_name=data['fullName'],
                job_title=data['jobTitle'],
                application_id=application.id
            )
            if email_sent:
                print(f"📧 Confirmation email sent to {data['email']}")
        except Exception as e:
            print(f"⚠️ Email error: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Application submitted successfully!',
            'applicationId': application.id,
            'emailSent': email_sent
        }, status=201)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': 'Server error occurred while processing your application',
            'details': str(e)
        }, status=500)


def send_confirmation_email(applicant_email, applicant_name, job_title, application_id):
    """Send confirmation email to applicant"""
    
    subject = f"Application Received - {job_title} | Green Tara"
    
    message = f"""
Dear {applicant_name},

Thank you for applying for the position of {job_title} at Green Tara!

We have successfully received your application and all supporting documents.

📋 Application Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Position: {job_title}
• Application ID: GT-{application_id}
• Submitted: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ What's Next?

Our recruitment team will review your application. If your qualifications 
match our requirements, we will contact you within 5-7 business days.

Best regards,
Green Tara Recruitment Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email: info@greentara.co.ke
📞 Phone: +254 700 123 456
🌐 Website: https://greentara-jobs.onrender.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[applicant_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


# ============================================
# GET ALL JOBS
# ============================================

@require_http_methods(["GET"])
def get_jobs(request):
    """Get all active jobs"""
    try:
        from .models import Job
        
        jobs = Job.objects.filter(is_active=True).order_by('-created_at')
        
        jobs_list = []
        for job in jobs:
            jobs_list.append({
                'id': job.id,
                'title': job.title,
                'location': job.location,
                'salary': job.salary,
                'contract': job.contract,
                'icon': job.icon or '💼',
                'description': job.description,
                'responsibilities': job.responsibilities,
                'requirements': job.requirements,
                'benefits': job.benefits,
                'workplace_photos': job.workplace_photos or [],
                'expiry_date': job.expiry_date.isoformat() if job.expiry_date else None,
                'created_at': job.created_at.isoformat(),
            })
        
        return JsonResponse(jobs_list, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================
# GET SINGLE JOB
# ============================================

@require_http_methods(["GET"])
def get_job(request, job_id):
    """Get a single job by ID"""
    try:
        from .models import Job
        
        job = Job.objects.get(id=job_id, is_active=True)
        
        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'location': job.location,
            'salary': job.salary,
            'contract': job.contract,
            'icon': job.icon or '💼',
            'description': job.description,
            'responsibilities': job.responsibilities,
            'requirements': job.requirements,
            'benefits': job.benefits,
            'workplace_photos': job.workplace_photos or [],
            'expiry_date': job.expiry_date.isoformat() if job.expiry_date else None,
            'created_at': job.created_at.isoformat(),
        })
        
    except Job.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================
# GET SITE CONTENT
# ============================================

@require_http_methods(["GET"])
def get_site_content(request):
    """Get site content"""
    try:
        from .models import SiteContent
        
        content, created = SiteContent.objects.get_or_create(pk=1)
        
        return JsonResponse({
            'site_name': content.site_name,
            'site_logo': content.site_logo.url if content.site_logo else None,
            'hero_title': content.hero_title,
            'hero_subtitle': content.hero_subtitle,
            'about_text': content.about_text,
            'contact_email': content.contact_email,
            'contact_phone': content.contact_phone,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================
# GET ALL APPLICATIONS (for admin)
# ============================================

@require_http_methods(["GET"])
def get_applications(request):
    """Get all applications"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        from .models import Application
        
        apps = Application.objects.all().order_by('-applied_at')
        
        apps_list = []
        for app in apps:
            apps_list.append({
                'id': app.id,
                'job_id': app.job_id,
                'job_title': app.job_title,
                'full_name': app.full_name,
                'email': app.email,
                'phone': app.phone,
                'age': app.age,
                'gender': app.gender,
                'kcse_grade': app.kcse_grade,
                'status': app.status,
                'applied_at': app.applied_at.isoformat(),
                'cv_url': app.cv_document.url if app.cv_document else None,
                'id_url': app.id_document.url if app.id_document else None,
                'cert_url': app.certificate_document.url if app.certificate_document else None,
            })
        
        return JsonResponse(apps_list, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Server is running',
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def check_application(request, job_id, email):
    """Check if user already applied for this job"""
    
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        return response
    
    try:
        from .models import Application
        
        application = Application.objects.filter(
            job_id=job_id,
            email=email
        ).first()
        
        if application:
            return JsonResponse({
                'hasApplied': True,
                'appliedDate': application.applied_at.isoformat(),
                'status': application.status
            })
        
        return JsonResponse({'hasApplied': False})
        
    except Exception as e:
        print(f"Error checking application: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def admin_login(request):
    """Admin login endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        from django.contrib.auth import authenticate, login
        
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
                'error': 'Invalid credentials or not authorized'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def admin_logout(request):
    """Admin logout endpoint"""
    try:
        from django.contrib.auth import logout
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logged out'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def admin_check(request):
    """Check if user is authenticated admin"""
    if request.user.is_authenticated and request.user.is_staff:
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username
        })
    else:
        return JsonResponse({'authenticated': False}, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    """Change admin password"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not request.user.check_password(current_password):
            return JsonResponse({'error': 'Current password is incorrect'}, status=400)
        
        request.user.set_password(new_password)
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_job(request):
    """Create a new job"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        from .models import Job
        data = json.loads(request.body)
        
        job = Job.objects.create(
            title=data['title'],
            location=data['location'],
            salary=data['salary'],
            contract=data['contract'],
            icon=data.get('icon'),
            description=data['description'],
            responsibilities=data['responsibilities'],
            requirements=data['requirements'],
            benefits=data['benefits'],
            expiry_date=data.get('expiry_date'),
            is_active=data.get('is_active', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Job created',
            'jobId': job.id
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def update_job(request, job_id):
    """Update an existing job"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        from .models import Job
        job = Job.objects.get(id=job_id)
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
        job.is_active = data.get('is_active', job.is_active)
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Job updated'
        })
        
    except Job.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_job(request, job_id):
    """Delete a job"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        from .models import Job
        job = Job.objects.get(id=job_id)
        job.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Job deleted'
        })
        
    except Job.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def update_site_content(request, key):
    """Update site content"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        from .models import SiteContent
        data = json.loads(request.body)
        value = data.get('value')
        
        content, created = SiteContent.objects.get_or_create(pk=1)
        
        if hasattr(content, key):
            setattr(content, key, value)
            content.save()
            return JsonResponse({
                'success': True,
                'message': f'{key} updated'
            })
        else:
            return JsonResponse({'error': 'Invalid field'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_analytics(request):
    """Get analytics data for admin dashboard"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        from .models import Application, Job
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # Basic counts
        total_apps = Application.objects.count()
        total_jobs = Job.objects.filter(is_active=True).count()
        
        # Today's applications
        today = timezone.now().date()
        today_apps = Application.objects.filter(applied_at__date=today).count()
        
        # This week
        week_ago = timezone.now() - timedelta(days=7)
        week_apps = Application.objects.filter(applied_at__gte=week_ago).count()
        
        # This month
        month_ago = timezone.now() - timedelta(days=30)
        month_apps = Application.objects.filter(applied_at__gte=month_ago).count()
        
        # Gender distribution
        gender_dist = list(Application.objects.values('gender').annotate(count=Count('id')))
        
        # Age groups
        age_groups = [
            {'age_group': '18-25', 'count': Application.objects.filter(age__gte=18, age__lte=25).count()},
            {'age_group': '26-35', 'count': Application.objects.filter(age__gte=26, age__lte=35).count()},
            {'age_group': '36-45', 'count': Application.objects.filter(age__gte=36, age__lte=45).count()},
            {'age_group': '46+', 'count': Application.objects.filter(age__gte=46).count()},
        ]
        
        # Applications by job
        apps_by_job = list(Application.objects.values('job_title').annotate(count=Count('id')))
        
        return JsonResponse({
            'totalApplications': total_apps,
            'todayApplications': today_apps,
            'weeklyApplications': week_apps,
            'monthlyApplications': month_apps,
            'activeJobs': total_jobs,
            'expiredJobs': Job.objects.filter(is_active=False).count(),
            'avgApplicationsPerJob': round(total_apps / total_jobs, 1) if total_jobs > 0 else 0,
            'genderDistribution': gender_dist,
            'ageDistribution': age_groups,
            'applicationsByJob': apps_by_job,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
