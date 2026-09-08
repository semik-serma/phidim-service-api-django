from rest_framework import viewsets,permissions
from .serializers import *
from .models import *
from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser
from rest_framework.views import APIView
from django.db.models import F
from rest_framework.exceptions import PermissionDenied

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
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                }
            },
            status=status.HTTP_201_CREATED
        )


class UserProfileRetrieveView(RetrieveAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileServiceAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProfileServiceSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        profile = serializer.save()

        return Response(
            {
                "message": "Services linked to profile successfully",
                "profile_id": profile.id,
                "service_ids": [
                    service.id
                    for service in profile.services.all()
                ]
            },
            status=status.HTTP_201_CREATED
        )


class ArticleModelViewSet(viewsets.ModelViewSet):
    queryset=Article.objects.all()
    serializer_class=ArticleSerializer


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset=Comment.objects.all()
    serializer_class=CommentSerializer


class AnnouncementBannerViewSet(viewsets.ModelViewSet):
    queryset=AnnouncementBanner.objects.all()
    serializer_class=AnnouncementBannerSerializer


class ReplyViewSet(viewsets.ModelViewSet):
    queryset=Reply.objects.all()
    serializer_class=ReplySerializer


class LikesOnCommentViewSet(viewsets.ModelViewSet):
    queryset=TotalLikesonComment.objects.all()
    serializer_class=TotalLikesOnCommentSerializer


class CrouselImagesViewSet(viewsets.ModelViewSet):
    queryset=CrouselImages.objects.all()
    serializer_class=CrouselImagesSerializer


class TechnicianListingView(APIView):
    def get(self, request, *args, **kwargs):
        print(request.GET)
        technicians = CustomUser.objects.filter(role=CustomUser.Role.TECHNICIAN)
        category_id = request.GET.get('category')
        if category_id:
            category = Category.objects.get(pk=category_id)
            technicians = technicians.filter(profile__services__category=category)

        serializer = UserSerializer(
            instance=technicians,
            many=True
        )
        return Response(serializer.data,status=status.HTTP_200_OK)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BookingsListingSerializer

        return BookingSerializer


class HomeViewCountView(APIView):

    def post(self, request):

        stats, created = SiteStats.objects.get_or_create(
            id=1,
            defaults={"view_count": 0}
        )

        SiteStats.objects.filter(
            id=stats.id
        ).update(
            view_count=F("view_count") + 1
        )

        stats.refresh_from_db()

        serializer = SiteStatsSerializer(stats)

        return Response(serializer.data)


class UserLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if latitude is None or longitude is None:
            return Response(
                {"detail": "Latitude and longitude are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        location, created = UserLocation.objects.update_or_create(
            user=request.user,
            defaults={
                "latitude": latitude,
                "longitude": longitude,
            }
        )

        serializer = UserLocationSerializer(location)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def get(self, request):
        try:
            location = UserLocation.objects.get(user=request.user)
        except UserLocation.DoesNotExist:
            return Response(
                {"detail": "Location not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserLocationSerializer(location)
        return Response(serializer.data)


class ProblemImageViewSet(viewsets.ModelViewSet):

    queryset = ProblemImage.objects.all()
    serializer_class = ProblemImageSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        return [AllowAny()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != CustomUser.Role.CUSTOMER:
            raise PermissionDenied(
                "Only customer can upload problem images."
            )

        serializer.save()


class TechnicianBookingStatusUpdate(APIView):
    permission_classes=[IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        if request.user.role != CustomUser.Role.TECHNICIAN:
            raise PermissionDenied(
                "only technicians can accept or reject "
            )
        serializer = TechnicianBookingUpdateSerializer(
            data=request.data
        )


        serializer.is_valid(raise_exception=True)

        booking = serializer.save()

        return Response({
            "message": "Booking status updated successfully.",
            "booking": booking.id,
            "status": booking.status,
        })
































































    



