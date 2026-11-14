from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.db import transaction
from .models import Profile,CustomUser
from django.core.mail import send_mail
from django.conf import settings
from api.tasks import send_status_email_task
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from chat.models import ChatGroup


class CustomUserDetailsSerializer(UserDetailsSerializer):
    role = serializers.CharField(read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = (*UserDetailsSerializer.Meta.fields, "role")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role
        return data


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Service
        fields='__all__'

class CategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    class Meta:
        model=Category
        fields='__all__'





class TechnicianRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=3)
    last_name = serializers.CharField(min_length=3)
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=20,
        min_length=8,
        write_only=True
    )
    confirm_password = serializers.CharField(
        max_length=20,
        min_length=8,
        write_only=True
    )

    address = serializers.CharField(max_length=50, min_length=10)
    nagarita_front = serializers.ImageField(required=False)
    nagarita_back = serializers.ImageField(required=False)
    certificate = serializers.ImageField(required=False)
    phone_number = serializers.CharField(max_length=10, min_length=10)
    role = serializers.CharField(max_length=1, min_length=1)

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_role(self, value):
        if value not in CustomUser.Role.values:
             raise serializers.ValidationError("Role Does not exist.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Remove fields that don't belong to CustomUser
        confirm_password = validated_data.pop("confirm_password")
        address = validated_data.pop("address")
        # nagarita_front = validated_data.pop("nagarita_front")
        # nagarita_back = validated_data.pop("nagarita_back")
        # certificate = validated_data.pop("certificate")
        phone_number = validated_data.pop("phone_number")


        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            role=validated_data["role"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        Profile.objects.create(
            user=user,
            address=address,
            # nagarita_front=nagarita_front,
            # nagarita_back=nagarita_back,
            # certificate=certificate,
            phone_number=phone_number,
        )

        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            email=email,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        attrs["user"] = user

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    services=ServiceSerializer(many=True)
    class Meta:
        model=Profile
        fields='__all__'


class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'role',
            'address',
            'phone_number',
            'profile',
            'is_verified'
        ]


class ProfileServiceSerializer(serializers.Serializer):

    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        many=True
    )

    def create(self, validated_data):
        services = validated_data["service_ids"]

        # Get the logged-in user's profile
        profile = self.context["request"].user.profile

        # Link services to the profile
        profile.services.add(*services)

        return profile




from rest_framework import serializers
from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all()
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'article',
            'user',
            'content',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at'
        ]


class ArticleSerializer(serializers.ModelSerializer):
    comments=CommentSerializer(many=True)
    class Meta:
        model=Article
        fields='__all__'
        read_only_fields=["created_at","updated_at"]





class ReplyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['id','rating','address','nagarita_front','nagarita_back','certificate','phone_number']


class ReplyUserSerializer(serializers.ModelSerializer):
    profile=ReplyProfileSerializer()
    class Meta:
        model=CustomUser
        fields=['id','first_name','last_name','email','profile']


class CustomUserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['first_name','last_name']


class ProblemImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProblemImage
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        if user.role != CustomUser.Role.CUSTOMER:
            raise serializers.ValidationError(
                "Only customer can upload problem images."
            )

        return attrs

        
class BookingsListingSerializer(serializers.ModelSerializer):

    technician = CustomUserMiniSerializer(read_only=True)
    customer = CustomUserMiniSerializer(read_only=True)

    problem_images = ProblemImageSerializer(many=True)

    status_display = serializers.SerializerMethodField()
    chat_group = serializers.SerializerMethodField()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_chat_group(self, obj):

        if obj.status != Booking.STATUS.CONFIRMED:
            return None

        chat_group, created = ChatGroup.objects.get_or_create(
            booking=obj
        )

        return str(chat_group.id)

    class Meta:
        model = Booking

        fields = [
            "id",
            "status",
            "status_display",
            "technician",
            "customer",
            "problem_images",
            "chat_group",
            "latitude",
            "longitude",
            "date",
            "created_at",
            "updated_at",
            "problem_details",
        ]
        
class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "updated_at",
            "customer",
        ]

    def validate_technician(self, technician):
        if technician.role != CustomUser.Role.TECHNICIAN:
            raise serializers.ValidationError(
                "The selected user is not a technician."
            )

        return technician

    def create(self, validated_data):
        customer = self.context["request"].user

        if customer.role != CustomUser.Role.CUSTOMER:
            raise serializers.ValidationError(
                "Only a customer can create a booking."
            )

        if not customer.is_verified:
            raise serializers.ValidationError(
                "Your account must be verified before creating a booking."
            )

        return Booking.objects.create(
            customer=customer,
            **validated_data
        )

def create(self, validated_data):
    customer = self.context["request"].user

    if customer.role != CustomUser.Role.CUSTOMER:
        raise serializers.ValidationError(
            "Only a customer can create a booking."
        )

    # Check if the customer is verified
    if not customer.is_verified:
        raise serializers.ValidationError(
            "Your account must be verified before creating a booking."
        )

    booking = Booking.objects.create(
        customer=customer,
        **validated_data
    )

    return booking


# class BookingListingSerializer(serializers.ModelSerializer):


class TechnicianBookingUpdateSerializer(serializers.Serializer):
    booking = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all()
    )

    status = serializers.CharField()

    def validate(self, attrs):
        booking = attrs["booking"]
        new_status = attrs["status"]

        # Prevent updating to the same status
        if booking.status == new_status:
            raise serializers.ValidationError(
                "Booking is already in the same status."
            )

        # Define allowed status transitions
        allowed_transitions = {
            Booking.STATUS.PENDING: {
                Booking.STATUS.CONFIRMED,
                Booking.STATUS.REJECTED,
            },
            Booking.STATUS.CONFIRMED: {
                Booking.STATUS.SERVED,
            },
        }

        allowed_statuses = allowed_transitions.get(
            booking.status, set()
        )

        if new_status not in allowed_statuses:
            raise serializers.ValidationError(
                f"Cannot change booking status from "
                f"'{booking.get_status_display()}' to "
                f"'{new_status}'."
            )

        return attrs

    def create(self, validated_data):
        booking = validated_data["booking"]
        new_status = validated_data["status"]

        booking.status = new_status
        booking.save(update_fields=["status", "updated_at"])

        print("===================================")
        print("BOOKING UPDATED")
        print("Booking ID:", booking.id)
        print("Status:", booking.get_status_display())
        print("Customer:", booking.customer)
        print("Customer email:",
              booking.customer.email if booking.customer else None)
        print("Technician email:", booking.technician.email)
        print("===================================")

        self.send_status_email(booking)

        return booking

    def send_status_email(self, booking):
        if not booking.customer:
            print("EMAIL NOT SENT: customer is None")
            return

        customer_email = booking.customer.email

        if not customer_email:
            print("EMAIL NOT SENT: customer has no email")
            return

        print("Sending email to:", customer_email)

        if booking.status == Booking.STATUS.CONFIRMED:

            subject = "Your booking has been accepted"

            message = (
                f"Your booking #{booking.id} has been accepted "
                f"by technician {booking.technician.email}.\n\n"
                f"Problem details: {booking.problem_details}\n"
                f"Booking date: {booking.date}\n\n"
                "Thank you for using our service."
            )

        elif booking.status == Booking.STATUS.REJECTED:

            subject = "Your booking has been rejected"

            message = (
                f"Unfortunately, your booking #{booking.id} has been "
                f"rejected by technician {booking.technician.email}.\n\n"
                f"Problem details: {booking.problem_details}\n"
                f"Booking date: {booking.date}\n\n"
                "Please try booking another technician."
            )

        elif booking.status == Booking.STATUS.SERVED:

            subject = "Your booking service has been completed"

            message = (
                f"Your booking #{booking.id} has been successfully served "
                f"by technician {booking.technician.email}.\n\n"
                f"Problem details: {booking.problem_details}\n"
                f"Booking date: {booking.date}\n\n"
                "Thank you for using our service."
            )

        else:
            print("EMAIL NOT SENT: unsupported status")
            return

        print("Subject:", subject)
        print("From:", settings.DEFAULT_FROM_EMAIL)
        print("To:", customer_email)

        send_status_email_task.delay(
            subject=subject,
            message=message,
            customer_email=customer_email
        )


from rest_framework import serializers
from .models import HeroBanner, CustomUser


class HeroBannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = HeroBanner
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        if request.user.role != CustomUser.Role.ADMIN:
            raise serializers.ValidationError(
                "Only admin users can create or update hero banners."
            )

        return attrs

        

class OtpVerifySerializer(serializers.Serializer):
    otp_value = serializers.CharField(max_length=6)

    def validate_otp_value(self, value):
        user = self.context["request"].user

        try:
            otp = OTP.objects.get(
                user=user,
                otp_value=value
            )
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        if otp.is_expired:
            raise serializers.ValidationError("OTP has expired.")

        otp.delete()

        return value



class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["address","certificate","nagarita_front","nagarita_back","phone_number"]



# class ServiceArea

class ServiceAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceArea
        fields = '__all__'