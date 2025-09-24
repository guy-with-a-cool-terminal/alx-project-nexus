from django.core.mail import send_mail
from django.conf import settings
from ..models import EmailLog

class EmailService:
    @staticmethod
    def send_welcome_email(user):
        """send welcome email to new users and log it"""
        subject = 'Welcome to Our E-Commerce Platform🎉'
        message = f'''
        Hi {user.username},
        Welcome to our e-commerce platform🎉 Your {user.get_role_display().lower()} account has been successfully created.
        
        Start browsing our products and enjoy your shopping experience!
        
        Best regards,
        The CnB E-Commerce Team
        '''
        try:
            send_mail(
                subject,
                message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            # log successful email
            EmailLog.objects.create(
                recipient_email=user.email,
                recipient_user=user,
                email_type='WELCOME',
                subject=subject,
                status='SENT'
            )
            return True
        
        except Exception as e:
            # log failed email
            EmailLog.objects.create(
                recipient_email=user.email,
                recipient_user=user,
                email_type='WELCOME',
                subject=subject,
                status='FAILED',
                error_message=str(e)
            )
            # for user experience let it fail silently(no raise)
            return False