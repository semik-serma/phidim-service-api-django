from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.db import transaction
from .models import Profile,CustomUser

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Service
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
    nagarita_front = serializers.ImageField()
    nagarita_back = serializers.ImageField()
    certificate = serializers.ImageField()
    phone_number = serializers.CharField(max_length=10, min_length=10)


    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
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

        role = CustomUser.Role.TECHNICIAN
        address = validated_data.pop("address")
        nagarita_front = validated_data.pop("nagarita_front")
        nagarita_back = validated_data.pop("nagarita_back")
        certificate = validated_data.pop("certificate")
        phone_number = validated_data.pop("phone_number")

        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            role=role,
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        Profile.objects.create(
            user=user,
            address=address,
            nagarita_front=nagarita_front,
            nagarita_back=nagarita_back,
            certificate=certificate,
            phone_number=phone_number,
            role=role
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
            'first_name',
            'last_name',
            'email',
            'role',
            'address',
            'phone_number',
            'profile'
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




class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields='__all__'
        read_only_fields=["created_at","updated_at"]


class ArticleSerializer(serializers.ModelSerializer):
    comments=CommentSerializer(many=True)
    class Meta:
        model=Article
        fields='__all__'
        read_only_fields=["created_at","updated_at"]


class AnnouncementBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model=AnnouncementBanner
        fields='__all__'
        ready_only_fields=["created_at","updated_at"]


class ReplyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['id','rating','address','nagarita_front','nagarita_back','certificate','phone_number','role']


class ReplyUserSerializer(serializers.ModelSerializer):
    profile=ReplyProfileSerializer()
    class Meta:
        model=CustomUser
        fields=['id','first_name','last_name','email','profile']


class ReplySerializer(serializers.ModelSerializer):
    article=ArticleSerializer()
    user=ReplyUserSerializer()
    comment=CommentSerializer()
    class Meta:
        model=Reply
        fields='__all__'
        read_only_fields=["created_at"]


class TotalLikesOnCommentSerializer(serializers.ModelSerializer):
    comment = CommentSerializer()
    class Meta:
        model = TotalLikesonComment
        fields = "__all__"
        read_only_fields = ["created_at", "likes"]


class CrouselImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model=CrouselImages
        fields='__all__'
        ready_only_fields=["created_at","updated_at"]


class CustomUserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['first_name','last_name']


class BookingsListingSerializer(serializers.ModelSerializer):
    technician = CustomUserMiniSerializer(read_only=True)
    customer = CustomUserMiniSerializer(read_only=True)
    class Meta:
        model=Booking
        fields='__all__'
        read_only_fields=["created_at","updated_at"]


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
        # Make sure the selected user is actually a technician
        if technician.role != CustomUser.Role.TECHNICIAN:
            raise serializers.ValidationError(
                "The selected user is not a technician."
            )

        return technician

    def create(self, validated_data):
        # Get the logged-in user
        customer = self.context["request"].user

        # Make sure the logged-in user is actually a customer
        if customer.role != CustomUser.Role.CUSTOMER:
            raise serializers.ValidationError(
                "Only a customer can create a booking."
            )

        # Create booking with logged-in user as customer
        booking = Booking.objects.create(
            customer=customer,
            **validated_data
        )

        return booking



# class BookingListingSerializer(serializers.ModelSerializer):
