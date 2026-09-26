from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator,MinLengthValidator, MaxLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from .utils import generate_otp,otp_expiry
from django.utils import timezone
from datetime import timedelta



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

    is_verified = models.BooleanField(default=False)

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
    image = models.ImageField(upload_to='serivces/',null = True)

    def __str__(self):
        return self.name
        


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='profile')
    rating = models.PositiveSmallIntegerField(
    default=0,
    validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ]
)
    address = models.CharField(max_length=50)
    nagarita_front = models.ImageField(upload_to="nagarita/",null=True)
    nagarita_back = models.ImageField(upload_to="nagarita/",null=True)
    certificate = models.ImageField(upload_to="certificates/",null=True)
    phone_number = models.CharField(max_length=10)
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

    class STATUS(models.TextChoices):
        PENDING = 'p','pending'
        CONFIRMED = 'c','confirmed'
        REJECTED = 'r','rejected'

    status = models.CharField(max_length=1,choices=STATUS,default=STATUS.PENDING)
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


class UpdateHero(models.Model):
    text = models.CharField(max_length=40,validators=[MinLengthValidator(10)])
    discription = models.TextField(max_length=140,validators=[MinLengthValidator(60)])
    crouselImage = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class OTP(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    otp_value = models.CharField(max_length=6,validators=[MinLengthValidator(6)],default=generate_otp)
    expires_at = models.DateTimeField(default=otp_expiry)


    @property 
    def is_expired(self):
        return self.expires_at <= timezone.now()

    def __str__(self):
        return self.otp_value