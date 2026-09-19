from celery import shared_task
from .models import *
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


@shared_task
def clear_rejected_bookings():
    selected_bookings = Booking.objects.filter(status=Booking.STATUS.REJECTED)
    customer_emails = {booking.customer.email for booking in selected_bookings}
    print(customer_emails)
    
    deleted_count, _=Booking.objects.filter(status=Booking.STATUS.REJECTED).delete()
    print(f"{deleted_count} were deleted")
    print(_)


@shared_task
def send_otp_for_email_verification(user_id):
    user = CustomUser.objects.get(id=user_id)
    otp = OTP.objects.create(user=user)
    send_mail(
        subject='Email_verification',
        message=f"OTP for email_verification {otp.otp_value}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    print("EMAIL SENT SUCCESSFULLY")
