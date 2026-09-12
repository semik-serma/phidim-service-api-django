from celery import shared_task
from .models import Booking
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_status_email_task(subject,message,customer_email):
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer_email],
            fail_silently=False,
        )

        print("EMAIL SENT SUCCESSFULLY")