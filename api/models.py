from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator,MinLengthValidator, MaxLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError


max_file_size=5 #5MB

def validate_file_size(value):
    limit = max_file_size * 1024 * 1024 # 5 MB
    if value.size > limit:
        raise ValidationError(f"File too large. Size should not exceed {max_file_size} MB.")


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        CUSTOMER = "c", "Customer"
        ADMIN = "a", "Admin"
        STAFF = "s", "Staff"
        TECHNICIAN = "t", "Technician"

    email = models.EmailField(
        unique=True,
        max_length=255
    )

    first_name = models.CharField(
        max_length=50
    )

    last_name = models.CharField(
        max_length=50
    )

    role = models.CharField(
        max_length=1,
        choices=Role,
        default=Role.CUSTOMER
    )

    address = models.CharField(
        max_length=100,
        blank=True
    )

    phone_number = models.CharField(
        max_length=10,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "first_name",
        "last_name"
    ]

    def __str__(self):
        return self.email

    
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

    def __str__(self):
        return self.name
        


class Profile(models.Model):
    class Roles(models.TextChoices):
        customer='c','Custumer'
        technician='t','Technician'
        admin='a','Admin'
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='profile')
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
    services=models.ManyToManyField(Service)

    def __str__(self):
        return self.user.email


class Article(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    image=models.ImageField(upload_to='articles/')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class Comment(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
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
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
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


class Booking(models.Model):
    technician = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='bookings')
    customer = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,related_name='customer_bookings')
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=7, 
        null=True, 
        blank=True
    )
    
    # Longitude: Max 180.0000000, min -180.0000000 (3 integer digits + 7 decimal digits)
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True
    )
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    problem_details = models.TextField()

    def __str__(self):
        return f"{self.customer.email}=>{self.technician.email}"



class ProblemImage(models.Model):
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE,related_name='problem_images',null=True)
    picture = models.ImageField(
        upload_to="products/",
        validators=[validate_file_size],
        null=True,
        blank=True
    )
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.booking


