from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from .tasks import send_status_email_task

@receiver (post_save,sender=Booking)
def create_new_booking_email(sender, instance, created, **kwargs):
    if created:
        print("Booking created signal triggered")
        subject = "Booking Request"
        message = f"Dear {instance.technician.first_name},\n\nNew Booking Request has been made by {instance.customer.first_name},\n\nPlease Visit your dashboard to accept or reject the booking request.\n\nThank you."
        technician_email = instance.technician.email
        send_status_email_task.delay(subject, message, technician_email)