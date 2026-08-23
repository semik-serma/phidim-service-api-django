from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=100)
    photo=models.ImageField(upload_to='categories/')
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name=models.CharField(max_length=200)
    description=models.TextField()
    category=models.ForeignKey(Category, on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)
    nagarita_front = models.ImageField(upload_to="nagarita/")
    nagarita_back = models.ImageField(upload_to="nagarita/")
    certificate = models.ImageField(upload_to="certificates/")
    phone_number = models.CharField(max_length=10)


