from rest_framework import serializers
from .models import Category,Service,Article,Comment,AnnouncementBanner,Reply,TotalLikesonComment,CrouselImages
from django.db import transaction
from .models import Profile
from django.contrib.auth.models import User

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
    username = serializers.CharField(max_length=20, min_length=8)
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

    role=serializers.CharField(max_length=1,min_length=1)
    address = serializers.CharField(max_length=50, min_length=10)
    nagarita_front = serializers.ImageField()
    nagarita_back = serializers.ImageField()
    certificate = serializers.ImageField()
    phone_number = serializers.CharField(max_length=10, min_length=10)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
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
        # Remove fields that don't belong to User
        confirm_password = validated_data.pop("confirm_password")

        role = validated_data.pop("role")
        address = validated_data.pop("address")
        nagarita_front = validated_data.pop("nagarita_front")
        nagarita_back = validated_data.pop("nagarita_back")
        certificate = validated_data.pop("certificate")
        phone_number = validated_data.pop("phone_number")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
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


class ProfileSerializer(serializers.ModelSerializer):
    services=ServiceSerializer(many=True)
    class Meta:
        model=Profile
        fields='__all__'


class UserSerializer(serializers.ModelSerializer):
    profile=ProfileSerializer()
    class Meta:
        model=User
        fields=['first_name','last_name','username','email','profile']


class ProfileServiceSerializer(serializers.Serializer):
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all()
    )
    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        many=True
    )

    def create(self, validated_data):
        profile_id = validated_data["profile_id"]
        services = validated_data["service_ids"]


        profile_id.services.set(services)

        return profile_id


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
        model=User
        fields=['id','first_name','last_name','username','email','profile']


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