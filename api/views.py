from rest_framework import viewsets
from .serializers import (CategorySerializer,
                          ServiceSerializer,
                          TechnicianRegisterSerializer,
                          UserSerializer,
                        ProfileServiceSerializer
                          )
from .models import Category,Service
from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView

# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing category instances.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class ServiceViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing service instances.
    """
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()


class TechnicianRegisterAPIView(CreateAPIView):
    serializer_class = TechnicianRegisterSerializer
    permission_classes = [AllowAny]
    # parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message": "Technician registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                }
            },
            status=status.HTTP_201_CREATED
        )


class UserProfileRetriveView(RetrieveAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer


class ProfileServiceAPIView(APIView):

    def post(self, request):
        serializer = ProfileServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = serializer.save()

        return Response(
            {
                "message": "Services linked to profile successfully",
                "profile_id": profile.id,
                "service_ids": [service.id for service in profile.services.all()]
            },
            status=status.HTTP_201_CREATED
        )


