from django.shortcuts import render
import threading
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
# Create your views here.
def home(request):
    return render(request, 'home.html')

def view_404(request, exception=None):
    return render(request, 'base/404.html', status=404)


def send_contact_emails(form_data):
    """
    Send emails to admin and user 
    """
    try:
        admin_subject = f"New Contact Form Inquiry: {form_data.get('inquiry_type', 'General')}"
        admin_message = f"""
        New Contact Form Submission:
        
        Inquiry Type: {form_data.get('inquiry_type')}
        Name: {form_data.get('full_name')}
        Email: {form_data.get('email')}
        Phone: {form_data.get('phone')}
        Company: {form_data.get('company', 'Not provided')}
        Country: {form_data.get('country')}
        Product Interest: {form_data.get('product_interest', 'Not specified')}
        
        Project Details:
        {form_data.get('project_details', 'Not provided')}
        
        Message:
        {form_data.get('message')}
        
        Timestamp: {form_data.get('timestamp', 'Now')}
        """
        
        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        user_subject = "Thank You for Contacting Sambhavi Trading Pvt. Ltd"
        user_message = f"""
        Dear {form_data.get('full_name')},
        
        Thank you for reaching out to Sambhavi Trading Pvt. Ltd. We have received your inquiry and our team will get back to you within 24 hours on business days.
        
        Here's a summary of your inquiry:
        - Inquiry Type: {form_data.get('inquiry_type')}
        - Submitted: {form_data.get('timestamp', 'Now')}
        
        If you have any urgent questions, please don't hesitate to contact us at:
        Phone: +977-1-415414
        Email: info@everestcarpets.com
        
        Best regards,
        Sambhavi Trading Pvt. Ltd Team
         Kathmandu, Nepal
        G.P.O. Box: 
        """
        
        user_email = form_data.get('email')
        if user_email:
            send_mail(
                subject=user_subject,
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                fail_silently=False,
            )
            
    except BadHeaderError:
        print("Invalid header found.")
    except Exception as e:
        print(f"Error sending email: {e}")

@csrf_exempt
@require_POST
def contact_submit(request):
    """
    Handle contact form submission and send emails
    """
    try:
        data = json.loads(request.body)
        
        required_fields = ['full_name', 'email', 'phone', 'country', 'message', 'inquiry_type']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Please fill in the {field.replace("_", " ")} field.'
                }, status=400)
        
        if '@' not in data.get('email', '') or '.' not in data.get('email', ''):
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address.'
            }, status=400)
        
        from django.utils import timezone
        data['timestamp'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        
        email_thread = threading.Thread(target=send_contact_emails, args=(data,))
        email_thread.start()
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your inquiry! We have received your message and will get back to you within 24 hours. A confirmation email has been sent to your email address.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid form data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

def contact_us(request):
    return render(request, 'pages/contact.html')