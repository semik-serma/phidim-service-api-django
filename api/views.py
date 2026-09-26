# views.py
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework import viewsets,permissions
from .serializers import *
from .models import *
from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,BasePermission
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser
from rest_framework.views import APIView
from django.db.models import F
from rest_framework.exceptions import PermissionDenied
from .tasks import send_otp_for_email_verification


# Create your views here.


class IsTechnicianOrReadOnly(BasePermission):
    """
    Anyone can read categories.
    Only authenticated technicians can create, update, or delete.
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # Write operations require authentication
        if not request.user or not request.user.is_authenticated:
            return False

        # Only Technician role can modify categories
        return request.user.role == "t"


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsTechnicianOrReadOnly]


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
        send_otp_for_email_verification.delay(user.id)
        return Response(
            {
                "message": "Technician registered successfully.",
                "user": {
                    "id": user.id,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "role":user.role,
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


class UpdateHeroViewSet(viewsets.ModelViewSet):
    queryset = UpdateHero.objects.all()
    serializer_class = UpdateHeroSerializer


class OtpVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = OtpVerifySerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            request.user.is_verified = True
            request.user.save()
            print(request.user,request.user.is_verified,request.user.email)
            return Response(
                {
                    "message": "OTP verified successfully.User Account Verified"
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class EmailVerifyRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        send_otp_for_email_verification.delay(request.user.id)
        return Response(
                {
                    "message": "OTP sent successfully."
                },
                status=status.HTTP_200_OK
            )





class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        data = serializer.validated_data
        
        # Create the response
        response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        
        # Set Access Token Cookie
        response.set_cookie(
            key='access_token',
            value=data['access'],
            httponly=True,       # JavaScript cannot read it
            secure=True,         # Only sent over HTTPS (Set to False for localhost testing)
            samesite='Lax',      # Protects against CSRF
            max_age=60 * 60 * 24 # 1 day (Adjust based on your SIMPLE_JWT settings)
        )
        
        # Set Refresh Token Cookie
        response.set_cookie(
            key='refresh_token',
            value=data['refresh'],
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=60 * 60 * 24 * 7 # 7 days
        )
        
        return response



# --- 2. New Refresh View ---
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # 1. Get the refresh token from the HttpOnly cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found in cookies"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Inject the cookie token into the request data for SimpleJWT to process
        request.data['refresh'] = refresh_token
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {"detail": "Invalid or expired refresh token"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        data = serializer.validated_data
        
        # 3. Create the response and set the new Access Token cookie
        response = Response({"message": "Token refreshed successfully"}, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key='access_token',
            value=data['access'],
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=60 * 60 * 24 
        )

        # 4. If you have ROTATE_REFRESH_TOKENS = True in settings.py, 
        # SimpleJWT will return a new 'refresh' token in the data. 
        # We should update the refresh cookie as well.
        if 'refresh' in data:
            response.set_cookie(
                key='refresh_token',
                value=data['refresh'],
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=60 * 60 * 24 * 7 
            )
            
        return response


# --- 3. New Logout View ---
class LogoutView(APIView):
    def post(self, request):
        # Since HttpOnly cookies cannot be deleted by JavaScript, 
        # we must instruct the browser to delete them from the server response.
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response

class LogoutView(APIView):

    def post(self, request):

        response = Response(
            {
                "message": "Logged out successfully"
            },
            status=status.HTTP_200_OK
        )

        # Remove access token cookie
        response.delete_cookie(
            key="access_token",
            path="/"
        )

        # Remove refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            path="/"
        )

        return response














































    



