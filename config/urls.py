from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api import views
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')

router.register(r'services', views.ServiceViewSet, basename='service')

router.register(r'articles', views.ArticleModelViewSet, basename='article')

router.register(r'comments', views.CommentModelViewSet, basename='comment')

router.register(r'announcements', views.AnnouncementBannerViewSet, basename='announcement')

router.register(r'replies', views.ReplyViewSet, basename='reply')

router.register(r'likes', views.LikesOnCommentViewSet, basename='like')

router.register(r'crousel-images', views.CrouselImagesViewSet, basename='crousel-image')

router.register(r'bookings', views.BookingViewSet, basename='bookings')

router.register(r'technicians-problem-images', views.ProblemImageViewSet, basename='technicians-problem-image')


urlpatterns = [

    path('admin/', admin.site.urls),

    path(
        'swagger<format>/',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),

    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),

    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),

    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    path(
        "technicians/register/",
        views.TechnicianRegisterAPIView.as_view(),
        name="technician-register"
    ),

    path(
        "userprofile/",
        views.UserProfileRetrieveView.as_view(),
        name="user-profile-view"
    ),

    path(
        "profileservice/",
        views.ProfileServiceAPIView.as_view(),
        name="profileservice"
    ),

    path(
        "technicians/",
        views.TechnicianListingView.as_view(),
        name="technicians"
    )
    ,
    path(
        "home-views/",
        views.HomeViewCountView.as_view(),
        name="home-views"
    ),
    path(
        "technician/booking/",
        views.TechnicianBookingStatusUpdate.as_view(),
        name="technician-booking"
    )

] + router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
