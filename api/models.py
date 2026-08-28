from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator,MinLengthValidator, MaxLengthValidator
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
    class Roles(models.TextChoices):
        customer='c','Custumer'
        technician='t','Technician'
        admin='a','Admin'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
    default=0,
    validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ]
)
    address = models.CharField(max_length=50)
    nagarita_front = models.ImageField(upload_to="nagarita/")
    nagarita_back = models.ImageField(upload_to="nagarita/")
    certificate = models.ImageField(upload_to="certificates/")
    phone_number = models.CharField(max_length=10)
    role=models.CharField(max_length=1, choices=Roles, default='c')
    services=models.ManyToManyField(Service,null=True,blank=True)


class Article(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    image=models.ImageField(upload_to='articles/')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    article=models.ForeignKey(Article,on_delete=models.CASCADE,related_name='comments')
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class AnnouncementBanner(models.Model):
        text = models.CharField(
        max_length=150,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(150),
        ],
        help_text="Announcement must be between 10 and 150 characters."
        )
        created_at=models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)


class Reply(models.Model):
    article=models.ForeignKey(Article,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    comment=models.ForeignKey(Comment,on_delete=models.CASCADE)
    reply=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)


class TotalLikesonComment(models.Model):
    article=models.ForeignKey(Article,on_delete=models.CASCADE)
    comment=models.ForeignKey(Comment,on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(default=0,editable=False)
    created_at=models.DateTimeField(auto_now_add=True)


class CrouselImages(models.Model):
    img1=models.ImageField(upload_to='crousel-images/')
    img2=models.ImageField(upload_to='crousel-images/')
    img3=models.ImageField(upload_to='crousel-images/')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)










