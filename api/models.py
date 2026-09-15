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


# ============================================================
# CHAT MODELS
# ============================================================

class Conversation(models.Model):
    """
    Represents either:
    - a 1-to-1 conversation
    - a group conversation
    """

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_group = models.BooleanField(
        default=False
    )

    # Used only for 1-to-1 conversations.
    # Example: direct:4:12
    direct_key = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_conversations"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        if self.is_group:
            return self.name or f"Group {self.id}"

        return f"Conversation {self.id}"


class ConversationParticipant(models.Model):
    """
    Users who belong to a conversation.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="chat_conversations"
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "user"],
                name="unique_chat_participant"
            )
        ]

    def __str__(self):
        return f"{self.user.email} -> Conversation {self.conversation.id}"


class ChatAttachment(models.Model):
    """
    Files/images attached to chat messages.

    Maximum size: less than 5 MB.
    """

    file = models.FileField(
        upload_to="chat/attachments/",
        validators=[validate_file_size]
    )

    original_name = models.CharField(
        max_length=255
    )

    size = models.PositiveIntegerField()

    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="chat_attachments"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.original_name


class ChatMessage(models.Model):
    """
    A single message in a conversation.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sent_chat_messages"
    )

    content = models.TextField(
        blank=True
    )

    attachment = models.ForeignKey(
        ChatAttachment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message"
    )

    is_deleted = models.BooleanField(
        default=False
    )

    edited_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["conversation", "-created_at"]
            ),
            models.Index(
                fields=["sender", "-created_at"]
            ),
        ]

    def __str__(self):
        return f"Message {self.id} - {self.sender.email}"


class MessageReadReceipt(models.Model):
    """
    Tracks which users have read which messages.
    """

    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="read_receipts"
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="chat_read_receipts"
    )

    read_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user"],
                name="unique_message_read_receipt"
            )
        ]

    def __str__(self):
        return f"{self.user.email} read Message {self.message.id}"


class ChatPresence(models.Model):
    """
    Tracks online/offline state and last seen.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="chat_presence"
    )

    is_online = models.BooleanField(
        default=False
    )

    active_connections = models.PositiveIntegerField(
        default=0
    )

    last_seen = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        status = "Online" if self.is_online else "Offline"
        return f"{self.user.email} - {status}"


class ChatNotification(models.Model):
    """
    Notification generated by chat activity.
    """

    NOTIFICATION_TYPES = (
        ("message", "New Message"),
        ("mention", "Mention"),
        ("group", "Group Activity"),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="chat_notifications"
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default="message"
    )

    text = models.TextField()

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_notifications"
    )

    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_notifications"
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "is_read"]
            ),
            models.Index(
                fields=["user", "-created_at"]
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.notification_type}"