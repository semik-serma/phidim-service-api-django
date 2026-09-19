import secrets
import string
from datetime import timedelta
from django.utils import timezone

def generate_otp(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def otp_expiry():
    return timezone.now() + timedelta(minutes=5)